"""Stoichiometry inference (offline, no per-gene hardcoding)

Computes a multiplicative amplification factor for interface-mediated DN risk
from general evidence provided in context and lightweight sequence heuristics.

Inputs (context keys are optional):
- stoichiometry: explicit integer k (1,2,3,4,6,8,...) if caller knows it
- go_terms / go_names: GO IDs or textual names, e.g., "protein homodimerization"
- pdb_assemblies: list of observed biological assembly sizes (ints) for this protein or close homologs
- interpro_ids / pfam_ids: IDs only; no baked-in mapping here
- tm_segments or tm_count: transmembrane segment annotations (numbers or spans)
- sequence_motifs: optionally precomputed motif hits

Returns: (amp: float, amp_feats: List[dict], note: str)
- amp is a multiplicative factor applied to interface poisoning score
- amp_feats is a small feature list describing the evidence used
- note is a short string summary

Design choices:
- No per-gene or per-accession tables. Only algorithmic rules and caller-provided
  evidence. If nothing is known, return neutral amp=1.0.
- If explicit k is provided, use a fixed poison ratio mapping. This is algorithmic,
  not a gene table.
"""
from __future__ import annotations
from typing import Dict, List, Tuple
import re

# Poison ratio mapping (algorithmic, not per-gene)
_POISON_MAP = {
    1: 0.8,   # mild dampening if explicitly monomeric (conservative by default)
    2: 2.0,
    3: 3.5,
    4: 6.0,
    6: 12.0,
    8: 20.0,
}

_HEPTAD_RE = re.compile(r"L.{6}L.{6}L")  # crude leucine zipper signal


def _cap(x: float, lo: float = 0.0, hi: float = 1e9) -> float:
    return max(lo, min(hi, float(x)))


def _mix_expectation(weights: Dict[int, float]) -> Tuple[float, Dict[int, float]]:
    # Normalize weights to probabilities; compute expected poison factor
    total = sum(max(0.0, w) for w in weights.values())
    if total <= 0:
        return 1.0, {}
    probs = {k: (max(0.0, w) / total) for k, w in weights.items() if k in _POISON_MAP}
    amp = 0.0
    for k, p in probs.items():
        amp += p * _POISON_MAP[k]
    return _cap(amp, 0.0, 32.0), probs


def _go_term_votes(ctx: Dict) -> Dict[int, float]:
    votes: Dict[int, float] = {}
    texts: List[str] = []
    for key in ("go_names", "go_terms", "go_texts"):
        xs = ctx.get(key)
        if isinstance(xs, str):
            texts.append(xs.lower())
        elif isinstance(xs, list):
            texts.extend(str(x).lower() for x in xs)
    if not texts:
        return votes
    def add(k: int, w: float):
        votes[k] = votes.get(k, 0.0) + w
    for t in texts:
        if "homodimer" in t or "heterodimer" in t or "dimerization" in t:
            add(2, 1.5)
        if "trimer" in t:
            add(3, 1.5)
        if "tetramer" in t:
            add(4, 1.5)
        if "hexamer" in t or "6-mer" in t:
            add(6, 1.5)
        if "oligomer" in t or "oligomerization" in t:
            for k in (2, 3, 4):
                add(k, 0.5)
        if "monomer" in t or "monomeric" in t:
            votes[1] = votes.get(1, 0.0) + 1.0
    return votes


def _pdb_votes(ctx: Dict) -> Dict[int, float]:
    votes: Dict[int, float] = {}
    assemblies = ctx.get("pdb_assemblies")
    if not assemblies:
        return votes
    # Each observed assembly contributes proportional weight
    for a in assemblies:
        try:
            a = int(a)
        except Exception:
            continue
        votes[a] = votes.get(a, 0.0) + 2.0
    return votes


def _sequence_votes(seq: str, ctx: Dict) -> Dict[int, float]:
    votes: Dict[int, float] = {}
    s = seq.upper()
    # Leucine zipper heuristic (supports dimers/trimers)
    if _HEPTAD_RE.search(s):
        votes[2] = votes.get(2, 0.0) + 1.0
        votes[3] = votes.get(3, 0.0) + 0.5
    # Coiled-coil rough flag near variant position if provided
    # Caller may have set ctx["coiled_coil_near"]
    if ctx.get("coiled_coil_near"):
        votes[2] = votes.get(2, 0.0) + 0.5
        votes[3] = votes.get(3, 0.0) + 0.5
    # Transmembrane architecture hints
    tm_count = None
    if isinstance(ctx.get("tm_count"), int):
        tm_count = ctx.get("tm_count")
    elif isinstance(ctx.get("tm_segments"), list):
        tm_count = len(ctx.get("tm_segments"))
    if tm_count is not None:
        # Very crude: channels often oligomerize; carriers often act as monomers
        if tm_count >= 10:
            votes[4] = votes.get(4, 0.0) + 0.5
        elif tm_count >= 6:
            votes[2] = votes.get(2, 0.0) + 0.3
    return votes


def compute_interface_amp(seq: str, ctx: Dict | None) -> Tuple[float, List[Dict], str]:
    """Compute amplification for interface poisoning from context + sequence.

    Logic order:
    1) If explicit ctx["stoichiometry"] provided, use mapping directly.
    2) Else, combine evidence votes from GO, PDB, and sequence heuristics and
       return expectation over k.
    3) If nothing is known, return neutral amp=1.0.
    """
    ctx = ctx or {}
    feats: List[Dict] = []

    # 1) Explicit k
    k_raw = ctx.get("stoichiometry")
    try:
        k = int(float(k_raw)) if k_raw is not None else None
    except Exception:
        k = None
    if k is not None and k in _POISON_MAP:
        amp = float(ctx.get("_stoich_amp_override", _POISON_MAP[k]))
        if k == 1:
            # Allow caller to override the mild dampening if desired
            amp = float(ctx.get("_mono_damp", amp))
        feats.append({"feature": f"stoichiometry_{k}x", "value": amp, "weight": abs(amp)})
        return _cap(amp, 0.0, 32.0), feats, f"explicit k={k}"

    # 2) Evidence fusion
    votes: Dict[int, float] = {}
    for part in (_go_term_votes(ctx), _pdb_votes(ctx), _sequence_votes(seq, ctx)):
        for kk, ww in part.items():
            votes[kk] = votes.get(kk, 0.0) + ww
    amp, probs = _mix_expectation(votes)

    # Optional monomeric evidence dampening (light)
    monomeric_hint = (votes.get(1, 0.0) > 0)
    if monomeric_hint and amp >= 1.0:
        amp *= float(ctx.get("_mono_damp", 0.9))  # light dampening only when hinted

    # Build feature explanations
    for kk, ww in sorted(votes.items(), key=lambda kv: -kv[1])[:3]:
        feats.append({"feature": f"vote_k={kk}", "value": ww, "weight": ww})
    note = (
        f"evidence mix: " + ", ".join(f"k{kk}:{probs.get(kk,0):.2f}" for kk in sorted(probs))
        if probs else "no_evidence"
    )
    return _cap(amp, 0.0, 32.0), feats, note


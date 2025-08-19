#!/usr/bin/env python3
"""
🔬 DOMINANT NEGATIVE ANALYZER - BIN 2 ANALYSIS
Built by Ace for the revolutionary two-bin approach

This tiny module analyzes whether variants cause dominant negative effects.
Revolutionary interference prediction - does it poison protein complexes?
"""

from typing import Dict, Any
import re

class DNAnalyzer:
    """Analyze dominant negative potential - Bin 2 of our two-bin approach"""
    
    def __init__(self, offline_mode=False):
        self.name = "DNAnalyzer"
        self.offline_mode = offline_mode
        
        # Protein family patterns for DN mechanisms
        self.dn_patterns = {
            'oligomeric_proteins': {
                'patterns': [r'tetramer', r'dimer', r'complex', r'subunit'],
                'mechanism': 'complex_poisoning',
                'weight': 0.8
            },
            'motor_proteins': {
                'patterns': [r'myosin', r'kinesin', r'dynein', r'motor'],
                'mechanism': 'motor_complex_disruption',
                'weight': 0.7
            },
            'transcription_factors': {
                'patterns': [r'DNA.binding', r'transcription', r'zinc.finger'],
                'mechanism': 'competitive_dna_binding',
                'weight': 0.6
            },
            'structural_proteins': {
                'patterns': [r'collagen', r'keratin', r'actin', r'tubulin'],
                'mechanism': 'filament_poisoning',
                'weight': 0.9
            }
        }
        
        # Known DN hotspot mutations
        self.known_dn_mutations = {
            'R175H': 0.9,  # TP53 classic DN
            'R248W': 0.9,  # TP53 classic DN
            'R273H': 0.9,  # TP53 classic DN
            'R282W': 0.8,  # TP53 DN
            'G349S': 0.8,  # Collagen DN pattern
            'G415S': 0.8,  # Collagen DN pattern
        }
    
    def analyze_dn(self, mutation: str, sequence: str, uniprot_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Analyze dominant negative potential
        
        Args:
            mutation: Mutation string (e.g., "R175H")
            sequence: Protein sequence
            uniprot_id: UniProt ID for additional context
            
        Returns:
            DN analysis results
        """
        
        parsed = self._parse_mutation(mutation)
        if not parsed:
            return self._empty_result()
        
        original_aa = parsed['original_aa']
        new_aa = parsed['new_aa']
        position = parsed['position']
        
        # Analyze different DN mechanisms
        complex_poisoning = self._assess_complex_poisoning(mutation, sequence, uniprot_id)
        competitive_binding = self._assess_competitive_binding(original_aa, new_aa, position, sequence)
        interference_potential = self._assess_interference_potential(mutation, sequence)
        known_dn_score = self._check_known_dn_patterns(mutation)
        
        # Calculate overall DN score
        dn_score = self._calculate_dn_score(
            complex_poisoning, competitive_binding, interference_potential, known_dn_score
        )
        
        return {
            'dn_score': dn_score,
            'complex_poisoning': complex_poisoning,
            'competitive_binding': competitive_binding,
            'interference_potential': interference_potential,
            'known_dn_score': known_dn_score,
            'mechanism': self._determine_dn_mechanism(complex_poisoning, competitive_binding, interference_potential),
            'confidence': self._calculate_dn_confidence(mutation, sequence, uniprot_id)
        }
    
    def _parse_mutation(self, mutation: str) -> Dict[str, Any]:
        """Parse mutation string"""
        if not mutation or len(mutation) < 3:
            return None
            
        return {
            'original_aa': mutation[0],
            'position': int(mutation[1:-1]),
            'new_aa': mutation[-1],
            'mutation': mutation
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Empty result for failed parsing"""
        return {
            'dn_score': 0.0,
            'complex_poisoning': 0.0,
            'competitive_binding': 0.0,
            'interference_potential': 0.0,
            'known_dn_score': 0.0,
            'mechanism': 'unknown',
            'confidence': 0.0
        }
    
    def _assess_complex_poisoning(self, mutation: str, sequence: str, uniprot_id: str) -> float:
        """Assess potential for protein complex poisoning"""
        score = 0.0
        
        # Check for oligomeric protein patterns
        sequence_lower = sequence.lower() if sequence else ""
        
        # Collagen-specific patterns (Gly-X-Y repeats)
        if re.search(r'G.{2}G.{2}G', sequence):
            if mutation[0] == 'G':  # Glycine loss in collagen
                score += 0.8
        
        # Look for repeated motifs (suggests oligomeric structure)
        if len(sequence) > 100:
            # Simple repeat detection
            for i in range(10, 30):  # Check for repeats of length 10-30
                pattern = sequence[:i]
                if sequence.count(pattern) > 3:  # Found repeated motif
                    score += 0.3
                    break
        
        # UniProt ID-based classification (simplified)
        if uniprot_id:
            # Known oligomeric proteins (simplified list)
            oligomeric_proteins = ['P04637', 'P25705', 'Q92734']  # TP53, ATP5F1A, TFG
            if uniprot_id in oligomeric_proteins:
                score += 0.4
        
        return min(score, 1.0)
    
    def _assess_competitive_binding(self, original_aa: str, new_aa: str, position: int, sequence: str) -> float:
        """Assess competitive binding potential"""
        score = 0.0
        
        # Charge changes often affect binding specificity
        aa_charges = {'R': 1, 'K': 1, 'H': 0.5, 'D': -1, 'E': -1}
        orig_charge = aa_charges.get(original_aa, 0)
        new_charge = aa_charges.get(new_aa, 0)
        
        charge_change = abs(new_charge - orig_charge)
        if charge_change > 0.5:
            score += 0.4
        
        # Size changes in binding regions
        aa_sizes = {'G': 1, 'A': 2, 'S': 2, 'C': 2, 'T': 3, 'P': 3, 'V': 3, 'N': 3, 'D': 3,
                   'Q': 4, 'E': 4, 'I': 4, 'L': 4, 'M': 4, 'K': 4, 'H': 4, 'F': 5, 'R': 5, 'Y': 5, 'W': 6}
        
        orig_size = aa_sizes.get(original_aa, 3)
        new_size = aa_sizes.get(new_aa, 3)
        
        size_change = abs(new_size - orig_size)
        if size_change > 2:
            score += 0.3
        
        # Position-based scoring (N-terminal and C-terminal regions often important for binding)
        seq_length = len(sequence) if sequence else 100
        if position < seq_length * 0.2 or position > seq_length * 0.8:  # Terminal regions
            score *= 1.2
        
        return min(score, 1.0)
    
    def _assess_interference_potential(self, mutation: str, sequence: str) -> float:
        """Assess general interference potential"""
        score = 0.0
        
        original_aa = mutation[0]
        new_aa = mutation[-1]
        
        # Specific amino acid changes known to cause interference
        interference_patterns = {
            ('R', 'H'): 0.6,  # Common in TP53 DN mutations
            ('R', 'W'): 0.7,  # Charge to bulky hydrophobic
            ('G', 'S'): 0.5,  # Flexibility loss
            ('G', 'R'): 0.8,  # Flexibility to charge
            ('I', 'R'): 0.6,  # Hydrophobic to charged (like ATP5F1A)
            ('H', 'Y'): 0.4,  # Aromatic change (like MYO7A)
        }
        
        pattern_score = interference_patterns.get((original_aa, new_aa), 0.0)
        score += pattern_score
        
        # Proline introduction (often disruptive)
        if new_aa == 'P':
            score += 0.3
        
        # Cysteine changes (disulfide bond disruption)
        if original_aa == 'C' or new_aa == 'C':
            score += 0.4
        
        return min(score, 1.0)
    
    def _check_known_dn_patterns(self, mutation: str) -> float:
        """Check against known DN mutations"""
        return self.known_dn_mutations.get(mutation, 0.0)
    
    def _calculate_dn_score(self, complex_poisoning: float, competitive_binding: float, 
                           interference_potential: float, known_dn_score: float) -> float:
        """Calculate overall DN score"""
        # Weighted combination with emphasis on known patterns
        score = (
            complex_poisoning * 0.3 +
            competitive_binding * 0.2 +
            interference_potential * 0.3 +
            known_dn_score * 0.2
        )
        
        return min(score, 1.0)
    
    def _determine_dn_mechanism(self, complex_poisoning: float, competitive_binding: float, 
                               interference_potential: float) -> str:
        """Determine primary DN mechanism"""
        if complex_poisoning > 0.5:
            return 'complex_poisoning'
        elif competitive_binding > 0.5:
            return 'competitive_binding'
        elif interference_potential > 0.5:
            return 'general_interference'
        else:
            return 'low_dn_potential'
    
    def _calculate_dn_confidence(self, mutation: str, sequence: str, uniprot_id: str) -> float:
        """Calculate confidence in DN prediction"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for known DN patterns
        if mutation in self.known_dn_mutations:
            confidence += 0.3
        
        # Higher confidence for oligomeric proteins
        if sequence and re.search(r'G.{2}G.{2}G', sequence):  # Collagen-like
            confidence += 0.2
        
        # Known protein families
        if uniprot_id in ['P04637', 'P25705', 'Q92734']:  # TP53, ATP5F1A, TFG
            confidence += 0.1
        
        return min(confidence, 0.9)

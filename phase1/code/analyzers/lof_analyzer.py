#!/usr/bin/env python3
"""
🔬 LOSS OF FUNCTION ANALYZER - BIN 1 ANALYSIS
Built by Ace for the revolutionary two-bin approach

This tiny module analyzes whether variants cause loss of function.
Traditional pathogenicity prediction - does it break the protein?
"""

from typing import Dict, Any
import re
from .smart_protein_analyzer import SmartProteinAnalyzer

class LOFAnalyzer:
    """Analyze loss of function potential - Bin 1 of our two-bin approach"""
    
    def __init__(self):
        self.name = "LOFAnalyzer"
        self.smart_analyzer = SmartProteinAnalyzer()
        
        # Amino acid stability/conservation properties
        self.aa_properties = {
            'G': {'size': 1, 'charge': 0, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'critical'},
            'A': {'size': 2, 'charge': 0, 'hydrophobic': True, 'flexibility': 'medium', 'conservation': 'medium'},
            'V': {'size': 3, 'charge': 0, 'hydrophobic': True, 'flexibility': 'low', 'conservation': 'medium'},
            'L': {'size': 4, 'charge': 0, 'hydrophobic': True, 'flexibility': 'low', 'conservation': 'medium'},
            'I': {'size': 4, 'charge': 0, 'hydrophobic': True, 'flexibility': 'low', 'conservation': 'medium'},
            'M': {'size': 4, 'charge': 0, 'hydrophobic': True, 'flexibility': 'medium', 'conservation': 'medium'},
            'F': {'size': 5, 'charge': 0, 'hydrophobic': True, 'flexibility': 'low', 'conservation': 'high'},
            'W': {'size': 6, 'charge': 0, 'hydrophobic': True, 'flexibility': 'low', 'conservation': 'high'},
            'P': {'size': 3, 'charge': 0, 'hydrophobic': False, 'flexibility': 'rigid', 'conservation': 'critical'},
            'S': {'size': 2, 'charge': 0, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'low'},
            'T': {'size': 3, 'charge': 0, 'hydrophobic': False, 'flexibility': 'medium', 'conservation': 'low'},
            'C': {'size': 2, 'charge': 0, 'hydrophobic': False, 'flexibility': 'medium', 'conservation': 'critical'},
            'Y': {'size': 5, 'charge': 0, 'hydrophobic': False, 'flexibility': 'medium', 'conservation': 'high'},
            'N': {'size': 3, 'charge': 0, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'medium'},
            'Q': {'size': 4, 'charge': 0, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'medium'},
            'D': {'size': 3, 'charge': -1, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'high'},
            'E': {'size': 4, 'charge': -1, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'high'},
            'K': {'size': 4, 'charge': 1, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'high'},
            'R': {'size': 5, 'charge': 1, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'high'},
            'H': {'size': 4, 'charge': 0.5, 'hydrophobic': False, 'flexibility': 'high', 'conservation': 'high'}
        }
    
    def analyze_lof(self, mutation: str, sequence: str, uniprot_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Analyze loss of function potential
        
        Args:
            mutation: Mutation string (e.g., "R175H")
            sequence: Protein sequence
            
        Returns:
            LOF analysis results
        """
        
        parsed = self._parse_mutation(mutation)
        if not parsed:
            return self._empty_result()
        
        original_aa = parsed['original_aa']
        new_aa = parsed['new_aa']
        position = parsed['position']
        
        # Get amino acid properties
        orig_props = self.aa_properties.get(original_aa, self._default_props())
        new_props = self.aa_properties.get(new_aa, self._default_props())
        
        # Analyze different LOF mechanisms
        stability_impact = self._assess_stability_impact(orig_props, new_props)
        conservation_impact = self._assess_conservation_impact(orig_props, new_props)
        structural_impact = self._assess_structural_impact(orig_props, new_props, position, len(sequence))
        functional_impact = self._assess_functional_impact(mutation, sequence)
        
        # Get smart protein context multiplier
        smart_multiplier, smart_confidence = 1.0, 0.0
        if uniprot_id and sequence:
            smart_multiplier, smart_confidence = self.smart_analyzer.get_protein_context_multiplier(
                uniprot_id, sequence, position
            )

        # Calculate overall LOF score with smart multiplier
        base_lof_score = self._calculate_lof_score(
            stability_impact, conservation_impact, structural_impact, functional_impact
        )
        lof_score = min(base_lof_score * smart_multiplier, 1.0)
        
        return {
            'lof_score': lof_score,
            'base_lof_score': base_lof_score,
            'smart_multiplier': smart_multiplier,
            'stability_impact': stability_impact,
            'conservation_impact': conservation_impact,
            'structural_impact': structural_impact,
            'functional_impact': functional_impact,
            'mechanism': self._determine_lof_mechanism(stability_impact, conservation_impact, structural_impact),
            'confidence': min(self._calculate_lof_confidence(orig_props, new_props, mutation) + smart_confidence, 0.9)
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
    
    def _default_props(self) -> Dict[str, Any]:
        """Default amino acid properties"""
        return {'size': 3, 'charge': 0, 'hydrophobic': False, 'flexibility': 'medium', 'conservation': 'medium'}
    
    def _empty_result(self) -> Dict[str, Any]:
        """Empty result for failed parsing"""
        return {
            'lof_score': 0.0,
            'stability_impact': 0.0,
            'conservation_impact': 0.0,
            'structural_impact': 0.0,
            'functional_impact': 0.0,
            'mechanism': 'unknown',
            'confidence': 0.0
        }
    
    def _assess_stability_impact(self, orig_props: Dict, new_props: Dict) -> float:
        """Assess impact on protein stability"""
        score = 0.0
        
        # Size changes affect stability
        size_change = abs(new_props['size'] - orig_props['size'])
        if size_change > 2:
            score += 0.3
        elif size_change > 1:
            score += 0.1
        
        # Charge changes affect stability
        charge_change = abs(new_props['charge'] - orig_props['charge'])
        if charge_change > 1:
            score += 0.4
        elif charge_change > 0.5:
            score += 0.2
        
        # Hydrophobicity changes
        if orig_props['hydrophobic'] != new_props['hydrophobic']:
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_conservation_impact(self, orig_props: Dict, new_props: Dict) -> float:
        """Assess impact based on amino acid conservation"""
        conservation_scores = {'critical': 1.0, 'high': 0.8, 'medium': 0.5, 'low': 0.2}
        
        orig_conservation = conservation_scores.get(orig_props['conservation'], 0.5)
        
        # Higher impact if we're changing a highly conserved residue
        return orig_conservation
    
    def _assess_structural_impact(self, orig_props: Dict, new_props: Dict, position: int, seq_length: int) -> float:
        """Assess structural impact"""
        score = 0.0
        
        # Flexibility changes
        flexibility_map = {'rigid': 0, 'low': 1, 'medium': 2, 'high': 3}
        orig_flex = flexibility_map.get(orig_props['flexibility'], 2)
        new_flex = flexibility_map.get(new_props['flexibility'], 2)
        
        flex_change = abs(new_flex - orig_flex)
        if flex_change > 2:
            score += 0.3
        elif flex_change > 1:
            score += 0.1
        
        # Position-based impact (middle regions often more critical)
        position_factor = 1.0 - abs(position - seq_length/2) / (seq_length/2)
        score *= (0.5 + 0.5 * position_factor)
        
        return min(score, 1.0)
    
    def _assess_functional_impact(self, mutation: str, sequence: str) -> float:
        """Assess functional impact based on known patterns"""
        score = 0.0
        
        # Known highly disruptive changes
        if mutation[0] == 'C':  # Cysteine loss (disulfide bonds)
            score += 0.5
        if mutation[0] == 'P':  # Proline loss (structural rigidity)
            score += 0.3
        if mutation[0] == 'G':  # Glycine loss (flexibility)
            score += 0.4
        
        return min(score, 1.0)
    
    def _calculate_lof_score(self, stability: float, conservation: float, structural: float, functional: float) -> float:
        """Calculate overall LOF score"""
        # Weighted combination
        score = (
            stability * 0.3 +
            conservation * 0.3 +
            structural * 0.2 +
            functional * 0.2
        )
        
        return min(score, 1.0)
    
    def _determine_lof_mechanism(self, stability: float, conservation: float, structural: float) -> str:
        """Determine primary LOF mechanism"""
        if stability > 0.5:
            return 'protein_instability'
        elif conservation > 0.7:
            return 'critical_residue_loss'
        elif structural > 0.5:
            return 'structural_disruption'
        else:
            return 'mild_functional_impact'
    
    def _calculate_lof_confidence(self, orig_props: Dict, new_props: Dict, mutation: str) -> float:
        """Calculate confidence in LOF prediction"""
        confidence = 0.6  # Base confidence
        
        # Higher confidence for well-understood changes
        if orig_props['conservation'] in ['critical', 'high']:
            confidence += 0.2
        
        # Known disruptive patterns
        if mutation[0] in ['C', 'P', 'G']:
            confidence += 0.1
        
        return min(confidence, 0.9)

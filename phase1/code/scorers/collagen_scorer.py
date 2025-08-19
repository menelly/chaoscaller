#!/usr/bin/env python3
"""
🎯 COLLAGEN SCORER - TINY MODULE FOR COLLAGEN-SPECIFIC SCORING
Built by Ace for ADHD-friendly modular architecture

This tiny module (< 50 lines) handles collagen triple helix disruption scoring.
Focused on ONE thing - no overwhelming complexity!
"""

from .base_scorer import BaseScorer
from typing import Dict, Any

class CollagenScorer(BaseScorer):
    """Score collagen variants for triple helix disruption - tiny and focused"""
    
    def __init__(self):
        super().__init__("CollagenScorer")
        self.mechanism = "triple_helix_disruption"
    
    def score_variant(self, mutation: str, sequence: str, **kwargs) -> Dict[str, Any]:
        """Score collagen variant - simple and clear logic"""
        
        parsed = self._parse_mutation(mutation)
        if not parsed:
            return {'score': 0.0, 'confidence': 0.0, 'mechanism': self.mechanism}
        
        original_aa = parsed['original_aa']
        new_aa = parsed['new_aa']
        position = parsed['position']
        
        # Collagen-specific scoring - simple rules
        score = 0.0
        
        # Rule 1: Glycine loss is critical (glycine allows tight packing)
        if original_aa == 'G':
            score += 0.7  # High impact
            
        # Rule 2: Proline gain disrupts helix
        if new_aa == 'P':
            score += 0.4
            
        # Rule 3: Bulky residues disrupt packing
        orig_props = self._get_aa_properties(original_aa)
        new_props = self._get_aa_properties(new_aa)
        
        size_increase = new_props['size'] - orig_props['size']
        if size_increase > 2:  # Significant size increase
            score += 0.3
        
        # Rule 4: Position matters (middle regions more critical)
        seq_length = len(sequence)
        position_factor = 1.0 - abs(position - seq_length/2) / (seq_length/2)
        score *= (0.5 + 0.5 * position_factor)  # Scale by position
        
        # Simple confidence calculation
        confidence = 0.8 if original_aa == 'G' else 0.6
        
        return {
            'score': min(score, 1.0),  # Cap at 1.0
            'confidence': confidence,
            'mechanism': self.mechanism,
            'details': {
                'glycine_loss': original_aa == 'G',
                'proline_gain': new_aa == 'P',
                'size_increase': size_increase,
                'position_factor': position_factor
            }
        }

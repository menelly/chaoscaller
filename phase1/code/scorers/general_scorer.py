#!/usr/bin/env python3
"""
🎯 GENERAL SCORER - TINY MODULE FOR GENERAL VARIANT SCORING
Built by Ace for ADHD-friendly modular architecture

This tiny module (< 50 lines) handles general dominant negative scoring.
Simple fallback when we don't know the specific mechanism!
"""

from .base_scorer import BaseScorer
from typing import Dict, Any

class GeneralScorer(BaseScorer):
    """General variant scorer - tiny fallback module"""
    
    def __init__(self):
        super().__init__("GeneralScorer")
        self.mechanism = "general_interference"
    
    def score_variant(self, mutation: str, sequence: str, **kwargs) -> Dict[str, Any]:
        """Score variant using general rules - simple and clear"""
        
        parsed = self._parse_mutation(mutation)
        if not parsed:
            return {'score': 0.0, 'confidence': 0.0, 'mechanism': self.mechanism}
        
        original_aa = parsed['original_aa']
        new_aa = parsed['new_aa']
        position = parsed['position']
        
        # General scoring rules - simple and focused
        score = 0.0
        
        # Rule 1: Charge changes often disrupt interactions
        orig_props = self._get_aa_properties(original_aa)
        new_props = self._get_aa_properties(new_aa)
        
        charge_change = abs(new_props['charge'] - orig_props['charge'])
        if charge_change > 0.5:
            score += 0.3
        
        # Rule 2: Size changes can disrupt structure
        size_change = abs(new_props['size'] - orig_props['size'])
        if size_change > 2:
            score += 0.2
        
        # Rule 3: Known hotspot mutations (TP53 examples)
        if mutation in ['R175H', 'R248W', 'R273H', 'R282W']:
            score += 0.4  # Literature-supported dominant negatives
        
        # Rule 4: Position-based scoring (middle regions more critical)
        seq_length = len(sequence)
        if seq_length > 0:
            position_factor = 1.0 - abs(position - seq_length/2) / (seq_length/2)
            score *= (0.7 + 0.3 * position_factor)
        
        # Simple confidence calculation
        confidence = 0.7 if mutation in ['R175H', 'R248W', 'R273H', 'R282W'] else 0.5
        
        return {
            'score': min(score, 1.0),  # Cap at 1.0
            'confidence': confidence,
            'mechanism': self.mechanism,
            'details': {
                'charge_change': charge_change,
                'size_change': size_change,
                'known_hotspot': mutation in ['R175H', 'R248W', 'R273H', 'R282W'],
                'position_factor': position_factor if seq_length > 0 else 1.0
            }
        }

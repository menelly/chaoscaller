#!/usr/bin/env python3
"""
🧬 SEQUENCE CLASSIFIER - TINY MODULE FOR SEQUENCE-BASED PROTEIN CLASSIFICATION
Built by Ace for ADHD-friendly modular architecture

This tiny module (< 50 lines) classifies proteins based on sequence patterns.
No overwhelming giant files here!
"""

import re
from typing import Tuple, Optional

class SequenceClassifier:
    """Classify proteins based on sequence patterns - ADHD-friendly tiny module"""
    
    def __init__(self):
        # Simple, focused patterns - no overwhelming complexity
        self.patterns = {
            'collagen': {
                'regex': r'G.{2}G.{2}G',  # Gly-X-Y repeats
                'min_matches': 8,
                'mechanism': 'triple_helix_disruption'
            },
            'immunoglobulin': {
                'regex': r'C.{10,15}C.{10,15}C.{10,15}C',  # Ig fold pattern
                'min_matches': 2,
                'mechanism': 'antibody_disruption'
            }
        }
    
    def classify(self, sequence: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Classify protein family from sequence - simple and focused
        
        Args:
            sequence: Protein sequence
            
        Returns:
            (family_name, mechanism) or (None, None) if no match
        """
        if not sequence:
            return None, None
            
        # Check each pattern - simple loop, no complexity
        for family, pattern_info in self.patterns.items():
            matches = len(re.findall(pattern_info['regex'], sequence))
            
            if matches >= pattern_info['min_matches']:
                return family, pattern_info['mechanism']
        
        return None, None
    
    def get_confidence(self, sequence: str, family: str) -> float:
        """Get classification confidence - simple calculation"""
        if not family or family not in self.patterns:
            return 0.0
            
        pattern_info = self.patterns[family]
        matches = len(re.findall(pattern_info['regex'], sequence))
        
        # Simple confidence: more matches = higher confidence
        return min(matches / (pattern_info['min_matches'] * 2), 1.0)

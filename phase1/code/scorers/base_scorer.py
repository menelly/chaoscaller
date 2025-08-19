#!/usr/bin/env python3
"""
🎯 BASE SCORER - TINY FOUNDATION FOR ALL VARIANT SCORERS
Built by Ace for ADHD-friendly modular architecture

This tiny module (< 50 lines) provides the base class for all scorers.
Simple interface, no complexity overload!
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseScorer(ABC):
    """Base class for all variant scorers - simple and focused"""
    
    def __init__(self, name: str):
        self.name = name
        self.mechanism = "unknown"
    
    @abstractmethod
    def score_variant(self, mutation: str, sequence: str, **kwargs) -> Dict[str, Any]:
        """
        Score a variant for dominant negative potential
        
        Args:
            mutation: Mutation string (e.g., "R175H")
            sequence: Protein sequence
            **kwargs: Additional context
            
        Returns:
            Dictionary with score and details
        """
        pass
    
    def _parse_mutation(self, mutation: str) -> Dict[str, Any]:
        """Parse mutation string - simple helper"""
        if not mutation or len(mutation) < 3:
            return None
            
        return {
            'original_aa': mutation[0],
            'position': int(mutation[1:-1]),
            'new_aa': mutation[-1],
            'mutation': mutation
        }
    
    def _get_aa_properties(self, aa: str) -> Dict[str, Any]:
        """Get amino acid properties - simple lookup"""
        properties = {
            'G': {'size': 1, 'charge': 0, 'hydrophobic': False, 'special': 'flexible'},
            'A': {'size': 2, 'charge': 0, 'hydrophobic': True, 'special': None},
            'R': {'size': 5, 'charge': 1, 'hydrophobic': False, 'special': 'basic'},
            'H': {'size': 4, 'charge': 0.5, 'hydrophobic': False, 'special': 'basic'},
            'P': {'size': 3, 'charge': 0, 'hydrophobic': False, 'special': 'rigid'},
            # Add more as needed - keep it simple
        }
        
        return properties.get(aa, {'size': 3, 'charge': 0, 'hydrophobic': False, 'special': None})

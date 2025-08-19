#!/usr/bin/env python3
"""
🧬 EXPRESSION CLASSIFIER - TINY MODULE FOR TISSUE EXPRESSION CLASSIFICATION
Built by Ace for ADHD-friendly modular architecture

This tiny module (< 50 lines) classifies proteins based on tissue expression.
Simple, focused, no brain overload!
"""

from typing import Dict, Tuple, Optional

class ExpressionClassifier:
    """Classify proteins based on tissue expression - bite-sized and focused"""
    
    def __init__(self):
        # Simple tissue -> mechanism mapping
        self.tissue_mechanisms = {
            'brain': 'neurodevelopmental_disruption',
            'muscle': 'contractile_disruption',
            'bone': 'structural_matrix_disruption', 
            'skin': 'structural_matrix_disruption',
            'heart': 'contractile_disruption',
            'liver': 'metabolic_disruption',
            'ubiquitous': 'general_cellular_disruption'
        }
    
    def classify(self, expression_data: Dict[str, float]) -> Tuple[Optional[str], Optional[str]]:
        """
        Classify based on expression pattern - simple and clear
        
        Args:
            expression_data: {tissue: expression_level}
            
        Returns:
            (tissue_type, mechanism) or (None, None)
        """
        if not expression_data:
            return None, None
        
        # Find highest expressing tissue - simple max
        max_tissue = max(expression_data, key=expression_data.get)
        max_expression = expression_data[max_tissue]
        
        # Check if ubiquitous (expressed everywhere)
        avg_expression = sum(expression_data.values()) / len(expression_data)
        if max_expression < avg_expression * 2:  # Not much higher than average
            tissue_type = 'ubiquitous'
        else:
            tissue_type = max_tissue
        
        mechanism = self.tissue_mechanisms.get(tissue_type, 'general_cellular_disruption')
        return tissue_type, mechanism
    
    def get_confidence(self, expression_data: Dict[str, float]) -> float:
        """Simple confidence calculation"""
        if not expression_data:
            return 0.0
        
        values = list(expression_data.values())
        max_val = max(values)
        avg_val = sum(values) / len(values)
        
        # Higher confidence if expression is clearly tissue-specific
        return min((max_val - avg_val) / max_val, 1.0) if max_val > 0 else 0.0

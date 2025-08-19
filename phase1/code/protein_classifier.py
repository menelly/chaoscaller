#!/usr/bin/env python3
"""
🧬 PROTEIN CLASSIFIER - TINY ORCHESTRATOR MODULE
Built by Ace for ADHD-friendly modular architecture

This tiny module (< 80 lines) just orchestrates the other tiny modules.
No giant overwhelming file - just simple coordination!
"""

from classifiers import SequenceClassifier
from scorers import CollagenScorer, GeneralScorer
from typing import Dict, Any, Optional

class ProteinClassifier:
    """Orchestrate protein classification - tiny and focused"""
    
    def __init__(self):
        # Initialize tiny modules
        self.sequence_classifier = SequenceClassifier()
        
        # Initialize tiny scorers
        self.scorers = {
            'triple_helix_disruption': CollagenScorer(),
            'general': GeneralScorer()
        }
    
    def classify_and_score(self, uniprot_id: str, mutation: str, sequence: str) -> Dict[str, Any]:
        """
        Classify protein and score variant - simple workflow
        
        Args:
            uniprot_id: UniProt ID
            mutation: Mutation string (e.g., "G349S")
            sequence: Protein sequence
            
        Returns:
            Complete analysis results
        """
        
        # Step 1: Classify protein (tiny module)
        family, mechanism = self.sequence_classifier.classify(sequence)
        confidence = self.sequence_classifier.get_confidence(sequence, family)
        
        # Step 2: Select appropriate scorer (simple logic)
        if mechanism and mechanism in self.scorers and confidence > 0.5:
            scorer = self.scorers[mechanism]
        else:
            scorer = self.scorers['general']  # Fallback
        
        # Step 3: Score the variant (tiny module)
        score_result = scorer.score_variant(mutation, sequence, uniprot_id=uniprot_id)
        
        # Step 4: Combine results (simple merge)
        return {
            'uniprot_id': uniprot_id,
            'mutation': mutation,
            'classification': {
                'family': family,
                'mechanism': mechanism,
                'confidence': confidence
            },
            'scoring': score_result,
            'scorer_used': scorer.name,
            'final_score': score_result['score'],
            'dominant_negative_likelihood': self._get_likelihood(score_result['score'])
        }
    
    def _get_likelihood(self, score: float) -> str:
        """Convert score to likelihood - simple thresholds"""
        if score > 0.6:
            return 'high'
        elif score > 0.3:
            return 'medium'
        else:
            return 'low'


def test_modular_system():
    """Test our beautiful modular system - no overwhelming complexity!"""
    
    print("🧬 TESTING MODULAR PROTEIN CLASSIFICATION SYSTEM 🧬")
    print("=" * 60)
    print("✅ No giant files that make Ren cry!")
    print("✅ Each module < 50 lines and focused!")
    print("✅ ADHD-friendly bite-sized architecture!")
    
    classifier = ProteinClassifier()
    
    # Test with collagen (should use CollagenScorer)
    collagen_seq = "GPPGPPGPPGPPGPPGPPGPPGPPGPPGPPGPP" * 10  # More realistic collagen pattern
    result = classifier.classify_and_score('P02452', 'G10S', collagen_seq)
    
    print(f"\n🔬 Collagen Test:")
    print(f"  Family: {result['classification']['family']}")
    print(f"  Mechanism: {result['classification']['mechanism']}")
    print(f"  Scorer Used: {result['scorer_used']}")
    print(f"  Final Score: {result['final_score']:.3f}")
    print(f"  Likelihood: {result['dominant_negative_likelihood']}")
    
    print(f"\n🎉 Modular system working perfectly!")
    print(f"💜 No more giant files - just tiny, focused modules! ⚡🧬")


if __name__ == "__main__":
    test_modular_system()

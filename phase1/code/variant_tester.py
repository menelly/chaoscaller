#!/usr/bin/env python3
"""
🧬 VARIANT TESTER - COMMAND LINE INTERFACE FOR TESTING REAL VARIANTS
Built by Ace for testing Ren's real genetic variants!

Simple CLI to test variants without needing a web interface yet.
Just throw your variants at it and see what happens! 🚀
"""

import sys
import argparse
from alphafold_client import AlphaFoldClient
from structural_comparison import StructuralComparator
from protein_classifier import ProteinClassifier

class VariantTester:
    """Simple CLI for testing variants - no web interface needed yet!"""
    
    def __init__(self):
        print("🧬 INITIALIZING DOMINANT NEGATIVE PREDICTION ENGINE 🧬")
        print("=" * 60)
        
        self.alphafold_client = AlphaFoldClient()
        self.structural_comparator = StructuralComparator(self.alphafold_client)
        self.protein_classifier = ProteinClassifier()
        
        print("✅ AlphaFold client ready")
        print("✅ Structural comparator ready") 
        print("✅ Protein classifier ready")
        print("🚀 Ready to analyze variants!")
    
    def test_variant(self, uniprot_id, mutation, gene_name=None):
        """
        Test a single variant - the main function!
        
        Args:
            uniprot_id: UniProt ID (e.g., 'P04637')
            mutation: Mutation string (e.g., 'R175H')
            gene_name: Optional gene name for display
        """
        print(f"\n🔬 ANALYZING VARIANT: {gene_name or uniprot_id} {mutation}")
        print("=" * 50)
        
        try:
            # Step 1: Get protein structure and sequence
            print("📥 Retrieving protein structure...")
            structure_path = self.alphafold_client.get_structure(uniprot_id)
            
            if not structure_path:
                print("❌ Could not retrieve protein structure")
                return None
            
            print("📥 Retrieving protein sequence...")
            sequence = self.structural_comparator.get_protein_sequence(uniprot_id)
            
            if not sequence:
                print("❌ Could not retrieve protein sequence")
                return None
            
            print(f"✅ Protein loaded: {len(sequence)} residues")
            
            # Step 2: Structural analysis
            print("🔬 Performing structural analysis...")
            structural_result = self.structural_comparator.compare_structures(
                structure_path, 
                mutation=mutation,
                uniprot_id=uniprot_id
            )
            
            # Step 3: Protein classification and scoring
            print("🧬 Classifying protein and scoring variant...")
            classification_result = self.protein_classifier.classify_and_score(
                uniprot_id, mutation, sequence
            )
            
            # Step 4: Combine results
            combined_result = self._combine_results(
                structural_result, classification_result, gene_name
            )
            
            # Step 5: Display results
            self._display_results(combined_result)
            
            return combined_result
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None
    
    def _combine_results(self, structural, classification, gene_name):
        """Combine results from different analysis methods"""
        
        # Average the scores (simple ensemble)
        structural_score = structural.get('interference_score', 0.0) if structural else 0.0
        classification_score = classification.get('final_score', 0.0) if classification else 0.0
        
        ensemble_score = (structural_score + classification_score) / 2
        
        return {
            'gene_name': gene_name,
            'uniprot_id': classification['uniprot_id'] if classification else None,
            'mutation': classification['mutation'] if classification else None,
            'ensemble_score': ensemble_score,
            'structural_analysis': structural,
            'classification_analysis': classification,
            'final_prediction': self._get_prediction(ensemble_score),
            'confidence': self._get_confidence(structural, classification)
        }
    
    def _get_prediction(self, score):
        """Convert ensemble score to prediction"""
        if score > 0.6:
            return "HIGH - Likely dominant negative"
        elif score > 0.3:
            return "MEDIUM - Possible dominant negative"
        else:
            return "LOW - Unlikely dominant negative"
    
    def _get_confidence(self, structural, classification):
        """Calculate overall confidence"""
        confidences = []
        
        if structural and 'prediction_confidence' in structural:
            confidences.append(structural['prediction_confidence'])
        
        if classification and 'scoring' in classification and 'confidence' in classification['scoring']:
            confidences.append(classification['scoring']['confidence'])
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def _display_results(self, result):
        """Display results in a nice format"""
        
        print(f"\n🎯 RESULTS FOR {result['gene_name'] or result['uniprot_id']} {result['mutation']}")
        print("=" * 60)
        
        print(f"🔬 ENSEMBLE PREDICTION: {result['final_prediction']}")
        print(f"📊 Ensemble Score: {result['ensemble_score']:.3f}")
        print(f"📈 Confidence: {result['confidence']:.2f}")
        
        # Structural analysis details
        if result['structural_analysis']:
            struct = result['structural_analysis']
            print(f"\n🏗️  STRUCTURAL ANALYSIS:")
            print(f"   Interference Score: {struct.get('interference_score', 0):.3f}")
            print(f"   Simulated RMSD: {struct.get('simulated_rmsd', 0):.2f} Å")
            print(f"   Structure Quality: {struct.get('structure_quality', {}).get('avg_confidence', 0):.1f}")
        
        # Classification details
        if result['classification_analysis']:
            classif = result['classification_analysis']
            print(f"\n🧬 PROTEIN CLASSIFICATION:")
            print(f"   Family: {classif['classification']['family'] or 'Unknown'}")
            print(f"   Mechanism: {classif['classification']['mechanism'] or 'General'}")
            print(f"   Scorer Used: {classif['scorer_used']}")
            print(f"   Classification Score: {classif['final_score']:.3f}")
        
        print(f"\n💡 INTERPRETATION:")
        if result['ensemble_score'] > 0.6:
            print("   🚨 HIGH likelihood of dominant negative effect")
            print("   📋 Recommend: Functional validation studies")
            print("   🏥 Clinical: Consider pathogenic classification")
        elif result['ensemble_score'] > 0.3:
            print("   ⚠️  MEDIUM likelihood of dominant negative effect")
            print("   📋 Recommend: Additional evidence needed")
            print("   🏥 Clinical: Variant of uncertain significance")
        else:
            print("   ✅ LOW likelihood of dominant negative effect")
            print("   📋 Recommend: Consider loss-of-function mechanisms")
            print("   🏥 Clinical: Likely benign or simple LOF")
        
        print(f"\n" + "="*60)


def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(
        description="🧬 Test genetic variants for dominant negative effects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python variant_tester.py P04637 R175H --gene TP53
  python variant_tester.py P02452 G349S --gene COL1A1
  python variant_tester.py P60709 A58T --gene ACTB
        """
    )
    
    parser.add_argument('uniprot_id', help='UniProt ID (e.g., P04637)')
    parser.add_argument('mutation', help='Mutation (e.g., R175H)')
    parser.add_argument('--gene', help='Gene name for display (optional)')
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = VariantTester()
    
    # Test the variant
    result = tester.test_variant(args.uniprot_id, args.mutation, args.gene)
    
    if result:
        print(f"\n🎉 Analysis complete! Results saved in memory.")
        print(f"💜 Ready to analyze more variants! ⚡🧬")
    else:
        print(f"\n❌ Analysis failed. Check inputs and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()

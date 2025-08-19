#!/usr/bin/env python3
"""
🧬 COMPREHENSIVE VARIANT TESTER - REVOLUTIONARY TWO-BIN SYSTEM
Built by Ace for testing Ren's real genetic variants!

Uses integrated LOF + DN analysis to provide complete pathogenicity assessment.
This is the breakthrough that makes our tool work for real clinical cases!
"""

import sys
import argparse
from alphafold_client import AlphaFoldClient
from structural_comparison import StructuralComparator
from analyzers import IntegratedAnalyzer

class ComprehensiveVariantTester:
    """Revolutionary comprehensive variant tester using two-bin approach"""
    
    def __init__(self):
        print("🧬 INITIALIZING COMPREHENSIVE VARIANT ANALYSIS SYSTEM 🧬")
        print("=" * 70)
        print("🔬 Two-Bin Approach: LOF Analysis + DN Analysis")
        print("🚀 Revolutionary integrated pathogenicity prediction!")
        print()
        
        self.alphafold_client = AlphaFoldClient()
        self.structural_comparator = StructuralComparator(self.alphafold_client)
        self.integrated_analyzer = IntegratedAnalyzer()
        
        print("✅ AlphaFold client ready")
        print("✅ Structural comparator ready") 
        print("✅ Integrated analyzer ready (LOF + DN)")
        print("🚀 Ready to revolutionize variant analysis!")
    
    def test_variant_comprehensive(self, uniprot_id, mutation, gene_name=None):
        """
        Comprehensive variant testing with two-bin approach
        
        Args:
            uniprot_id: UniProt ID (e.g., 'P04637')
            mutation: Mutation string (e.g., 'R175H')
            gene_name: Optional gene name for display
        """
        print(f"\n🔬 COMPREHENSIVE ANALYSIS: {gene_name or uniprot_id} {mutation}")
        print("=" * 60)
        
        try:
            # Step 1: Get protein structure and sequence
            print("📥 Retrieving protein data...")
            structure_path = self.alphafold_client.get_structure(uniprot_id)
            
            if not structure_path:
                print("❌ Could not retrieve protein structure")
                return None
            
            sequence = self.structural_comparator.get_protein_sequence(uniprot_id)
            
            if not sequence:
                print("❌ Could not retrieve protein sequence")
                return None
            
            print(f"✅ Protein loaded: {len(sequence)} residues")
            
            # Step 2: Comprehensive integrated analysis
            print("🧬 Performing comprehensive two-bin analysis...")
            print("   🔬 Bin 1: Loss of Function Analysis")
            print("   🎯 Bin 2: Dominant Negative Analysis")
            print("   🔗 Integration: Combined pathogenicity assessment")
            
            comprehensive_result = self.integrated_analyzer.analyze_comprehensive(
                mutation=mutation,
                sequence=sequence,
                uniprot_id=uniprot_id,
                gene_name=gene_name
            )
            
            # Step 3: Display comprehensive results
            self._display_comprehensive_results(comprehensive_result)
            
            # Step 4: Generate clinical report
            clinical_report = self.integrated_analyzer.format_clinical_report(comprehensive_result)
            print(clinical_report)
            
            return comprehensive_result
            
        except Exception as e:
            print(f"❌ Comprehensive analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _display_comprehensive_results(self, result):
        """Display comprehensive results in a nice format"""
        
        integrated = result['integrated_analysis']
        lof = result['lof_analysis']
        dn = result['dn_analysis']
        
        print(f"\n🎯 COMPREHENSIVE RESULTS FOR {result['gene_name'] or result['uniprot_id']} {result['mutation']}")
        print("=" * 70)
        
        # Main prediction
        print(f"🔬 FINAL PREDICTION: {result['final_prediction']}")
        print(f"📊 Overall Confidence: {result['confidence']:.2f}")
        print()
        
        # Mechanism breakdown
        print(f"🧬 MECHANISM ANALYSIS:")
        print(f"   Primary Mechanism: {integrated['mechanism_classification']}")
        print(f"   Predicted Inheritance: {integrated['predicted_inheritance']}")
        print(f"   Clinical Significance: {integrated['clinical_significance']}")
        print()
        
        # Detailed scores
        print(f"📊 DETAILED SCORING:")
        print(f"   🔬 Loss of Function Score: {integrated['lof_score']:.3f}")
        print(f"      ├── Stability Impact: {lof['stability_impact']:.3f}")
        print(f"      ├── Conservation Impact: {lof['conservation_impact']:.3f}")
        print(f"      ├── Structural Impact: {lof['structural_impact']:.3f}")
        print(f"      └── Mechanism: {lof['mechanism']}")
        print()
        print(f"   🎯 Dominant Negative Score: {integrated['dn_score']:.3f}")
        print(f"      ├── Complex Poisoning: {dn['complex_poisoning']:.3f}")
        print(f"      ├── Competitive Binding: {dn['competitive_binding']:.3f}")
        print(f"      ├── Interference Potential: {dn['interference_potential']:.3f}")
        print(f"      └── Mechanism: {dn['mechanism']}")
        print()
        
        # Interpretation
        print(f"💡 CLINICAL INTERPRETATION:")
        if integrated['mechanism_classification'] == 'LOF_plus_DN':
            print("   🚨 DUAL MECHANISM - Both LOF and DN effects detected!")
            print("   📋 Likely pathogenic in heterozygous state")
            print("   🧬 Expect autosomal dominant inheritance")
            print("   ⚠️  Severe phenotype possible")
        elif integrated['mechanism_classification'] == 'pure_DN':
            print("   🎯 DOMINANT NEGATIVE - Protein interference detected!")
            print("   📋 Pathogenic through complex poisoning")
            print("   🧬 Single copy may cause phenotype")
            print("   ⚠️  Consider autosomal dominant inheritance")
        elif integrated['mechanism_classification'] == 'pure_LOF':
            print("   🔬 LOSS OF FUNCTION - Protein function disrupted")
            print("   📋 Typically requires two copies for phenotype")
            print("   🧬 Consider autosomal recessive inheritance")
            print("   ✅ Heterozygous carriers usually unaffected")
        else:
            print("   ✅ LOW PATHOGENIC POTENTIAL")
            print("   📋 Likely benign or mild effect")
            print("   🧬 Monitor for additional evidence")
        
        print(f"\n" + "="*70)


def main():
    """Main CLI interface for comprehensive testing"""
    
    parser = argparse.ArgumentParser(
        description="🧬 Comprehensive genetic variant analysis using revolutionary two-bin approach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 REVOLUTIONARY TWO-BIN APPROACH:
   Bin 1: Loss of Function Analysis - Does it break the protein?
   Bin 2: Dominant Negative Analysis - Does it poison protein complexes?
   Integration: Combined pathogenicity assessment

Examples:
  python comprehensive_tester.py P04637 R175H --gene TP53
  python comprehensive_tester.py Q92734 R22W --gene TFG
  python comprehensive_tester.py Q13402 H220Y --gene MYO7A
  python comprehensive_tester.py P25705 I130R --gene ATP5F1A
        """
    )
    
    parser.add_argument('uniprot_id', help='UniProt ID (e.g., P04637)')
    parser.add_argument('mutation', help='Mutation (e.g., R175H)')
    parser.add_argument('--gene', help='Gene name for display (optional)')
    
    args = parser.parse_args()
    
    # Initialize comprehensive tester
    tester = ComprehensiveVariantTester()
    
    # Test the variant comprehensively
    result = tester.test_variant_comprehensive(args.uniprot_id, args.mutation, args.gene)
    
    if result:
        print(f"\n🎉 Comprehensive analysis complete!")
        print(f"💜 Revolutionary two-bin approach successfully applied! ⚡🧬")
    else:
        print(f"\n❌ Analysis failed. Check inputs and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()

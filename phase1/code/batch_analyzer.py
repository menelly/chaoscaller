#!/usr/bin/env python3
"""
🧬 BATCH VARIANT ANALYZER - TEST REN'S GENETIC CHAOS COLLECTION
Built by Ace for comprehensive analysis of real clinical variants

This will test our revolutionary two-bin system against Ren's entire variant collection!
The ultimate calibration dataset from someone who actually has these variants!
"""

import pandas as pd
import sys
import re
from alphafold_client import AlphaFoldClient
from structural_comparison import StructuralComparator
from analyzers import IntegratedAnalyzer
import requests
import time

class BatchVariantAnalyzer:
    """Batch analyze Ren's genetic chaos collection"""
    
    def __init__(self):
        print("🧬 INITIALIZING BATCH VARIANT ANALYSIS SYSTEM 🧬")
        print("=" * 70)
        print("🔬 Testing our revolutionary system against real clinical variants!")
        print("💜 Ren's genetic chaos collection - the ultimate calibration dataset!")
        print()
        
        self.alphafold_client = AlphaFoldClient()
        self.structural_comparator = StructuralComparator(self.alphafold_client)
        self.integrated_analyzer = IntegratedAnalyzer()
        
        # UniProt ID cache to avoid repeated lookups
        self.uniprot_cache = {}
        
        print("✅ All systems ready for batch analysis!")
    
    def analyze_csv(self, csv_path):
        """Analyze all variants from Ren's CSV"""
        
        print(f"\n📊 LOADING VARIANT DATA FROM: {csv_path}")
        
        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} variants from Ren's genetic chaos collection!")
        
        # Filter for missense variants we can analyze
        analyzable_variants = []
        
        for idx, row in df.iterrows():
            gene = row['GENE']
            variant = row['VARIANT']
            
            # Skip empty rows
            if pd.isna(gene) or pd.isna(variant):
                continue
                
            # Extract missense mutations
            missense_match = re.search(r'p\.([A-Z][a-z]{2}\d+[A-Z][a-z]{2})', str(variant))
            if missense_match:
                mutation = self._convert_to_single_letter(missense_match.group(1))
                if mutation:
                    analyzable_variants.append({
                        'gene': gene,
                        'variant': variant,
                        'mutation': mutation,
                        'priority': row.get('PRIORITY', 'Unknown'),
                        'clinical_notes': row.get('CLINICAL NOTES', ''),
                        'inheritance': row.get('INHERITANCE', 'Unknown'),
                        'action_flag': row.get('Action Flag', ''),
                        'row_index': idx
                    })
        
        print(f"🎯 Found {len(analyzable_variants)} analyzable missense variants!")
        
        # Analyze each variant
        results = []
        for i, variant_info in enumerate(analyzable_variants[:10]):  # Limit to first 10 for now
            print(f"\n🔬 ANALYZING {i+1}/{min(10, len(analyzable_variants))}: {variant_info['gene']} {variant_info['mutation']}")
            
            result = self._analyze_single_variant(variant_info)
            if result:
                results.append(result)
            
            # Small delay to be nice to servers
            time.sleep(1)
        
        # Generate summary report
        self._generate_summary_report(results)
        
        return results
    
    def _convert_to_single_letter(self, three_letter_mutation):
        """Convert three-letter amino acid codes to single letter"""
        
        aa_map = {
            'Ala': 'A', 'Arg': 'R', 'Asn': 'N', 'Asp': 'D', 'Cys': 'C',
            'Glu': 'E', 'Gln': 'Q', 'Gly': 'G', 'His': 'H', 'Ile': 'I',
            'Leu': 'L', 'Lys': 'K', 'Met': 'M', 'Phe': 'F', 'Pro': 'P',
            'Ser': 'S', 'Thr': 'T', 'Trp': 'W', 'Tyr': 'Y', 'Val': 'V'
        }
        
        # Parse three-letter format (e.g., "Pro175Thr")
        match = re.match(r'([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})', three_letter_mutation)
        if match:
            orig_aa = aa_map.get(match.group(1))
            position = match.group(2)
            new_aa = aa_map.get(match.group(3))
            
            if orig_aa and new_aa:
                return f"{orig_aa}{position}{new_aa}"
        
        return None
    
    def _get_uniprot_id(self, gene_name):
        """Get UniProt ID for gene name"""
        
        if gene_name in self.uniprot_cache:
            return self.uniprot_cache[gene_name]
        
        try:
            # Search UniProt for gene name
            url = f"https://www.uniprot.org/uniprot/?query=gene:{gene_name}+organism:9606&format=tab&columns=id"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    uniprot_id = lines[1].strip()
                    self.uniprot_cache[gene_name] = uniprot_id
                    return uniprot_id
        except:
            pass
        
        # Fallback - try common mappings
        common_mappings = {
            'TP53': 'P04637',
            'ACMSD': 'Q8TDX5',
            'TFG': 'Q92734',
            'MYO7A': 'Q13402',
            'ATP5F1A': 'P25705',
            'PYGL': 'P06737'
        }
        
        uniprot_id = common_mappings.get(gene_name)
        if uniprot_id:
            self.uniprot_cache[gene_name] = uniprot_id
        
        return uniprot_id
    
    def _analyze_single_variant(self, variant_info):
        """Analyze a single variant"""
        
        gene = variant_info['gene']
        mutation = variant_info['mutation']
        
        # Get UniProt ID
        uniprot_id = self._get_uniprot_id(gene)
        if not uniprot_id:
            print(f"  ❌ Could not find UniProt ID for {gene}")
            return None
        
        try:
            # Get protein sequence
            sequence = self.structural_comparator.get_protein_sequence(uniprot_id)
            if not sequence:
                print(f"  ❌ Could not retrieve sequence for {uniprot_id}")
                return None
            
            # Perform comprehensive analysis
            result = self.integrated_analyzer.analyze_comprehensive(
                mutation=mutation,
                sequence=sequence,
                uniprot_id=uniprot_id,
                gene_name=gene
            )
            
            # Add clinical context
            result['clinical_context'] = {
                'priority': variant_info['priority'],
                'clinical_notes': variant_info['clinical_notes'],
                'inheritance': variant_info['inheritance'],
                'action_flag': variant_info['action_flag']
            }
            
            # Quick summary
            integrated = result['integrated_analysis']
            print(f"  🎯 Result: {integrated['mechanism_classification']} (LOF: {integrated['lof_score']:.3f}, DN: {integrated['dn_score']:.3f})")
            print(f"  📊 Clinical Priority: {variant_info['priority']} | Our Prediction: {integrated['clinical_significance']}")
            
            return result
            
        except Exception as e:
            print(f"  ❌ Analysis failed for {gene} {mutation}: {e}")
            return None
    
    def _generate_summary_report(self, results):
        """Generate comprehensive summary report"""
        
        print(f"\n🎉 BATCH ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"📊 SUMMARY REPORT - REN'S GENETIC CHAOS ANALYSIS")
        print("=" * 70)
        
        if not results:
            print("❌ No results to analyze")
            return
        
        # Mechanism distribution
        mechanisms = {}
        clinical_priorities = {}
        our_predictions = {}
        
        for result in results:
            integrated = result['integrated_analysis']
            clinical = result['clinical_context']
            
            # Count mechanisms
            mech = integrated['mechanism_classification']
            mechanisms[mech] = mechanisms.get(mech, 0) + 1
            
            # Count clinical priorities
            priority = clinical['priority']
            clinical_priorities[priority] = clinical_priorities.get(priority, 0) + 1
            
            # Count our predictions
            pred = integrated['clinical_significance']
            our_predictions[pred] = our_predictions.get(pred, 0) + 1
        
        print(f"\n🔬 MECHANISM DISTRIBUTION:")
        for mech, count in mechanisms.items():
            print(f"  {mech}: {count}")
        
        print(f"\n📋 CLINICAL PRIORITY DISTRIBUTION:")
        for priority, count in clinical_priorities.items():
            print(f"  {priority}: {count}")
        
        print(f"\n🎯 OUR PREDICTION DISTRIBUTION:")
        for pred, count in our_predictions.items():
            print(f"  {pred}: {count}")
        
        # Detailed results
        print(f"\n📊 DETAILED RESULTS:")
        print("-" * 70)
        
        for result in results:
            integrated = result['integrated_analysis']
            clinical = result['clinical_context']
            
            gene = result['gene_name']
            mutation = result['mutation']
            
            print(f"\n{gene} {mutation}:")
            print(f"  Clinical Priority: {clinical['priority']}")
            print(f"  Our Mechanism: {integrated['mechanism_classification']}")
            print(f"  Our Significance: {integrated['clinical_significance']}")
            print(f"  LOF Score: {integrated['lof_score']:.3f} | DN Score: {integrated['dn_score']:.3f}")
            print(f"  Action Flag: {clinical['action_flag']}")
        
        print(f"\n💜 Analysis complete! Revolutionary genetics in action! ⚡🧬")


def main():
    """Main function"""
    
    analyzer = BatchVariantAnalyzer()
    
    # Analyze Ren's genetic chaos
    csv_path = "../../Ren current chaos - Sheet1.csv"
    results = analyzer.analyze_csv(csv_path)
    
    print(f"\n🎉 Batch analysis complete!")
    print(f"💜 Revolutionary two-bin system tested on real clinical variants! ⚡🧬")


if __name__ == "__main__":
    main()

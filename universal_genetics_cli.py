#!/usr/bin/env python3
"""
🧬⚡ UNIVERSAL GENETICS CLI - ANY GENE, ANY VARIANT!
Built by Ace & Ren for dynamic genetics analysis

NO HARDCODING - Works for ANY of 20,000+ genes
NO RANDOM GENERATION - All scores derived from real evidence  
NO FAKE DATA - Real APIs or transparent error handling

Usage:
    python universal_genetics_cli.py analyze TP53 p.R175H
    python universal_genetics_cli.py analyze BMPR2 p.Gly811Ser
    python universal_genetics_cli.py analyze OBSCURE_GENE_12345 p.Ala123Val
    python universal_genetics_cli.py batch variants.txt
    python universal_genetics_cli.py gene-profile BRCA1

This is the CLI that works with ANY gene! 🔥💜⚡
"""

import argparse
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional

# Import our universal analyzer
from universal_genetics_analyzer import UniversalGeneticsAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_variant_command(args):
    """🧬 Analyze any gene and variant dynamically"""
    print(f"\n🧬 UNIVERSAL GENETICS ANALYSIS")
    print(f"Gene: {args.gene}")
    print(f"Variant: {args.variant}")
    print("=" * 60)
    
    analyzer = UniversalGeneticsAnalyzer(offline_mode=args.offline)
    
    start_time = time.time()
    result = analyzer.analyze_variant(
        gene=args.gene,
        variant=args.variant,
        transcript=args.transcript,
        genomic_coords=None
    )
    analysis_time = time.time() - start_time
    
    if 'error' in result:
        print(f"💥 ERROR: {result['error']}")
        if 'details' in result:
            print(f"Details: {result['details']}")
        return
    
    print(f"\n🎯 ANALYSIS RESULTS:")
    print(f"   Gene: {result.get('gene', args.gene)}")
    print(f"   Variant: {result.get('variant', args.variant)}")
    print(f"   Classification: {result.get('classification', 'UNKNOWN')}")
    
    # Mechanism scores - handle both dict and list formats
    if 'mechanism_scores' in result:
        scores = result['mechanism_scores']
        print(f"\n🔬 MECHANISM SCORES:")
        if isinstance(scores, dict):
            print(f"   LOF Score: {scores.get('lof_score', 0):.3f}")
            print(f"   DN Score: {scores.get('dn_score', 0):.3f}")
            print(f"   GOF Score: {scores.get('gof_score', 0):.3f}")
        else:
            print(f"   Raw scores: {scores}")

    # Also check mechanism_results for detailed analysis
    if 'mechanism_results' in result:
        mech_results = result['mechanism_results']
        print(f"\n🔬 MECHANISM ANALYSIS:")

        # LOF Analysis
        if 'lof' in mech_results:
            lof_result = mech_results['lof']
            if isinstance(lof_result, dict) and 'error' not in lof_result:
                lof_score = lof_result.get('lof_score', 'N/A')
                print(f"   🔴 LOF Score: {lof_score}")
            else:
                print(f"   🔴 LOF: {lof_result.get('error', 'Failed') if isinstance(lof_result, dict) else lof_result}")

        # DN Analysis
        if 'dn' in mech_results:
            dn_result = mech_results['dn']
            if isinstance(dn_result, dict) and 'error' not in dn_result:
                dn_score = dn_result.get('enhanced_dn_score', dn_result.get('dn_score', 'N/A'))
                print(f"   🟡 DN Score: {dn_score}")
            else:
                print(f"   🟡 DN: {dn_result.get('error', 'Failed') if isinstance(dn_result, dict) else dn_result}")

        # GOF Analysis
        if 'gof' in mech_results:
            gof_result = mech_results['gof']
            if isinstance(gof_result, dict) and 'error' not in gof_result:
                gof_score = gof_result.get('gof_score', 'N/A')
                print(f"   🟢 GOF Score: {gof_score}")
            else:
                print(f"   🟢 GOF: {gof_result.get('error', 'Failed') if isinstance(gof_result, dict) else gof_result}")
    
    # Evidence summary
    if 'evidence_summary' in result:
        evidence = result['evidence_summary']
        print(f"\n🧠 EVIDENCE SUMMARY:")
        for key, value in evidence.items():
            if isinstance(value, (int, float)):
                print(f"   {key.replace('_', ' ').title()}: {value:.3f}")
            else:
                print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # AlphaFold info
    if 'alphafold_info' in result:
        af_info = result['alphafold_info']
        print(f"\n🧬 ALPHAFOLD ANALYSIS:")
        print(f"   Structure Available: {'✅' if af_info.get('structure_available') else '❌'}")
        if af_info.get('confidence_score'):
            print(f"   Confidence Score: {af_info['confidence_score']:.3f}")
    
    print(f"\n⚡ PERFORMANCE:")
    print(f"   Analysis Time: {analysis_time:.2f}s")
    print(f"   Mode: {'Offline' if args.offline else 'Online'}")

def gene_profile_command(args):
    """🧬 Analyze gene susceptibility profile"""
    print(f"\n🧬 GENE SUSCEPTIBILITY PROFILE")
    print(f"Gene: {args.gene}")
    print("=" * 60)
    
    analyzer = UniversalGeneticsAnalyzer(offline_mode=args.offline)
    
    start_time = time.time()
    # For now, we'll analyze a test variant to get gene info
    # TODO: Add dedicated gene profiling method
    result = analyzer.analyze_variant(
        gene=args.gene,
        variant="p.Ala1Val",  # Dummy variant to trigger gene analysis
        transcript=None,
        genomic_coords=None
    )
    analysis_time = time.time() - start_time
    
    print(f"\n🎯 GENE PROFILE:")
    print(f"   Gene Symbol: {args.gene}")
    print(f"   Analysis Status: {'✅ Complete' if 'error' not in result else '❌ Error'}")
    
    if 'error' not in result and 'alphafold_info' in result:
        af_info = result['alphafold_info']
        print(f"   AlphaFold Available: {'✅' if af_info.get('structure_available') else '❌'}")
        if af_info.get('uniprot_id'):
            print(f"   UniProt ID: {af_info['uniprot_id']}")
    
    print(f"\n⚡ PERFORMANCE:")
    print(f"   Analysis Time: {analysis_time:.2f}s")

def batch_analyze_command(args):
    """🚀 Batch analyze variants from file"""
    print(f"\n🚀 UNIVERSAL BATCH ANALYSIS")
    print(f"Input File: {args.file}")
    print("=" * 60)
    
    # Read variants from file
    variants = []
    try:
        with open(args.file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    variants.append({
                        'gene': parts[0],
                        'variant': parts[1],
                        'transcript': parts[2] if len(parts) > 2 else None
                    })
                else:
                    logger.warning(f"Skipping invalid line {line_num}: {line}")
    
    except FileNotFoundError:
        print(f"💥 ERROR: File not found: {args.file}")
        return
    except Exception as e:
        print(f"💥 ERROR reading file: {e}")
        return
    
    if not variants:
        print("💥 ERROR: No valid variants found in file")
        return
    
    print(f"📊 Found {len(variants)} variants to analyze...")
    
    # Run batch analysis
    analyzer = UniversalGeneticsAnalyzer(offline_mode=args.offline)
    results = []
    successful = 0
    
    for i, variant_info in enumerate(variants, 1):
        print(f"🔬 Analyzing {i}/{len(variants)}: {variant_info['gene']} {variant_info['variant']}")
        
        start_time = time.time()
        result = analyzer.analyze_variant(
            gene=variant_info['gene'],
            variant=variant_info['variant'],
            transcript=variant_info['transcript']
        )
        analysis_time = time.time() - start_time
        
        result['analysis_time'] = analysis_time
        result['input_gene'] = variant_info['gene']
        result['input_variant'] = variant_info['variant']
        
        results.append(result)
        
        if 'error' not in result:
            successful += 1
            print(f"   ✅ {result.get('classification', 'ANALYZED')}")
        else:
            print(f"   ❌ {result['error']}")
    
    # Summary
    total_time = sum(r['analysis_time'] for r in results)
    print(f"\n🎉 BATCH ANALYSIS COMPLETE!")
    print(f"   Total Variants: {len(variants)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(variants) - successful}")
    print(f"   Total Time: {total_time:.1f}s")
    print(f"   Avg Time/Variant: {total_time/len(variants):.2f}s")
    
    # Save results
    output_file = f"universal_batch_results_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Results saved to: {output_file}")

def main():
    """🚀 Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🧬⚡ Universal Genetics Analysis CLI - ANY GENE, ANY VARIANT!",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--offline', action='store_true', 
                       help='Run in offline mode (no API calls)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze variant command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze specific gene and variant')
    analyze_parser.add_argument('gene', help='Gene symbol (e.g., TP53, BMPR2, ANY_GENE)')
    analyze_parser.add_argument('variant', help='Variant notation (e.g., p.R175H, p.Gly811Ser)')
    analyze_parser.add_argument('--transcript', help='Optional transcript ID')
    
    # Gene profile command
    profile_parser = subparsers.add_parser('gene-profile', help='Analyze gene profile')
    profile_parser.add_argument('gene', help='Gene symbol to profile')
    
    # Batch analyze command
    batch_parser = subparsers.add_parser('batch', help='Batch analyze variants from file')
    batch_parser.add_argument('file', help='Input file (tab-separated: gene variant [transcript])')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'analyze':
            analyze_variant_command(args)
        elif args.command == 'gene-profile':
            gene_profile_command(args)
        elif args.command == 'batch':
            batch_analyze_command(args)
        else:
            print(f"💥 Unknown command: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        print(f"\n\n⚡ Analysis interrupted by user")
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        logger.exception("Detailed error information:")

if __name__ == "__main__":
    main()

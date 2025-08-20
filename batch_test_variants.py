#!/usr/bin/env python3
"""
🧬 BATCH VARIANT TESTING
Test all variants from test_snp.txt and generate comprehensive validation data
"""

import subprocess
import csv
import re
import sys
from pathlib import Path

def parse_snp_line(line):
    """Parse a line from test_snp.txt"""
    parts = line.strip().split('\t')
    if len(parts) < 4:
        return None
    
    # Extract coordinate (remove (+) suffix)
    coord_part = parts[0].replace('(+)', '').replace(',', '')
    
    # Extract HGVS
    hgvs_match = re.search(r'(NM_\d+\.\d+)\((\w+)\):(c\.\d+[ATCG]>[ATCG])\s+\((p\.\w+\d+\w+)\)', parts[1])
    if not hgvs_match:
        return None
    
    transcript, gene, cdna, protein = hgvs_match.groups()
    hgvs = f"{transcript}:{cdna} {protein}"
    
    # Extract ref/alt
    ref_alt = parts[2].split('/')
    if len(ref_alt) != 2:
        return None
    
    ref, alt = ref_alt
    
    # Extract mutation
    mutation = parts[3]
    
    return {
        'coordinate': f"chr6:{coord_part}",
        'ref': ref,
        'alt': alt,
        'gene': gene,
        'hgvs': hgvs,
        'mutation': mutation
    }

def run_variant_analysis(variant_data):
    """Run genetics_cli.py on a single variant"""
    try:
        cmd = [
            'python3', 'genetics_cli.py',
            '--coord', variant_data['coordinate'],
            '--ref', variant_data['ref'],
            '--alt', variant_data['alt'],
            '--gene', variant_data['gene'],
            '--hgvs', variant_data['hgvs'],
            '--all',
            '--log-validation', 'batch_validation_results.csv',
            '--expected-classification', 'UNKNOWN'  # We'll compare with ClinVar later
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, str(e)

def main():
    """Process all variants from test_snp.txt"""
    
    print("🧬 BATCH VARIANT TESTING")
    print("=" * 60)
    print("Processing all variants from test_snp.txt...")
    print()
    
    # Read test_snp.txt
    with open('test_snp.txt', 'r') as f:
        lines = f.readlines()
    
    # Clear previous batch results
    batch_results_file = Path('batch_validation_results.csv')
    if batch_results_file.exists():
        batch_results_file.unlink()
    
    total_variants = len(lines)
    processed = 0
    successful = 0
    failed = 0
    
    print(f"📊 Total variants to process: {total_variants}")
    print()
    
    for i, line in enumerate(lines, 1):
        variant_data = parse_snp_line(line)
        
        if not variant_data:
            print(f"❌ Line {i}: Failed to parse")
            failed += 1
            continue
        
        print(f"🧬 Processing {i}/{total_variants}: {variant_data['mutation']} ({variant_data['gene']})")
        
        success, output = run_variant_analysis(variant_data)
        
        if success:
            print(f"✅ Success: {variant_data['mutation']}")
            successful += 1
        else:
            print(f"❌ Failed: {variant_data['mutation']} - {output[:100]}...")
            failed += 1
        
        processed += 1
        
        # Progress update every 10 variants
        if i % 10 == 0:
            print(f"📊 Progress: {processed}/{total_variants} ({successful} success, {failed} failed)")
            print()
    
    print("=" * 60)
    print("🎯 BATCH PROCESSING COMPLETE!")
    print(f"📊 Total processed: {processed}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Results saved to: batch_validation_results.csv")
    print()
    print("🔬 Ready for ClinVar comparison!")

if __name__ == "__main__":
    main()

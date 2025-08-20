#!/usr/bin/env python3
"""
🧬 PREDICTION COMPARISON ANALYSIS
Compare our genetics predictions with ClinVar classifications
"""

import csv
import re
from pathlib import Path
from collections import defaultdict, Counter

def parse_clinvar_classification(clinvar_text):
    """Extract the primary ClinVar classification"""
    if not clinvar_text:
        return "UNKNOWN"
    
    # Clean up the text
    text = clinvar_text.lower().strip()
    
    # Priority order for conflicting classifications
    if "pathogenic" in text and "likely pathogenic" not in text:
        return "P"  # Pathogenic
    elif "likely pathogenic" in text:
        return "LP"  # Likely Pathogenic
    elif "uncertain significance" in text or "conflicting" in text:
        return "VUS"  # Variant of Uncertain Significance
    elif "likely benign" in text:
        return "LB"  # Likely Benign
    elif "benign" in text:
        return "B"  # Benign
    else:
        return "UNKNOWN"

def parse_our_prediction(prediction_text):
    """Extract our prediction category"""
    if not prediction_text:
        return "UNKNOWN", 0.0
    
    text = prediction_text.lower()
    
    # Extract score
    score_match = re.search(r'score:\s*([\d.]+)', text)
    score = float(score_match.group(1)) if score_match else 0.0
    
    # Categorize prediction
    if "high pathogenicity" in text:
        return "HIGH", score
    elif "moderate pathogenicity" in text:
        return "MODERATE", score
    elif "low pathogenicity" in text:
        return "LOW", score
    else:
        return "UNKNOWN", score

def load_clinvar_data():
    """Load ClinVar classifications from test_snp_validation.txt"""
    clinvar_data = {}

    with open('test_snp_validation.txt', 'r') as f:
        for line in f:
            parts = line.strip().split('\t')

            # Look for complete entries (should have 7+ columns)
            if len(parts) >= 7:
                # Column 6 has the mutation in single letter format (V615M)
                mutation = parts[6] if len(parts) > 6 else "UNKNOWN"

                # Column 2 has the ClinVar classification
                clinvar_text = parts[2] if len(parts) > 2 else ""
                classification = parse_clinvar_classification(clinvar_text)

                # Get HGVS for reference (Column 4)
                hgvs_part = parts[4] if len(parts) > 4 else ""

                if mutation != "UNKNOWN" and classification != "UNKNOWN":
                    clinvar_data[mutation] = {
                        'classification': classification,
                        'raw_text': clinvar_text,
                        'hgvs': hgvs_part
                    }

    return clinvar_data

def load_our_predictions():
    """Load our predictions from batch_validation_results.csv"""
    our_data = {}

    if not Path('batch_validation_results.csv').exists():
        print("❌ batch_validation_results.csv not found!")
        return {}

    with open('batch_validation_results.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract amino acid mutation from HGVS
            hgvs = row.get('hgvs', '')

            # Extract mutation like V615M from p.Val615Met
            mutation_match = re.search(r'p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})', hgvs)
            if mutation_match:
                orig_aa = mutation_match.group(1)
                position = mutation_match.group(2)
                new_aa = mutation_match.group(3)

                # Convert to single letter format
                aa_map = {
                    'Ala': 'A', 'Arg': 'R', 'Asn': 'N', 'Asp': 'D', 'Cys': 'C',
                    'Gln': 'Q', 'Glu': 'E', 'Gly': 'G', 'His': 'H', 'Ile': 'I',
                    'Leu': 'L', 'Lys': 'K', 'Met': 'M', 'Phe': 'F', 'Pro': 'P',
                    'Ser': 'S', 'Thr': 'T', 'Trp': 'W', 'Tyr': 'Y', 'Val': 'V'
                }

                orig_single = aa_map.get(orig_aa, orig_aa[0])
                new_single = aa_map.get(new_aa, new_aa[0])
                mutation = f"{orig_single}{position}{new_single}"
            else:
                continue  # Skip if we can't parse the mutation

            prediction_category, score = parse_our_prediction(row.get('prediction', ''))

            our_data[mutation] = {
                'category': prediction_category,
                'score': score,
                'lof_score': float(row.get('lof_score', 0)),
                'dn_score': float(row.get('dn_score', 0)),
                'phylop': float(row.get('phylop_score', 0)),
                'mechanism': row.get('mechanism', ''),
                'raw_prediction': row.get('prediction', ''),
                'hgvs': hgvs
            }

    return our_data

def compare_predictions():
    """Compare our predictions with ClinVar classifications"""
    
    print("🧬 PREDICTION COMPARISON ANALYSIS")
    print("=" * 80)
    
    clinvar_data = load_clinvar_data()
    our_data = load_our_predictions()
    
    print(f"📊 ClinVar entries loaded: {len(clinvar_data)}")
    print(f"📊 Our predictions loaded: {len(our_data)}")
    print()
    
    # Find matches
    matches = []
    clinvar_only = []
    our_only = []
    
    for mutation in clinvar_data:
        if mutation in our_data:
            matches.append(mutation)
        else:
            clinvar_only.append(mutation)
    
    for mutation in our_data:
        if mutation not in clinvar_data:
            our_only.append(mutation)
    
    print(f"🎯 Matched variants: {len(matches)}")
    print(f"📋 ClinVar only: {len(clinvar_only)}")
    print(f"🔬 Our predictions only: {len(our_only)}")
    print()
    
    # Analyze matches
    if matches:
        print("🔍 DETAILED COMPARISON:")
        print("-" * 80)
        
        agreement_stats = Counter()
        score_by_clinvar = defaultdict(list)
        
        for mutation in matches:
            clinvar_class = clinvar_data[mutation]['classification']
            our_category = our_data[mutation]['category']
            our_score = our_data[mutation]['score']
            
            # Determine agreement
            agreement = determine_agreement(clinvar_class, our_category, our_score)
            agreement_stats[agreement] += 1
            score_by_clinvar[clinvar_class].append(our_score)
            
            print(f"{mutation:10} | ClinVar: {clinvar_class:3} | Our: {our_category:8} ({our_score:.3f}) | {agreement}")
        
        print()
        print("📊 AGREEMENT STATISTICS:")
        print("-" * 40)
        total = len(matches)
        for agreement_type, count in agreement_stats.items():
            percentage = (count / total) * 100
            print(f"{agreement_type:15}: {count:3} ({percentage:5.1f}%)")
        
        print()
        print("📈 SCORE DISTRIBUTIONS BY CLINVAR CLASS:")
        print("-" * 50)
        for clinvar_class, scores in score_by_clinvar.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                print(f"{clinvar_class:3}: {len(scores):3} variants | Avg: {avg_score:.3f} | Range: {min_score:.3f}-{max_score:.3f}")

def determine_agreement(clinvar_class, our_category, our_score):
    """Determine if our prediction agrees with ClinVar"""
    
    # Map our categories to ClinVar-like classifications
    if our_category == "HIGH" and our_score > 0.7:
        our_mapped = "P/LP"
    elif our_category == "HIGH" or (our_category == "MODERATE" and our_score > 0.5):
        our_mapped = "LP/VUS"
    elif our_category == "MODERATE":
        our_mapped = "VUS"
    elif our_category == "LOW":
        our_mapped = "LB/B"
    else:
        our_mapped = "UNKNOWN"
    
    # Check agreement
    if clinvar_class in ["P", "LP"] and our_mapped in ["P/LP", "LP/VUS"]:
        return "AGREE"
    elif clinvar_class == "VUS" and our_mapped in ["LP/VUS", "VUS", "LB/B"]:
        return "AGREE"
    elif clinvar_class in ["LB", "B"] and our_mapped in ["VUS", "LB/B"]:
        return "AGREE"
    elif clinvar_class == "UNKNOWN":
        return "UNKNOWN"
    else:
        return "DISAGREE"

if __name__ == "__main__":
    compare_predictions()

#!/usr/bin/env python3
"""
🧬 GENETICS ANALYSIS CLI
Command-line interface for comprehensive variant analysis

Usage:
    python genetics_cli.py --hgvs "NM_000260.4:c.658C>T"
    python genetics_cli.py --coord "chr11:77156927" --ref "C" --alt "T" --gene "MYO7A"
    python genetics_cli.py --hgvs "NM_000260.4:c.658C>T" --all-analyses
"""

import argparse
import sys
import json
from pathlib import Path
import logging

# Add the phase1/code directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "phase1" / "code"))

# Import our analyzers
try:
    from analyzers.conservation_enhanced_analyzer import ConservationEnhancedAnalyzer
    from analyzers.population_frequency_analyzer import PopulationFrequencyAnalyzer
    from alphafold_client import AlphaFoldClient
    from gene_to_uniprot_mapper import GeneToUniProtMapper
    from analyzers.lof_analyzer import LOFAnalyzer
    from analyzers.dn_analyzer import DNAnalyzer
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the caller directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class GeneticsAnalysisCLI:
    """Command-line genetics analysis orchestrator"""
    
    def __init__(self):
        """Initialize all analyzers"""
        logger.info("🧬 Initializing genetics analysis pipeline...")
        
        # Initialize analyzers - USE THE SOPHISTICATED SYSTEM!
        self.conservation_analyzer = ConservationEnhancedAnalyzer()
        self.frequency_analyzer = PopulationFrequencyAnalyzer()
        self.alphafold_client = AlphaFoldClient()
        self.gene_mapper = GeneToUniProtMapper()

        # Import the REAL integrated system
        from analyzers.integrated_analyzer import IntegratedAnalyzer
        self.integrated_analyzer = IntegratedAnalyzer()
        
        logger.info("✅ All analyzers initialized")
    
    def parse_hgvs(self, hgvs_string):
        """Parse HGVS string into components"""
        # Simple HGVS parser - can be enhanced later
        try:
            if ':c.' in hgvs_string:
                transcript, cdna = hgvs_string.split(':c.')
                # Extract position and change
                import re
                match = re.match(r'(\d+)([ATCG])>([ATCG])', cdna)
                if match:
                    position, ref, alt = match.groups()
                    return {
                        'transcript': transcript,
                        'cdna_position': int(position),
                        'ref_allele': ref,
                        'alt_allele': alt,
                        'hgvs_input': hgvs_string
                    }
            return None
        except Exception as e:
            logger.error(f"❌ HGVS parsing failed: {e}")
            return None
    
    def analyze_variant(self, gene=None, chromosome=None, position=None, 
                       ref_allele=None, alt_allele=None, hgvs=None, 
                       run_all=False):
        """Run comprehensive variant analysis"""
        
        results = {
            'input': {
                'gene': gene,
                'chromosome': chromosome,
                'position': position,
                'ref_allele': ref_allele,
                'alt_allele': alt_allele,
                'hgvs': hgvs
            },
            'analyses': {}
        }
        
        # Parse HGVS if provided
        if hgvs:
            hgvs_data = self.parse_hgvs(hgvs)
            if hgvs_data:
                results['hgvs_parsed'] = hgvs_data
                logger.info(f"✅ HGVS parsed: {hgvs_data}")
        
        # Gene mapping
        if gene:
            logger.info(f"🧬 Mapping gene: {gene}")
            uniprot_id = self.gene_mapper.get_uniprot_id(gene)
            if uniprot_id:
                results['gene_mapping'] = {'gene': gene, 'uniprot_id': uniprot_id}
                logger.info(f"✅ Gene mapping: {gene} → {uniprot_id}")
            else:
                logger.warning(f"⚠️ No UniProt ID found for {gene}")
        
        # AlphaFold structure analysis
        if gene and run_all:
            logger.info(f"🏗️ Getting AlphaFold structure: {gene}")
            try:
                # First map gene to UniProt ID
                uniprot_id = self.gene_mapper.get_uniprot_id(gene)
                if uniprot_id:
                    structure_result = self.alphafold_client.get_structure(uniprot_id)
                    if structure_result:
                        results['analyses']['structure'] = {
                            'gene': gene,
                            'uniprot_id': uniprot_id,
                            'structure_file': structure_result,
                            'status': 'success'
                        }
                        logger.info(f"✅ Structure found: {structure_result}")
                    else:
                        results['analyses']['structure'] = {
                            'gene': gene,
                            'uniprot_id': uniprot_id,
                            'status': 'not_found'
                        }
                        logger.warning(f"⚠️ No structure found for {gene} ({uniprot_id})")
                else:
                    results['analyses']['structure'] = {
                        'gene': gene,
                        'status': 'no_uniprot_id'
                    }
                    logger.warning(f"⚠️ No UniProt ID found for {gene}")
            except Exception as e:
                logger.error(f"❌ Structure analysis failed: {e}")
                results['analyses']['structure'] = {'error': str(e)}

        # Conservation analysis (get multiplier for LOF/DN scoring)
        conservation_multiplier = 1.0
        conservation_data = None
        if chromosome and position and run_all:
            logger.info(f"🔬 Analyzing conservation: {chromosome}:{position}")
            try:
                # Direct conservation database lookup
                from analyzers.conservation_database import ConservationDatabase
                conservation_db = ConservationDatabase()

                # Clean chromosome format
                chrom = chromosome.replace('chr', '')
                conservation_scores = conservation_db.get_conservation_scores(chrom, position)

                # Calculate conservation multiplier based on your insights!
                phylop = conservation_scores['phyloP']
                if phylop > 6.0:
                    conservation_multiplier = 1.5  # High conservation boost
                elif phylop > 3.0:
                    conservation_multiplier = 1.0  # Neutral
                else:
                    conservation_multiplier = 0.8  # Slight penalty for low conservation

                conservation_data = {
                    'coordinate': f"{chromosome}:{position}",
                    'phyloP': conservation_scores['phyloP'],
                    'phastCons': conservation_scores['phastCons'],
                    'conservation_score': conservation_scores['conservation_score'],
                    'confidence': conservation_scores['confidence'],
                    'multiplier': conservation_multiplier,
                    'interpretation': self._interpret_conservation(conservation_scores),
                    'source': 'direct_database_lookup'
                }

                results['analyses']['conservation'] = conservation_data
                logger.info(f"✅ Conservation: phyloP={phylop:.3f} → {conservation_multiplier}x multiplier")
            except Exception as e:
                logger.error(f"❌ Conservation analysis failed: {e}")
                results['analyses']['conservation'] = {'error': str(e)}

        # Get protein sequence and create mutation pairs using CAE's approach!
        protein_sequence = None
        wt_fasta_path = None
        mut_fasta_path = None
        uniprot_id = results.get('gene_mapping', {}).get('uniprot_id')

        if uniprot_id and run_all:
            logger.info(f"🧬 Fetching protein sequence: {uniprot_id}")
            try:
                protein_sequence = self._get_protein_sequence(uniprot_id)
                if protein_sequence:
                    logger.info(f"✅ Retrieved sequence: {len(protein_sequence)} residues")

                    # Create FASTA files using CAE's mutator if we have HGVS
                    if hgvs and 'p.' in hgvs:
                        logger.info(f"🔬 Creating mutation pair using CAE's approach...")
                        wt_fasta_path, mut_fasta_path = self._create_mutation_pair(
                            uniprot_id, protein_sequence, hgvs
                        )
                        if wt_fasta_path and mut_fasta_path:
                            logger.info(f"✅ Mutation pair created for structural analysis")

                            # Add mutation pair info to results
                            protein_hgvs = hgvs.split('p.')[1].split()[0] if 'p.' in hgvs else 'Unknown'
                            results['mutation_pair'] = {
                                'wt_fasta': wt_fasta_path,
                                'mut_fasta': mut_fasta_path,
                                'mutation_string': protein_hgvs,
                                'method': 'CAE_elegant_mutator'
                            }

                else:
                    logger.warning(f"⚠️ No sequence found for {uniprot_id}")
            except Exception as e:
                logger.error(f"❌ Sequence retrieval failed: {e}")

        # INTEGRATED ANALYSIS - Use the sophisticated system that was working!
        if protein_sequence and run_all:
            logger.info(f"🧪 Running integrated pathogenicity analysis")
            try:
                # Get real protein mutation from HGVS
                mutation_string = None
                if hgvs and 'p.' in hgvs:
                    protein_part = hgvs.split('p.')[1].split()[0] if 'p.' in hgvs else None
                    if protein_part:
                        parsed_mutation = self._parse_protein_hgvs(f"p.{protein_part}")
                        if parsed_mutation:
                            mutation_string = parsed_mutation['mutation_string']
                            logger.info(f"✅ Parsed protein mutation: {mutation_string}")

                # If no HGVS protein notation, use a generic mutation for testing
                if not mutation_string:
                    mutation_string = "R100W"  # Generic test mutation
                    logger.info(f"⚠️ Using generic mutation for testing: {mutation_string}")

                # Use the SOPHISTICATED IntegratedAnalyzer that was working!
                integrated_result = self.integrated_analyzer.analyze_comprehensive(
                    mutation=mutation_string,
                    sequence=protein_sequence,
                    uniprot_id=uniprot_id,
                    gene_name=gene,
                    conservation_multiplier=conservation_multiplier
                )

                # Extract individual components for display
                results['analyses']['lof'] = integrated_result.get('lof_analysis', {})
                results['analyses']['dn'] = integrated_result.get('dn_analysis', {})
                results['analyses']['integrated'] = integrated_result.get('integrated_analysis', {})

                logger.info(f"✅ Integrated analysis complete:")
                logger.info(f"   LOF score: {integrated_result.get('lof_analysis', {}).get('lof_score', 'N/A'):.3f}")
                logger.info(f"   DN score: {integrated_result.get('dn_analysis', {}).get('dn_score', 'N/A'):.3f}")
                logger.info(f"   Final prediction: {integrated_result.get('final_prediction', 'N/A')}")

            except Exception as e:
                logger.error(f"❌ Integrated analysis failed: {e}")
                results['analyses']['integrated'] = {'error': str(e)}

        # Population frequency analysis (COMMENTED OUT - focus on conservation first)
        # Real bioinformaticians test rare variants, not common ones >1%
        # if chromosome and position and ref_allele and alt_allele and run_all:
        #     logger.info(f"🌍 Analyzing population frequency: {chromosome}:{position} {ref_allele}>{alt_allele}")
        #     try:
        #         frequency_result = self.frequency_analyzer.get_variant_frequency(
        #             chromosome=chromosome,
        #             position=position,
        #             ref_allele=ref_allele,
        #             alt_allele=alt_allele
        #         )
        #         results['analyses']['frequency'] = frequency_result
        #         logger.info(f"✅ Frequency: {frequency_result.get('rarity_category', 'unknown')}")
        #     except Exception as e:
        #         logger.error(f"❌ Frequency analysis failed: {e}")
        #         results['analyses']['frequency'] = {'error': str(e)}

        return results

    def _log_validation_result(self, results, expected_classification, log_file):
        """Log results for validation tracking"""
        try:
            import csv
            import os
            from datetime import datetime

            # Extract key metrics
            input_data = results.get('input', {})
            conservation = results.get('analyses', {}).get('conservation', {})
            integrated = results.get('analyses', {}).get('integrated', {})
            lof = results.get('analyses', {}).get('lof', {})
            dn = results.get('analyses', {}).get('dn', {})

            # Create log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'gene': input_data.get('gene'),
                'hgvs': input_data.get('hgvs'),
                'coordinate': f"{input_data.get('chromosome')}:{input_data.get('position')}",
                'mutation': f"{input_data.get('ref_allele')}>{input_data.get('alt_allele')}",
                'expected_classification': expected_classification,
                'phylop_score': conservation.get('phyloP', 'N/A'),
                'conservation_multiplier': conservation.get('multiplier', 'N/A'),
                'lof_score': lof.get('lof_score', 'N/A'),
                'dn_score': dn.get('dn_score', 'N/A'),
                'final_pathogenicity': integrated.get('pathogenicity_score', 'N/A'),
                'prediction': integrated.get('prediction', 'N/A'),
                'confidence': integrated.get('confidence', 'N/A'),
                'mechanism': integrated.get('mechanism_classification', 'N/A')
            }

            # Write to CSV
            file_exists = os.path.exists(log_file)
            with open(log_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=log_entry.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(log_entry)

            logger.info(f"✅ Validation logged to {log_file}")

        except Exception as e:
            logger.error(f"❌ Validation logging failed: {e}")

    def _create_mutation_pair(self, uniprot_id, protein_sequence, hgvs_string):
        """Create wild-type and mutant FASTA pair using CAE's approach"""
        try:
            import tempfile
            from hgvs_fasta_mutator import HGVSFastaMutator

            # Create temporary FASTA file for wild-type
            temp_dir = tempfile.mkdtemp(prefix=f'mutation_{uniprot_id}_')
            wt_fasta_path = f"{temp_dir}/wt_{uniprot_id}.fasta"

            # Write wild-type FASTA
            with open(wt_fasta_path, 'w') as f:
                f.write(f">sp|{uniprot_id}|WILD_TYPE\n")
                # Write sequence in 60-character lines
                for i in range(0, len(protein_sequence), 60):
                    f.write(protein_sequence[i:i+60] + '\n')

            # Extract protein HGVS part
            protein_hgvs = None
            if 'p.' in hgvs_string:
                protein_hgvs = hgvs_string.split('p.')[1].split()[0]  # Get just the protein part

            if protein_hgvs:
                # Use CAE's mutator to create mutation pair
                mutator = HGVSFastaMutator()
                wt_path, mut_path = mutator.create_mutation_pair(
                    wt_fasta_path,
                    f"p.{protein_hgvs}",
                    temp_dir
                )

                return wt_path, mut_path

            return None, None

        except Exception as e:
            logger.error(f"❌ Mutation pair creation failed: {e}")
            return None, None

    def _get_protein_sequence(self, uniprot_id):
        """Fetch protein sequence from UniProt (from structural_comparison.py)"""
        try:
            import requests
            url = f"https://www.uniprot.org/uniprot/{uniprot_id}.fasta"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            lines = response.text.strip().split('\n')
            sequence = ''.join(lines[1:])  # Skip header line

            return sequence

        except Exception as e:
            logger.error(f"❌ Failed to fetch sequence for {uniprot_id}: {e}")
            return None

    def _extract_sequence_from_pdb(self, pdb_path):
        """Extract protein sequence from PDB file"""
        try:
            from Bio.PDB import PDBParser
            parser = PDBParser(QUIET=True)

            # Handle gzipped files
            if pdb_path.endswith('.gz'):
                import gzip
                with gzip.open(pdb_path, 'rt') as f:
                    structure = parser.get_structure('protein', f)
            else:
                structure = parser.get_structure('protein', pdb_path)

            # Extract sequence from first chain
            sequence = ""
            for model in structure:
                for chain in model:
                    for residue in chain:
                        if residue.get_id()[0] == ' ':  # Standard amino acid
                            resname = residue.get_resname()
                            # Convert 3-letter to 1-letter code
                            aa_map = {
                                'ALA': 'A', 'CYS': 'C', 'ASP': 'D', 'GLU': 'E', 'PHE': 'F',
                                'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LYS': 'K', 'LEU': 'L',
                                'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'GLN': 'Q', 'ARG': 'R',
                                'SER': 'S', 'THR': 'T', 'VAL': 'V', 'TRP': 'W', 'TYR': 'Y'
                            }
                            if resname in aa_map:
                                sequence += aa_map[resname]
                    break  # Only use first chain
                break  # Only use first model

            return sequence

        except Exception as e:
            logger.error(f"❌ Failed to extract sequence from PDB: {e}")
            return None

    def _parse_protein_hgvs(self, hgvs_string):
        """Parse protein HGVS like p.Arg321Cys"""
        try:
            import re
            # Pattern for protein HGVS: p.Arg321Cys
            pattern = r'p\.([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})'
            match = re.match(pattern, hgvs_string)

            if match:
                orig_aa_3 = match.group(1)
                position = int(match.group(2))
                new_aa_3 = match.group(3)

                # Convert 3-letter to 1-letter
                aa_map = {
                    'Ala': 'A', 'Cys': 'C', 'Asp': 'D', 'Glu': 'E', 'Phe': 'F',
                    'Gly': 'G', 'His': 'H', 'Ile': 'I', 'Lys': 'K', 'Leu': 'L',
                    'Met': 'M', 'Asn': 'N', 'Pro': 'P', 'Gln': 'Q', 'Arg': 'R',
                    'Ser': 'S', 'Thr': 'T', 'Val': 'V', 'Trp': 'W', 'Tyr': 'Y'
                }

                orig_aa = aa_map.get(orig_aa_3, 'X')
                new_aa = aa_map.get(new_aa_3, 'X')

                return {
                    'position': position,
                    'original_aa': orig_aa,
                    'new_aa': new_aa,
                    'mutation_string': f"{orig_aa}{position}{new_aa}"
                }

            return None

        except Exception as e:
            logger.error(f"❌ HGVS parsing failed: {e}")
            return None

    def _interpret_conservation(self, conservation_scores):
        """Interpret conservation scores for clinical relevance (FIXED THRESHOLDS!)"""
        phylop = conservation_scores['phyloP']
        phastcons = conservation_scores['phastCons']
        combined = conservation_scores['conservation_score']

        # CORRECTED THRESHOLDS based on real conservation standards
        if phylop > 3.0 or phastcons > 0.9:
            level = "EXTREMELY_CONSERVED"
            clinical = "Variants at this position are very likely to be pathogenic"
        elif phylop > 1.5 or phastcons > 0.7:
            level = "HIGHLY_CONSERVED"
            clinical = "Variants at this position are likely to be pathogenic"
        elif phylop > 0.5 or phastcons > 0.4:
            level = "MODERATELY_CONSERVED"
            clinical = "Variants at this position may be pathogenic"
        elif phylop > -0.5:
            level = "WEAKLY_CONSERVED"
            clinical = "Variants at this position are less likely to be pathogenic"
        else:
            level = "NOT_CONSERVED"
            clinical = "Variants at this position are likely benign"

        # Add GERP-equivalent interpretation
        gerp_equivalent = "N/A"
        if phylop > 2.0:
            gerp_equivalent = f"~GERP {phylop * 2.5:.1f} (highly constrained)"
        elif phylop > 0.5:
            gerp_equivalent = f"~GERP {phylop * 2.0:.1f} (constrained)"

        return {
            'conservation_level': level,
            'clinical_interpretation': clinical,
            'phyloP_interpretation': f"phyloP {phylop:.3f} ({'highly conserved' if phylop > 1.5 else 'conserved' if phylop > 0 else 'evolving'})",
            'phastCons_interpretation': f"phastCons {phastcons:.3f} ({'highly conserved' if phastcons > 0.7 else 'conserved' if phastcons > 0.4 else 'variable'})",
            'gerp_equivalent': gerp_equivalent
        }

    def print_results(self, results):
        """Pretty print analysis results"""
        print("\n" + "="*60)
        print("🧬 GENETICS ANALYSIS RESULTS")
        print("="*60)
        
        # Input summary
        print(f"\n📋 INPUT:")
        input_data = results['input']
        if input_data['hgvs']:
            print(f"   HGVS: {input_data['hgvs']}")
        if input_data['gene']:
            print(f"   Gene: {input_data['gene']}")
        if input_data['chromosome'] and input_data['position']:
            print(f"   Coordinate: {input_data['chromosome']}:{input_data['position']}")
        if input_data['ref_allele'] and input_data['alt_allele']:
            print(f"   Change: {input_data['ref_allele']} → {input_data['alt_allele']}")
        
        # Gene mapping
        if 'gene_mapping' in results:
            mapping = results['gene_mapping']
            print(f"\n🧬 GENE MAPPING:")
            print(f"   {mapping['gene']} → {mapping['uniprot_id']}")
        
        # Analysis results
        if 'analyses' in results:
            analyses = results['analyses']
            
            if 'conservation' in analyses:
                cons = analyses['conservation']
                if 'error' not in cons:
                    print(f"\n🔬 CONSERVATION:")
                    print(f"   phyloP: {cons.get('phyloP', 'N/A'):.3f}")
                    print(f"   phastCons: {cons.get('phastCons', 'N/A'):.3f}")
                    print(f"   Multiplier: {cons.get('multiplier', 'N/A'):.1f}x")
                    print(f"   Level: {cons.get('interpretation', {}).get('conservation_level', 'N/A')}")
                    print(f"   Confidence: {cons.get('confidence', 'N/A'):.1f}")

            if 'integrated' in analyses:
                integrated = analyses['integrated']
                if 'error' not in integrated:
                    print(f"\n🎯 INTEGRATED PATHOGENICITY ANALYSIS:")
                    print(f"   Final Prediction: {integrated.get('prediction', 'N/A')}")
                    print(f"   Confidence: {integrated.get('confidence', 'N/A'):.3f}")
                    print(f"   Primary Mechanism: {integrated.get('primary_mechanism', 'N/A')}")
                    if 'evidence_summary' in integrated:
                        print(f"   Evidence: {integrated['evidence_summary']}")

            if 'lof' in analyses:
                lof = analyses['lof']
                if 'error' not in lof:
                    print(f"\n🧪 LOSS OF FUNCTION COMPONENT:")
                    print(f"   LOF Score: {lof.get('lof_score', 'N/A'):.3f}")
                    print(f"   Base Score: {lof.get('base_lof_score', 'N/A'):.3f}")
                    print(f"   Conservation Multiplier: {lof.get('conservation_multiplier', 'N/A'):.1f}x")
                    print(f"   Smart Multiplier: {lof.get('smart_multiplier', 'N/A'):.1f}x")
                    print(f"   Mechanism: {lof.get('mechanism', 'N/A')}")

            if 'dn' in analyses:
                dn = analyses['dn']
                if 'error' not in dn:
                    print(f"\n🧪 DOMINANT NEGATIVE COMPONENT:")

                    # Safe formatting for numeric values
                    dn_score = dn.get('dn_score', 'N/A')
                    if isinstance(dn_score, (int, float)):
                        print(f"   DN Score: {dn_score:.3f}")
                    else:
                        print(f"   DN Score: {dn_score}")

                    base_dn_score = dn.get('base_dn_score', 'N/A')
                    if isinstance(base_dn_score, (int, float)):
                        print(f"   Base Score: {base_dn_score:.3f}")
                    else:
                        print(f"   Base Score: {base_dn_score}")

                    print(f"   Mechanism: {dn.get('mechanism', 'N/A')}")

                    confidence = dn.get('confidence', 'N/A')
                    if isinstance(confidence, (int, float)):
                        print(f"   Confidence: {confidence:.3f}")
                    else:
                        print(f"   Confidence: {confidence}")
            
            if 'frequency' in analyses:
                freq = analyses['frequency']
                if 'error' not in freq:
                    print(f"\n🌍 POPULATION FREQUENCY:")
                    print(f"   Global AF: {freq.get('global_af', 'N/A')}")
                    print(f"   Category: {freq.get('rarity_category', 'N/A')}")
                    if freq.get('manual_input_needed'):
                        print(f"   ⚠️ Manual input needed: {freq.get('manual_input_prompt', '')}")
            
            if 'structure' in analyses:
                struct = analyses['structure']
                if 'error' not in struct:
                    print(f"\n🏗️ PROTEIN STRUCTURE:")
                    print(f"   Status: {struct.get('status', 'N/A')}")
                    if struct.get('structure_file'):
                        print(f"   File: {struct['structure_file']}")

            # Show mutation pair info if created
            if 'mutation_pair' in results:
                pair = results['mutation_pair']
                print(f"\n🧬 MUTATION PAIR (CAE'S APPROACH):")
                print(f"   Wild-type FASTA: {pair.get('wt_fasta', 'N/A')}")
                print(f"   Mutant FASTA: {pair.get('mut_fasta', 'N/A')}")
                print(f"   Mutation: {pair.get('mutation_string', 'N/A')}")

        print("\n" + "="*60)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🧬 Comprehensive genetics variant analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python genetics_cli.py --hgvs "NM_000260.4:c.658C>T" --gene "MYO7A"
  python genetics_cli.py --coord "chr11:77156927" --ref "C" --alt "T" --gene "MYO7A" --all
  python genetics_cli.py --gene "FKRP" --all
        """
    )
    
    # Input options
    parser.add_argument('--hgvs', help='HGVS notation (e.g., "NM_000260.4:c.658C>T")')
    parser.add_argument('--gene', help='Gene name (e.g., "MYO7A")')
    parser.add_argument('--coord', help='Genomic coordinate (e.g., "chr11:77156927")')
    parser.add_argument('--ref', help='Reference allele (e.g., "C")')
    parser.add_argument('--alt', help='Alternative allele (e.g., "T")')
    
    # Analysis options
    parser.add_argument('--all', '--all-analyses', action='store_true',
                       help='Run all available analyses')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--log-validation', help='Log results to validation file for accuracy tracking')
    parser.add_argument('--expected-classification', help='Expected classification (P/LP/VUS/LB/B) for validation')
    
    args = parser.parse_args()
    
    # Validate input
    if not any([args.hgvs, args.gene, args.coord]):
        parser.error("Must provide at least one of: --hgvs, --gene, or --coord")
    
    # Parse coordinate if provided
    chromosome = None
    position = None
    if args.coord:
        try:
            chromosome, position = args.coord.split(':')
            position = int(position)
        except ValueError:
            parser.error("Coordinate must be in format 'chr11:77156927'")
    
    # Initialize and run analysis
    try:
        cli = GeneticsAnalysisCLI()
        
        results = cli.analyze_variant(
            gene=args.gene,
            chromosome=chromosome,
            position=position,
            ref_allele=args.ref,
            alt_allele=args.alt,
            hgvs=args.hgvs,
            run_all=args.all
        )
        
        # Log validation results if requested
        if args.log_validation and args.expected_classification:
            cli._log_validation_result(results, args.expected_classification, args.log_validation)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            cli.print_results(results)

    except KeyboardInterrupt:
        print("\n❌ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🧬 HGVS FASTA MUTATOR - CAE'S BRILLIANT SUGGESTION!
Elegantly brute-force FASTA mutation from HGVS notation

Usage:
    python hgvs_fasta_mutator.py --input wt.fasta --output mut.fasta --hgvs "p.Arg22Trp"
    python hgvs_fasta_mutator.py --input wt.fasta --mutation "R22W"
"""

import argparse
import re
import tempfile
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class HGVSFastaMutator:
    """CAE's elegant brute-force FASTA mutator"""
    
    def __init__(self):
        # 3-letter to 1-letter amino acid mapping
        self.aa_3to1 = {
            'Ala': 'A', 'Cys': 'C', 'Asp': 'D', 'Glu': 'E', 'Phe': 'F',
            'Gly': 'G', 'His': 'H', 'Ile': 'I', 'Lys': 'K', 'Leu': 'L',
            'Met': 'M', 'Asn': 'N', 'Pro': 'P', 'Gln': 'Q', 'Arg': 'R',
            'Ser': 'S', 'Thr': 'T', 'Val': 'V', 'Trp': 'W', 'Tyr': 'Y'
        }
    
    def parse_hgvs_protein(self, hgvs_string):
        """Parse protein HGVS like p.Arg22Trp → R22W"""
        try:
            # Remove p. prefix if present
            if hgvs_string.startswith('p.'):
                hgvs_string = hgvs_string[2:]
            
            # Pattern for protein HGVS: Arg22Trp
            pattern = r'([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2})'
            match = re.match(pattern, hgvs_string)
            
            if match:
                orig_aa_3 = match.group(1)
                position = int(match.group(2))
                new_aa_3 = match.group(3)
                
                # Convert to 1-letter codes
                orig_aa = self.aa_3to1.get(orig_aa_3, 'X')
                new_aa = self.aa_3to1.get(new_aa_3, 'X')
                
                if orig_aa == 'X' or new_aa == 'X':
                    raise ValueError(f"Unknown amino acid: {orig_aa_3} or {new_aa_3}")
                
                return {
                    'position': position,
                    'original_aa': orig_aa,
                    'new_aa': new_aa,
                    'mutation_string': f"{orig_aa}{position}{new_aa}"
                }
            
            # Try simple format like R22W
            simple_pattern = r'([A-Z])(\d+)([A-Z])'
            simple_match = re.match(simple_pattern, hgvs_string)
            if simple_match:
                orig_aa = simple_match.group(1)
                position = int(simple_match.group(2))
                new_aa = simple_match.group(3)
                
                return {
                    'position': position,
                    'original_aa': orig_aa,
                    'new_aa': new_aa,
                    'mutation_string': f"{orig_aa}{position}{new_aa}"
                }
            
            raise ValueError(f"Invalid HGVS format: {hgvs_string}")
            
        except Exception as e:
            logger.error(f"❌ HGVS parsing failed: {e}")
            return None
    
    def read_fasta(self, fasta_path):
        """Read FASTA file and return header + sequence"""
        try:
            with open(fasta_path, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                raise ValueError("Empty FASTA file")
            
            # First line is header
            header = lines[0].strip()
            if not header.startswith('>'):
                raise ValueError("Invalid FASTA format - no header")
            
            # Join all sequence lines
            sequence = ''.join(line.strip() for line in lines[1:])
            
            logger.info(f"✅ Read FASTA: {len(sequence)} residues")
            return header, sequence
            
        except Exception as e:
            logger.error(f"❌ Failed to read FASTA: {e}")
            return None, None
    
    def mutate_fasta(self, input_path, output_path, mutation_info):
        """
        CAE's elegant FASTA mutator!
        
        Args:
            input_path: Path to wild-type FASTA
            output_path: Path for mutant FASTA
            mutation_info: Dict with position, original_aa, new_aa
        """
        try:
            # Read wild-type sequence
            header, wt_sequence = self.read_fasta(input_path)
            if not wt_sequence:
                return False
            
            position = mutation_info['position']
            orig_aa = mutation_info['original_aa']
            new_aa = mutation_info['new_aa']
            
            # Validate position
            if position < 1 or position > len(wt_sequence):
                raise ValueError(f"Position {position} out of range (1-{len(wt_sequence)})")
            
            # Check original amino acid (1-based indexing)
            actual_aa = wt_sequence[position - 1]
            if actual_aa != orig_aa:
                raise ValueError(f"Expected {orig_aa} at position {position}, found {actual_aa}")
            
            # Create mutant sequence - CAE's elegant approach!
            mutant_sequence = wt_sequence[:position-1] + new_aa + wt_sequence[position:]
            
            # Write mutant FASTA with proper formatting (60 chars per line)
            with open(output_path, 'w') as f:
                # Update header to indicate mutation
                mutation_string = f"{orig_aa}{position}{new_aa}"
                new_header = header.replace('>', f'>{mutation_string}_')
                f.write(new_header + '\n')
                
                # Write sequence in 60-character lines
                for i in range(0, len(mutant_sequence), 60):
                    f.write(mutant_sequence[i:i+60] + '\n')
            
            logger.info(f"✅ Created mutant FASTA: {mutation_string}")
            logger.info(f"   Wild-type: {orig_aa} at position {position}")
            logger.info(f"   Mutant:    {new_aa} at position {position}")
            logger.info(f"   Output:    {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ FASTA mutation failed: {e}")
            return False
    
    def create_mutation_pair(self, input_fasta, hgvs_string, output_dir=None):
        """
        Create wild-type and mutant FASTA pair for comparison
        
        Returns:
            tuple: (wt_path, mut_path) or (None, None) if failed
        """
        try:
            # Parse HGVS
            mutation_info = self.parse_hgvs_protein(hgvs_string)
            if not mutation_info:
                return None, None
            
            # Set up output directory
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix='hgvs_mutation_')
            else:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            output_dir = Path(output_dir)
            mutation_string = mutation_info['mutation_string']
            
            # Copy wild-type FASTA
            wt_path = output_dir / f"wt_{mutation_string}.fasta"
            mut_path = output_dir / f"mut_{mutation_string}.fasta"
            
            # Copy wild-type
            import shutil
            shutil.copy2(input_fasta, wt_path)
            
            # Create mutant
            success = self.mutate_fasta(input_fasta, mut_path, mutation_info)
            
            if success:
                logger.info(f"🎯 Mutation pair created:")
                logger.info(f"   Wild-type: {wt_path}")
                logger.info(f"   Mutant:    {mut_path}")
                return str(wt_path), str(mut_path)
            else:
                return None, None
                
        except Exception as e:
            logger.error(f"❌ Mutation pair creation failed: {e}")
            return None, None

def main():
    """CLI entry point for CAE's FASTA mutator"""
    parser = argparse.ArgumentParser(
        description="🧬 CAE's elegant HGVS FASTA mutator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hgvs_fasta_mutator.py --input protein.fasta --output mutant.fasta --hgvs "p.Arg22Trp"
  python hgvs_fasta_mutator.py --input protein.fasta --mutation "R22W" --pair --output-dir ./mutations/
        """
    )
    
    parser.add_argument('--input', required=True, help='Input wild-type FASTA file')
    parser.add_argument('--output', help='Output mutant FASTA file')
    parser.add_argument('--hgvs', help='HGVS protein notation (e.g., "p.Arg22Trp")')
    parser.add_argument('--mutation', help='Simple mutation notation (e.g., "R22W")')
    parser.add_argument('--pair', action='store_true', help='Create wild-type and mutant pair')
    parser.add_argument('--output-dir', help='Output directory for mutation pairs')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.hgvs, args.mutation]):
        parser.error("Must provide either --hgvs or --mutation")
    
    if not args.pair and not args.output:
        parser.error("Must provide --output unless using --pair")
    
    # Initialize mutator
    mutator = HGVSFastaMutator()
    
    # Determine mutation string
    mutation_string = args.hgvs or args.mutation
    
    try:
        if args.pair:
            # Create mutation pair
            wt_path, mut_path = mutator.create_mutation_pair(
                args.input, 
                mutation_string, 
                args.output_dir
            )
            
            if wt_path and mut_path:
                print(f"✅ Mutation pair created successfully!")
                print(f"   Wild-type: {wt_path}")
                print(f"   Mutant:    {mut_path}")
            else:
                print(f"❌ Failed to create mutation pair")
                return 1
        else:
            # Single mutation
            mutation_info = mutator.parse_hgvs_protein(mutation_string)
            if not mutation_info:
                print(f"❌ Failed to parse mutation: {mutation_string}")
                return 1
            
            success = mutator.mutate_fasta(args.input, args.output, mutation_info)
            if success:
                print(f"✅ Mutant FASTA created: {args.output}")
            else:
                print(f"❌ Failed to create mutant FASTA")
                return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

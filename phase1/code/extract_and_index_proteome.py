#!/usr/bin/env python3
"""
🧬 PROTEOME EXTRACTOR AND INDEXER
Extract the human proteome tar and create a gene name index for fast lookups
"""

import tarfile
import os
import json
import re
from pathlib import Path
import logging

def extract_proteome(tar_path, extract_dir):
    """Extract the proteome tar file"""
    print(f"🔓 Extracting {tar_path} to {extract_dir}...")
    
    with tarfile.open(tar_path, 'r') as tar:
        tar.extractall(extract_dir)
    
    print(f"✅ Extraction complete!")

def create_gene_index(proteome_dir):
    """
    Create an index mapping gene names to PDB files
    AlphaFold files are named like: AF-P12345-F1-model_v4.pdb
    We need to map gene names to these files
    """
    print(f"📚 Creating gene name index...")
    
    proteome_path = Path(proteome_dir)
    pdb_files = list(proteome_path.glob("*.pdb.gz"))

    print(f"📁 Found {len(pdb_files)} PDB files (gzipped)")
    
    # For now, create a simple mapping
    # In a real implementation, we'd use UniProt API to map gene names to UniProt IDs
    gene_index = {}
    
    # Extract UniProt IDs from filenames
    for pdb_file in pdb_files:
        filename = pdb_file.name
        # Extract UniProt ID from AF-P12345-F1-model_v4.pdb.gz
        match = re.match(r'AF-([A-Z0-9]+)-F1-model_v4\.pdb\.gz', filename)
        if match:
            uniprot_id = match.group(1)
            gene_index[uniprot_id] = str(pdb_file)
    
    # Save index
    index_file = proteome_path / "gene_index.json"
    with open(index_file, 'w') as f:
        json.dump(gene_index, f, indent=2)
    
    print(f"✅ Created index with {len(gene_index)} entries")
    print(f"📄 Index saved to: {index_file}")
    
    return gene_index

def main():
    tar_path = "/mnt/Arcana/alphafold_human/UP000005640_9606_HUMAN_v4.tar"
    extract_dir = "/mnt/Arcana/alphafold_human/structures"
    
    if not os.path.exists(tar_path):
        print(f"❌ Tar file not found: {tar_path}")
        print("⏳ Wait for download to complete first!")
        return
    
    # Create extraction directory
    os.makedirs(extract_dir, exist_ok=True)
    
    # Extract
    extract_proteome(tar_path, extract_dir)
    
    # Create index
    create_gene_index(extract_dir)
    
    print(f"🎉 Proteome ready for use!")
    print(f"📁 Structures: {extract_dir}")

if __name__ == "__main__":
    main()

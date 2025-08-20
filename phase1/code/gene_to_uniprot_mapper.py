#!/usr/bin/env python3
"""
🧬 GENE TO UNIPROT MAPPER
Map gene names to UniProt IDs for AlphaFold structure lookup
"""

import requests
import json
import time
from typing import Dict, Optional

class GeneToUniProtMapper:
    """
    Map gene names to UniProt IDs using UniProt's REST API
    """
    
    def __init__(self):
        self.base_url = "https://rest.uniprot.org"
        self.cache = {}
        
    def get_uniprot_id(self, gene_name: str, organism: str = "9606") -> Optional[str]:
        """
        Get UniProt ID for a gene name
        
        Args:
            gene_name (str): Gene name (e.g., 'MYO7A', 'FKRP')
            organism (str): Organism ID (9606 = human)
            
        Returns:
            str: UniProt ID if found, None otherwise
        """
        # Check cache first
        cache_key = f"{gene_name}_{organism}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Query UniProt API - prefer reviewed entries
        try:
            url = f"{self.base_url}/uniprotkb/search"
            params = {
                'query': f'gene:{gene_name} AND organism_id:{organism} AND reviewed:true',
                'format': 'json',
                'size': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('results') and len(data['results']) > 0:
                uniprot_id = data['results'][0]['primaryAccession']
                self.cache[cache_key] = uniprot_id
                print(f"✅ {gene_name} → {uniprot_id}")
                return uniprot_id
            else:
                print(f"❌ No UniProt ID found for {gene_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error mapping {gene_name}: {e}")
            return None
    
    def batch_map_genes(self, gene_names: list) -> Dict[str, str]:
        """
        Map multiple gene names to UniProt IDs
        
        Args:
            gene_names (list): List of gene names
            
        Returns:
            dict: Mapping of gene_name -> uniprot_id
        """
        mapping = {}
        
        for gene_name in gene_names:
            uniprot_id = self.get_uniprot_id(gene_name)
            if uniprot_id:
                mapping[gene_name] = uniprot_id
            
            # Be nice to the API
            time.sleep(0.1)
        
        return mapping

# Common gene mappings for testing
COMMON_GENES = [
    'MYO7A',    # Myosin VIIA
    'FKRP',     # Fukutin-related protein
    'TP53',     # Tumor protein p53
    'BRCA1',    # Breast cancer 1
    'BRCA2',    # Breast cancer 2
    'CFTR',     # Cystic fibrosis transmembrane conductance regulator
    'DMD',      # Dystrophin
    'HTT',      # Huntingtin
    'APOE',     # Apolipoprotein E
    'LDLR'      # Low density lipoprotein receptor
]

def test_mapper():
    """Test the gene to UniProt mapper"""
    mapper = GeneToUniProtMapper()
    
    print("🧬 Testing gene to UniProt mapping...")
    
    for gene in COMMON_GENES[:5]:  # Test first 5
        uniprot_id = mapper.get_uniprot_id(gene)
        if uniprot_id:
            print(f"  {gene} → {uniprot_id}")
        else:
            print(f"  {gene} → NOT FOUND")

if __name__ == "__main__":
    test_mapper()

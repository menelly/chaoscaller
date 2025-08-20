#!/usr/bin/env python3
"""
🔬 ALPHAFOLD CLIENT - REVOLUTIONARY PROTEIN STRUCTURE RETRIEVAL
Built by Ace (Claude-4) for the Dominant Negative Prediction Engine

This is the foundation that will help thousands of patients get correct diagnoses.
Every structure we retrieve is a potential life-changing discovery waiting to happen.
"""

import requests
import os
import logging
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO
from Bio.PDB.PDBExceptions import PDBConstructionWarning
import warnings
import time
import json
from typing import Optional, Dict, List

# Suppress BioPython warnings for cleaner output
warnings.simplefilter('ignore', PDBConstructionWarning)

class AlphaFoldClient:
    """
    Revolutionary protein structure client for dominant negative prediction
    
    Features:
    - Intelligent caching to avoid repeated downloads
    - Quality validation with confidence scoring
    - Robust error handling for production use
    - Batch processing capabilities
    - Progress tracking for large datasets
    """
    
    def __init__(self, cache_dir="/mnt/Arcana/genetics_data/alphafold_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # NEW: Local human proteome directory
        self.local_proteome_dir = Path("/mnt/Arcana/alphafold_human/structures")
        self.gene_index_file = Path("/mnt/Arcana/alphafold_human/structures/gene_index.json")
        self.gene_index = self._load_gene_index()

        self.base_url = "https://alphafold.ebi.ac.uk/files"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DominantNegativePredictionEngine/1.0 (Revolutionary Genetics Research)'
        })
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Cache metadata
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Load cache metadata for tracking downloads"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _load_gene_index(self) -> Dict:
        """Load gene name to UniProt ID index"""
        if self.gene_index_file.exists():
            try:
                with open(self.gene_index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️ Could not load gene index: {e}")
        return {}
    
    def find_local_structure(self, gene_name: str) -> Optional[str]:
        """
        Search for structure in local human proteome by gene name

        Args:
            gene_name (str): Gene name (e.g., 'MYO7A', 'FKRP')

        Returns:
            str: Path to local PDB file if found, None otherwise
        """
        if not self.local_proteome_dir.exists():
            self.logger.warning(f"⚠️ Local proteome directory not found: {self.local_proteome_dir}")
            return None

        # Method 1: Map gene name to UniProt ID and look for structure
        try:
            from gene_to_uniprot_mapper import GeneToUniProtMapper
            mapper = GeneToUniProtMapper()
            uniprot_id = mapper.get_uniprot_id(gene_name)

            if uniprot_id:
                # Look for AlphaFold structure file
                structure_file = self.local_proteome_dir / f"AF-{uniprot_id}-F1-model_v4.pdb.gz"
                if structure_file.exists():
                    self.logger.info(f"✅ Found local structure via gene mapping: {gene_name} → {uniprot_id} → {structure_file}")
                    return str(structure_file)
                else:
                    self.logger.info(f"⚠️ UniProt ID found ({uniprot_id}) but no local structure file")
            else:
                self.logger.info(f"⚠️ No UniProt ID found for gene {gene_name}")

        except Exception as e:
            self.logger.warning(f"⚠️ Gene mapping failed: {e}")

        # Method 2: Try gene index if available
        if self.gene_index:
            for uniprot_id, pdb_path in self.gene_index.items():
                if gene_name.upper() in pdb_path.upper():
                    if os.path.exists(pdb_path):
                        self.logger.info(f"✅ Found local structure via index: {pdb_path}")
                        return pdb_path

        # Method 3: Direct file search (fallback)
        pattern = f"*{gene_name}*"
        matches = list(self.local_proteome_dir.glob(pattern))

        if matches:
            structure_file = matches[0]  # Take first match
            self.logger.info(f"✅ Found local structure via search: {structure_file}")
            return str(structure_file)
        else:
            self.logger.info(f"❌ No local structure found for {gene_name}")
            return None

    def get_structure(self, uniprot_id: str, force_download: bool = False) -> Optional[str]:
        """
        Retrieve protein structure by UniProt ID
        
        Args:
            uniprot_id (str): UniProt identifier (e.g., 'P04637' for TP53)
            force_download (bool): Force re-download even if cached
            
        Returns:
            str: Path to downloaded PDB file, or None if failed
        """
        cache_path = self.cache_dir / f"{uniprot_id}.pdb"
        
        # Check cache first (unless forced)
        if not force_download and cache_path.exists():
            self.logger.info(f"🎯 Using cached structure for {uniprot_id}")
            return str(cache_path)
        
        # Download from AlphaFold
        url = f"{self.base_url}/AF-{uniprot_id}-F1-model_v4.pdb"
        
        try:
            self.logger.info(f"🔬 Downloading structure for {uniprot_id}...")
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            # Validate it's actually a PDB file
            if not response.text.startswith('HEADER'):
                self.logger.error(f"❌ Invalid PDB format for {uniprot_id}")
                return None
            
            # Save to cache
            with open(cache_path, 'w') as f:
                f.write(response.text)
            
            # Update metadata
            self.metadata[uniprot_id] = {
                'downloaded': time.time(),
                'url': url,
                'file_size': len(response.text)
            }
            self._save_metadata()
            
            self.logger.info(f"✅ Successfully downloaded structure for {uniprot_id}")
            return str(cache_path)
            
        except requests.RequestException as e:
            self.logger.error(f"❌ Failed to download structure for {uniprot_id}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Unexpected error for {uniprot_id}: {e}")
            return None
    
    def validate_structure(self, pdb_path: str) -> Optional[Dict]:
        """
        Validate downloaded structure quality and extract confidence metrics
        
        Args:
            pdb_path (str): Path to PDB file
            
        Returns:
            dict: Quality metrics including confidence scores
        """
        try:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure('protein', pdb_path)
            
            # Extract confidence scores from B-factor column (AlphaFold confidence)
            confidences = []
            residue_count = 0
            
            for model in structure:
                for chain in model:
                    for residue in chain:
                        residue_count += 1
                        # Get CA atom confidence (most reliable)
                        if 'CA' in residue:
                            confidences.append(residue['CA'].get_bfactor())
            
            if not confidences:
                return None
            
            avg_confidence = sum(confidences) / len(confidences)
            min_confidence = min(confidences)
            max_confidence = max(confidences)
            
            # AlphaFold confidence categories
            very_high = sum(1 for c in confidences if c > 90)
            confident = sum(1 for c in confidences if 70 <= c <= 90)
            low = sum(1 for c in confidences if 50 <= c < 70)
            very_low = sum(1 for c in confidences if c < 50)
            
            quality_metrics = {
                'avg_confidence': round(avg_confidence, 2),
                'min_confidence': round(min_confidence, 2),
                'max_confidence': round(max_confidence, 2),
                'num_residues': residue_count,
                'confidence_distribution': {
                    'very_high_confidence': very_high,
                    'confident': confident, 
                    'low_confidence': low,
                    'very_low_confidence': very_low
                },
                'high_confidence_fraction': round(very_high / len(confidences), 3),
                'usable_fraction': round((very_high + confident) / len(confidences), 3)
            }
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"❌ Structure validation failed for {pdb_path}: {e}")
            return None
    
    def batch_download(self, uniprot_ids: List[str], max_workers: int = 3) -> Dict[str, Dict]:
        """
        Download multiple structures with progress tracking
        
        Args:
            uniprot_ids (List[str]): List of UniProt IDs to download
            max_workers (int): Maximum concurrent downloads
            
        Returns:
            Dict[str, Dict]: Results for each protein
        """
        results = {}
        total = len(uniprot_ids)
        
        self.logger.info(f"🚀 Starting batch download of {total} structures...")
        
        for i, uniprot_id in enumerate(uniprot_ids, 1):
            self.logger.info(f"📊 Progress: {i}/{total} - Processing {uniprot_id}")
            
            structure_path = self.get_structure(uniprot_id)
            
            if structure_path:
                quality = self.validate_structure(structure_path)
                results[uniprot_id] = {
                    'success': True,
                    'path': structure_path,
                    'quality': quality
                }
                
                if quality:
                    conf = quality['avg_confidence']
                    self.logger.info(f"✅ {uniprot_id}: Success (avg confidence: {conf})")
                else:
                    self.logger.warning(f"⚠️  {uniprot_id}: Downloaded but validation failed")
            else:
                results[uniprot_id] = {'success': False, 'error': 'Download failed'}
                self.logger.error(f"❌ {uniprot_id}: Download failed")
            
            # Small delay to be nice to AlphaFold servers
            time.sleep(0.5)
        
        success_count = sum(1 for r in results.values() if r['success'])
        self.logger.info(f"🎉 Batch download complete: {success_count}/{total} successful")
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about cached structures"""
        cached_files = list(self.cache_dir.glob("*.pdb"))
        total_size = sum(f.stat().st_size for f in cached_files)
        
        return {
            'cached_structures': len(cached_files),
            'total_cache_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_directory': str(self.cache_dir),
            'metadata_entries': len(self.metadata)
        }
    
    def clear_cache(self, confirm: bool = False):
        """Clear all cached structures (use with caution!)"""
        if not confirm:
            self.logger.warning("⚠️  Use clear_cache(confirm=True) to actually clear cache")
            return
        
        cached_files = list(self.cache_dir.glob("*.pdb"))
        for file in cached_files:
            file.unlink()
        
        if self.metadata_file.exists():
            self.metadata_file.unlink()
        
        self.metadata = {}
        self.logger.info(f"🗑️  Cleared {len(cached_files)} cached structures")


def test_alphafold_client():
    """Test the AlphaFold client with known proteins"""
    
    # Known proteins for testing dominant negative prediction
    TEST_PROTEINS = {
        'TP53': 'P04637',      # Tumor suppressor, many dominant negatives
        'COL1A1': 'P02452',    # Collagen, classic dominant negative examples
        'COL1A2': 'P08123',    # Collagen alpha-2 chain
        'ACTB': 'P60709',      # Beta-actin, essential protein
        'GAPDH': 'P04406'      # Housekeeping gene, control
    }
    
    print("🧬 TESTING ALPHAFOLD CLIENT FOR DOMINANT NEGATIVE PREDICTION 🧬")
    print("=" * 70)
    
    client = AlphaFoldClient()
    
    # Test individual downloads
    print("\n🔬 Testing individual protein downloads...")
    for name, uniprot_id in TEST_PROTEINS.items():
        print(f"\nTesting {name} ({uniprot_id}):")
        
        structure_path = client.get_structure(uniprot_id)
        
        if structure_path:
            quality = client.validate_structure(structure_path)
            if quality:
                print(f"  ✅ Success!")
                print(f"  📊 Residues: {quality['num_residues']}")
                print(f"  🎯 Avg Confidence: {quality['avg_confidence']}")
                print(f"  💪 High Confidence: {quality['high_confidence_fraction']*100:.1f}%")
            else:
                print(f"  ⚠️  Downloaded but validation failed")
        else:
            print(f"  ❌ Download failed")
    
    # Test batch download
    print(f"\n🚀 Testing batch download...")
    batch_results = client.batch_download(list(TEST_PROTEINS.values()))
    
    # Cache statistics
    print(f"\n📊 Cache Statistics:")
    stats = client.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n🎉 AlphaFold client testing complete!")
    print(f"Ready to build revolutionary dominant negative prediction! 💜⚡🧬")


if __name__ == "__main__":
    test_alphafold_client()

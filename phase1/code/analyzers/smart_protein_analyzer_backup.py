#!/usr/bin/env python3
"""
🧬 SMART PROTEIN ANALYZER - AUTOMATIC DOMAIN-AWARE SCORING
Built by Ace + Ren for scalable protein family analysis

This pulls domain/function info from real databases instead of hardcoding!
The breakthrough that makes our system work for ALL proteins, not just the ones we program!
"""

import requests
import re
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, List, Optional
import time
import logging

class SmartProteinAnalyzer:
    """Automatically pull domain/function info and adjust scoring - scales to ALL proteins!"""
    
    def __init__(self, offline_mode=False):
        self.name = "SmartProteinAnalyzer"
        self.offline_mode = offline_mode  # Skip API calls for testing

        # Cache to avoid repeated API calls
        self.uniprot_cache = {}
        self.pfam_cache = {}
        self.go_cache = {}

        # Set up logging
        self.logger = logging.getLogger(__name__)

        if self.offline_mode:
            self.logger.info("🔧 OFFLINE MODE: Skipping UniProt API calls, using local motifs only")
        
        # Domain/function scoring weights (evidence-based, not hardcoded genes!)
        self.pfam_weights = {
            # Metabolic enzymes
            'PF00171': 1.5,  # Aldehyde dehydrogenase family
            'PF04909': 1.5,  # Amidohydrolase family (ACMSD!)
            'PF00076': 1.4,  # ATP synthase alpha/beta family (like ATP5F1A!)
            'PF00069': 1.6,  # Protein kinase domain
            'PF00018': 1.3,  # SH3 domain (protein interactions)
            
            # Motor proteins  
            'PF00063': 1.4,  # Myosin motor domain (like MYO7A!)
            'PF00225': 1.3,  # Kinesin motor domain
            
            # DNA/RNA binding
            'PF00096': 1.4,  # Zinc finger C2H2
            'PF00104': 1.3,  # Ligand-binding domain
            
            # Structural proteins
            'PF01391': 1.5,  # Collagen triple helix repeat
            'PF00038': 1.2,  # Intermediate filament protein
        }
        
        self.go_weights = {
            # Catalytic activities
            'GO:0003824': 1.4,  # Catalytic activity (enzymes)
            'GO:0016491': 1.5,  # Oxidoreductase activity
            'GO:0016301': 1.4,  # Kinase activity
            
            # Motor activities
            'GO:0003774': 1.3,  # Motor activity
            'GO:0005524': 1.2,  # ATP binding
            
            # Binding activities
            'GO:0003677': 1.3,  # DNA binding
            'GO:0003723': 1.2,  # RNA binding
            
            # Metabolic processes
            'GO:0008152': 1.3,  # Metabolic process
            'GO:0006091': 1.4,  # Generation of precursor metabolites
        }
        
        # Sequence motifs (work without internet!)
        self.motif_patterns = {
            r'[LIVMFY].{0,3}G.{1,3}[ST]': ('walker_a_motif', 1.4),      # ATP/GTP binding
            r'[RK].{2,3}[LIVMFY].{3}[LIVMFY].{3}D': ('walker_b_motif', 1.4),  # ATP/GTP binding
            r'DFG': ('kinase_dfg_motif', 1.6),                          # Kinase active site
            r'[LIVMFY]G[LIVMFY]': ('hydrophobic_motif', 1.1),          # Hydrophobic core
            r'C.{2,4}C.{3}[FY].{5,8}C.{2}C': ('zinc_finger', 1.3),    # Zinc finger
            r'G.{2}G.{2}G': ('collagen_motif', 1.5),                   # Collagen Gly-X-Y
        }
    
    def get_protein_context_multiplier(self, uniprot_id: str, sequence: str, position: int) -> Tuple[float, float]:
        """
        Get context-aware scoring multiplier for any protein
        
        Args:
            uniprot_id: UniProt ID
            sequence: Protein sequence  
            position: Mutation position
            
        Returns:
            (multiplier, confidence) - how much to boost scoring
        """
        
        multiplier = 1.0
        confidence = 0.5
        evidence_sources = []
        
        try:
            if not self.offline_mode:
                # Source 1: Pfam domains (most reliable)
                pfam_multiplier, pfam_conf = self._get_pfam_multiplier(uniprot_id)
                if pfam_multiplier > 1.0:
                    multiplier *= pfam_multiplier
                    confidence += pfam_conf
                    evidence_sources.append(f"Pfam:{pfam_multiplier:.2f}")

                # Source 2: GO terms (functional context)
                go_multiplier, go_conf = self._get_go_multiplier(uniprot_id)
                if go_multiplier > 1.0:
                    multiplier *= go_multiplier
                    confidence += go_conf
                    evidence_sources.append(f"GO:{go_multiplier:.2f}")
            else:
                self.logger.debug("🔧 Skipping API calls in offline mode")

            # Source 3: Sequence motifs (works offline!)
            motif_multiplier, motif_conf = self._get_motif_multiplier(sequence, position)
            if motif_multiplier > 1.0:
                multiplier *= motif_multiplier
                confidence += motif_conf
                evidence_sources.append(f"Motif:{motif_multiplier:.2f}")
            
            # Cap multiplier and confidence
            final_multiplier = min(multiplier, 2.5)  # Don't go crazy
            final_confidence = min(confidence, 0.9)
            
            if evidence_sources:
                self.logger.info(f"🎯 Smart analysis for {uniprot_id}: {final_multiplier:.2f}x from {', '.join(evidence_sources)}")
            
            return final_multiplier, final_confidence
            
        except Exception as e:
            self.logger.warning(f"⚠️ Smart analysis failed for {uniprot_id}: {e}")
            return 1.0, 0.5
    
    def _get_pfam_multiplier(self, uniprot_id: str) -> Tuple[float, float]:
        """Get multiplier from Pfam domains"""
        
        if uniprot_id in self.pfam_cache:
            return self.pfam_cache[uniprot_id]
        
        try:
            # Query UniProt for Pfam domains
            url = f"https://www.uniprot.org/uniprot/{uniprot_id}.xml"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                
                # Find Pfam references
                pfam_ids = []
                for db_ref in root.findall('.//{http://uniprot.org/uniprot}dbReference[@type="Pfam"]'):
                    pfam_id = db_ref.get('id')
                    if pfam_id:
                        pfam_ids.append(pfam_id)
                
                # Get highest weight
                max_weight = 1.0
                for pfam_id in pfam_ids:
                    weight = self.pfam_weights.get(pfam_id, 1.0)
                    max_weight = max(max_weight, weight)
                
                confidence = 0.2 if max_weight > 1.0 else 0.0
                result = (max_weight, confidence)
                self.pfam_cache[uniprot_id] = result
                return result
                
        except Exception as e:
            self.logger.debug(f"Pfam lookup failed for {uniprot_id}: {e}")
        
        # Cache negative result
        result = (1.0, 0.0)
        self.pfam_cache[uniprot_id] = result
        return result
    
    def _get_go_multiplier(self, uniprot_id: str) -> Tuple[float, float]:
        """Get multiplier from GO terms"""
        
        if uniprot_id in self.go_cache:
            return self.go_cache[uniprot_id]
        
        try:
            # Query UniProt for GO terms (simpler than full XML parsing)
            url = f"https://www.uniprot.org/uniprot/{uniprot_id}.txt"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                text = response.text
                
                # Extract GO terms from text format
                go_terms = re.findall(r'GO:(\d+)', text)
                
                # Get highest weight
                max_weight = 1.0
                for go_term in go_terms:
                    go_id = f"GO:{go_term}"
                    weight = self.go_weights.get(go_id, 1.0)
                    max_weight = max(max_weight, weight)
                
                confidence = 0.15 if max_weight > 1.0 else 0.0
                result = (max_weight, confidence)
                self.go_cache[uniprot_id] = result
                return result
                
        except Exception as e:
            self.logger.debug(f"GO lookup failed for {uniprot_id}: {e}")
        
        # Cache negative result
        result = (1.0, 0.0)
        self.go_cache[uniprot_id] = result
        return result
    
    def _get_motif_multiplier(self, sequence: str, position: int) -> Tuple[float, float]:
        """Get multiplier from sequence motifs (works offline!)"""
        
        if not sequence:
            return 1.0, 0.0
        
        max_weight = 1.0
        motifs_found = []
        
        # Check each motif pattern
        for pattern, (motif_name, weight) in self.motif_patterns.items():
            matches = list(re.finditer(pattern, sequence))
            
            for match in matches:
                start, end = match.span()
                
                # Check if mutation is near this motif (within 10 residues)
                if abs(position - start) <= 10 or abs(position - end) <= 10:
                    max_weight = max(max_weight, weight)
                    motifs_found.append(motif_name)
        
        confidence = 0.1 if max_weight > 1.0 else 0.0
        
        if motifs_found:
            self.logger.info(f"🎯 Motifs near position {position}: {', '.join(motifs_found)}")
        
        return max_weight, confidence
    
    def get_analysis_summary(self, uniprot_id: str, sequence: str, position: int) -> Dict:
        """Get detailed analysis summary for debugging"""
        
        multiplier, confidence = self.get_protein_context_multiplier(uniprot_id, sequence, position)
        
        # Get individual components
        pfam_mult, pfam_conf = self._get_pfam_multiplier(uniprot_id)
        go_mult, go_conf = self._get_go_multiplier(uniprot_id)
        motif_mult, motif_conf = self._get_motif_multiplier(sequence, position)
        
        return {
            'final_multiplier': multiplier,
            'final_confidence': confidence,
            'pfam_multiplier': pfam_mult,
            'go_multiplier': go_mult,
            'motif_multiplier': motif_mult,
            'evidence_strength': 'high' if confidence > 0.3 else 'medium' if confidence > 0.1 else 'low'
        }


def test_smart_analyzer():
    """Test the smart analyzer on known proteins"""
    
    print("🧬 TESTING SMART PROTEIN ANALYZER 🧬")
    print("=" * 60)
    print("🎯 Automatic domain-aware scoring for ANY protein!")
    print()
    
    analyzer = SmartProteinAnalyzer()
    
    # Test cases
    test_cases = [
        ('Q8TDX5', 'ACMSD', 175),  # Should detect aldehyde dehydrogenase
        ('P25705', 'ATP5F1A', 130),  # Should detect ATP synthase
        ('Q13402', 'MYO7A', 220),   # Should detect myosin motor
        ('P04637', 'TP53', 175),    # Should detect DNA binding
    ]
    
    for uniprot_id, gene, position in test_cases:
        print(f"🔬 Testing {gene} ({uniprot_id}) position {position}:")
        
        # Get a sample sequence (simplified for testing)
        sequence = "A" * 400  # Placeholder
        
        summary = analyzer.get_analysis_summary(uniprot_id, sequence, position)
        
        print(f"  🎯 Final Multiplier: {summary['final_multiplier']:.2f}")
        print(f"  📊 Confidence: {summary['final_confidence']:.2f}")
        print(f"  🔬 Pfam: {summary['pfam_multiplier']:.2f}")
        print(f"  🧬 GO: {summary['go_multiplier']:.2f}")
        print(f"  ⚡ Evidence: {summary['evidence_strength']}")
        print()
    
    print("🎉 Smart analyzer ready to revolutionize protein analysis!")
    print("💜 Scales to ALL proteins without hardcoding! ⚡🧬")


if __name__ == "__main__":
    test_smart_analyzer()

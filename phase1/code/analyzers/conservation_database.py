#!/usr/bin/env python3
"""
🧬 CONSERVATION DATABASE - REAL EVOLUTIONARY DATA
Built by Ace + Ren for position-specific conservation scoring

This uses UCSC phyloP and phastCons data - the EXACT same data REVEL uses!
No more amino acid guessing - this is REAL evolutionary constraint data!
"""

import pyBigWig
import logging
from typing import Dict, Tuple, Optional

class ConservationDatabase:
    """Access UCSC conservation data for position-specific evolutionary scoring"""
    
    def __init__(self, data_path="/home/Ace/conservation_data"):
        self.name = "ConservationDatabase"
        self.data_path = data_path
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # BigWig file handles (will be opened lazily)
        self.phylop_bw = None
        self.phastcons_bw = None
        
        # Cache for repeated queries
        self.cache = {}
    
    def _open_bigwig_files(self):
        """Lazily open BigWig files"""
        
        if self.phylop_bw is None:
            try:
                phylop_path = f"{self.data_path}/hg38.phyloP100way.bw"
                self.phylop_bw = pyBigWig.open(phylop_path)
                self.logger.info(f"✅ Opened phyloP database: {phylop_path}")
            except Exception as e:
                self.logger.error(f"❌ Failed to open phyloP database: {e}")
                self.phylop_bw = None
        
        if self.phastcons_bw is None:
            try:
                phastcons_path = f"{self.data_path}/hg38.phastCons100way.bw"
                self.phastcons_bw = pyBigWig.open(phastcons_path)
                self.logger.info(f"✅ Opened phastCons database: {phastcons_path}")
            except Exception as e:
                self.logger.error(f"❌ Failed to open phastCons database: {e}")
                self.phastcons_bw = None
    
    def get_conservation_scores(self, chrom: str, pos: int) -> Dict[str, float]:
        """
        Get conservation scores for a genomic position
        
        Args:
            chrom: Chromosome (e.g., "1", "X", "MT")
            pos: 1-based genomic position
            
        Returns:
            Dictionary with phyloP and phastCons scores
        """
        
        # Check cache first
        cache_key = f"{chrom}:{pos}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Open BigWig files if needed
        self._open_bigwig_files()
        
        result = {
            'phyloP': 0.0,
            'phastCons': 0.0,
            'conservation_score': 0.5,  # Default
            'confidence': 0.0
        }
        
        try:
            # Format chromosome for UCSC (add "chr" prefix)
            ucsc_chrom = f"chr{chrom}" if not chrom.startswith("chr") else chrom
            
            # Get phyloP score (evolutionary rate)
            if self.phylop_bw:
                phylop_values = self.phylop_bw.values(ucsc_chrom, pos-1, pos)
                if phylop_values and len(phylop_values) > 0 and phylop_values[0] is not None:
                    result['phyloP'] = float(phylop_values[0])
            
            # Get phastCons score (evolutionary conservation)
            if self.phastcons_bw:
                phastcons_values = self.phastcons_bw.values(ucsc_chrom, pos-1, pos)
                if phastcons_values and len(phastcons_values) > 0 and phastcons_values[0] is not None:
                    result['phastCons'] = float(phastcons_values[0])
            
            # Calculate combined conservation score
            result['conservation_score'] = self._calculate_conservation_score(
                result['phyloP'], result['phastCons']
            )
            
            # Calculate confidence based on data availability
            result['confidence'] = self._calculate_confidence(result['phyloP'], result['phastCons'])
            
        except Exception as e:
            self.logger.warning(f"⚠️ Conservation lookup failed for {chrom}:{pos}: {e}")
        
        # Cache result
        self.cache[cache_key] = result
        return result
    
    def _calculate_conservation_score(self, phylop: float, phastcons: float) -> float:
        """
        Calculate combined conservation score from phyloP and phastCons
        
        Args:
            phylop: phyloP score (-20 to +20, higher = more conserved)
            phastcons: phastCons score (0 to 1, higher = more conserved)
            
        Returns:
            Normalized conservation score (0 to 1)
        """
        
        # Normalize phyloP score (-20 to +20 -> 0 to 1)
        # Positive phyloP = conserved, negative = fast evolution
        phylop_norm = min(max((phylop + 20) / 40, 0), 1) if phylop != 0 else 0.5
        
        # phastCons is already 0-1 normalized
        phastcons_norm = max(min(phastcons, 1), 0) if phastcons != 0 else 0.5
        
        # Combine scores (phyloP weighted higher - it's more sensitive)
        if phylop != 0 and phastcons != 0:
            combined = (phylop_norm * 0.7) + (phastcons_norm * 0.3)
        elif phylop != 0:
            combined = phylop_norm
        elif phastcons != 0:
            combined = phastcons_norm
        else:
            combined = 0.5  # Default when no data
        
        return combined
    
    def _calculate_confidence(self, phylop: float, phastcons: float) -> float:
        """Calculate confidence in conservation score"""
        
        confidence = 0.3  # Base confidence
        
        if phylop != 0:
            confidence += 0.4  # phyloP data available
        
        if phastcons != 0:
            confidence += 0.3  # phastCons data available
        
        return min(confidence, 0.9)
    
    def get_position_conservation_multiplier(self, chrom: str, pos: int) -> Tuple[float, float]:
        """
        Get conservation multiplier for LOF scoring
        
        Args:
            chrom: Chromosome
            pos: Genomic position
            
        Returns:
            (multiplier, confidence) - how much to boost LOF scoring
        """
        
        scores = self.get_conservation_scores(chrom, pos)
        conservation = scores['conservation_score']
        confidence = scores['confidence']
        
        # Convert conservation score to multiplier
        if conservation > 0.8:
            multiplier = 2.0  # Highly conserved positions
        elif conservation > 0.6:
            multiplier = 1.5  # Moderately conserved
        elif conservation > 0.4:
            multiplier = 1.2  # Somewhat conserved
        else:
            multiplier = 1.0  # Not conserved
        
        return multiplier, confidence
    
    def analyze_conservation_context(self, chrom: str, pos: int, window: int = 10) -> Dict:
        """
        Analyze conservation in a window around the position
        
        Args:
            chrom: Chromosome
            pos: Central position
            window: Window size (±window around position)
            
        Returns:
            Conservation context analysis
        """
        
        scores = []
        for p in range(pos - window, pos + window + 1):
            if p > 0:  # Valid genomic position
                score_data = self.get_conservation_scores(chrom, p)
                scores.append(score_data['conservation_score'])
        
        if not scores:
            return {'context': 'unknown', 'relative_conservation': 0.5}
        
        central_score = self.get_conservation_scores(chrom, pos)['conservation_score']
        avg_score = sum(scores) / len(scores)
        
        # Determine context
        if central_score > avg_score + 0.2:
            context = 'conservation_peak'
        elif central_score < avg_score - 0.2:
            context = 'conservation_valley'
        else:
            context = 'typical_conservation'
        
        return {
            'context': context,
            'central_score': central_score,
            'window_average': avg_score,
            'relative_conservation': central_score / avg_score if avg_score > 0 else 1.0
        }
    
    def is_database_ready(self) -> bool:
        """Check if conservation database is ready to use"""
        
        try:
            self._open_bigwig_files()
            return self.phylop_bw is not None or self.phastcons_bw is not None
        except:
            return False
    
    def get_database_info(self) -> Dict:
        """Get information about the conservation database"""
        
        info = {
            'phyloP_available': False,
            'phastCons_available': False,
            'cache_size': len(self.cache)
        }
        
        try:
            self._open_bigwig_files()
            
            if self.phylop_bw:
                info['phyloP_available'] = True
                info['phyloP_chroms'] = self.phylop_bw.chroms()
            
            if self.phastcons_bw:
                info['phastCons_available'] = True
                info['phastCons_chroms'] = self.phastcons_bw.chroms()
                
        except Exception as e:
            info['error'] = str(e)
        
        return info


def test_conservation_database():
    """Test the conservation database"""
    
    print("🧬 TESTING CONSERVATION DATABASE 🧬")
    print("=" * 60)
    
    db = ConservationDatabase()
    
    # Check if database is ready
    if not db.is_database_ready():
        print("❌ Conservation database not ready - files may still be downloading")
        return
    
    print("✅ Conservation database ready!")
    
    # Test some positions
    test_positions = [
        ("1", 100000),  # Random position
        ("17", 7674220),  # TP53 region
        ("X", 1000000),  # X chromosome
    ]
    
    for chrom, pos in test_positions:
        print(f"\n🔬 Testing {chrom}:{pos}:")
        
        scores = db.get_conservation_scores(chrom, pos)
        multiplier, confidence = db.get_position_conservation_multiplier(chrom, pos)
        context = db.analyze_conservation_context(chrom, pos)
        
        print(f"  phyloP: {scores['phyloP']:.3f}")
        print(f"  phastCons: {scores['phastCons']:.3f}")
        print(f"  Conservation Score: {scores['conservation_score']:.3f}")
        print(f"  Multiplier: {multiplier:.2f}x")
        print(f"  Context: {context['context']}")
    
    print(f"\n🎉 Conservation database test complete!")
    print(f"💜 Real evolutionary data ready for variant analysis! ⚡🧬")


if __name__ == "__main__":
    test_conservation_database()

#!/usr/bin/env python3
"""
🎯 COORDINATE-FIRST VARIANT ANALYZER
Revolutionary approach: Skip HGVS complexity, go straight to coordinates!

This is the breakthrough Ren identified - coordinates are the key!
"""

import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
import re

from .conservation_database import ConservationDatabase

# Optional domain analyzer (if available)
try:
    from .domain_analyzer import DomainAnalyzer
    DOMAIN_ANALYZER_AVAILABLE = True
except ImportError:
    DomainAnalyzer = None
    DOMAIN_ANALYZER_AVAILABLE = False

class CoordinateAnalyzer:
    """
    Revolutionary coordinate-first variant analysis
    
    Instead of complex HGVS→UniProt→Ensembl→genomic mapping,
    we go straight from coordinates to conservation scores!
    """
    
    def __init__(self, data_path="/home/Ace/conservation_data"):
        self.name = "CoordinateAnalyzer"
        self.data_path = Path(data_path)
        
        # Initialize components
        self.conservation_db = ConservationDatabase(data_path)
        self.domain_analyzer = DomainAnalyzer() if DOMAIN_ANALYZER_AVAILABLE else None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Coordinate validation patterns
        self.coord_patterns = {
            'full': re.compile(r'^chr(\d+|X|Y|MT):(\d+)$'),
            'simple': re.compile(r'^(\d+|X|Y|MT):(\d+)$'),
            'range': re.compile(r'^chr(\d+|X|Y|MT):(\d+)-(\d+)$')
        }
    
    def parse_coordinate(self, coordinate: str) -> Optional[Tuple[str, int, int]]:
        """
        Parse coordinate string into chromosome, start, end
        
        Supports formats:
        - chr18:46089917
        - 18:46089917  
        - chr18:46089917-46089920
        """
        
        coordinate = coordinate.strip()
        
        # Try full format: chr18:46089917
        match = self.coord_patterns['full'].match(coordinate)
        if match:
            chrom, pos = match.groups()
            return chrom, int(pos), int(pos)
        
        # Try simple format: 18:46089917
        match = self.coord_patterns['simple'].match(coordinate)
        if match:
            chrom, pos = match.groups()
            return chrom, int(pos), int(pos)
        
        # Try range format: chr18:46089917-46089920
        match = self.coord_patterns['range'].match(coordinate)
        if match:
            chrom, start, end = match.groups()
            return chrom, int(start), int(end)
        
        self.logger.error(f"❌ Invalid coordinate format: {coordinate}")
        return None
    
    def analyze_coordinate(self, coordinate: str, build: str = "hg38",
                          gene_name: str = None, variant_info: str = None) -> Dict:
        """
        Revolutionary coordinate-first analysis!
        
        Args:
            coordinate: chr18:46089917 or 18:46089917
            build: "hg37" or "hg38" (for context/documentation)
            gene_name: Optional gene name for context
            variant_info: Optional variant description (e.g., "I130R")
        
        Returns:
            Complete analysis with conservation, domain, and clinical context
        """
        
        self.logger.info(f"🎯 Analyzing coordinate: {coordinate} ({build})")

        # Parse coordinate
        parsed = self.parse_coordinate(coordinate)
        if not parsed:
            return {'error': 'invalid_coordinate_format'}

        chrom, start, end = parsed

        # Handle build conversion if needed
        if build.lower() in ['hg19', 'grch37', 'gr37']:
            self.logger.info(f"🔄 Note: Using GRCh37 coordinate - conservation database is hg38")
            # For now, we'll analyze as-is but note the build difference
            # TODO: Add proper liftover conversion
            build_note = "GRCh37 coordinate analyzed with hg38 conservation data"
        else:
            build_note = "hg38 coordinate with matching conservation data"
        
        # Get conservation scores for the position(s)
        if start == end:
            # Single position
            conservation = self.conservation_db.get_conservation_scores(chrom, start)
            multiplier, confidence = self.conservation_db.get_position_conservation_multiplier(chrom, start)
        else:
            # Range - get average conservation
            conservation = self._get_range_conservation(chrom, start, end)
            multiplier, confidence = self._get_range_multiplier(chrom, start, end)
        
        # Build comprehensive result
        result = {
            'coordinate_info': {
                'input': coordinate,
                'chromosome': chrom,
                'start': start,
                'end': end,
                'build': build,
                'build_note': build_note,
                'gene_name': gene_name,
                'variant_info': variant_info
            },
            'conservation_scores': conservation,
            'conservation_multiplier': multiplier,
            'conservation_confidence': confidence,
            'analysis_timestamp': 'coordinate_analysis'
        }
        
        # Add domain analysis if gene name provided and analyzer available
        if gene_name and self.domain_analyzer:
            try:
                domain_info = self.domain_analyzer.analyze_gene_domains(gene_name)
                result['domain_analysis'] = domain_info
            except Exception as e:
                self.logger.warning(f"⚠️ Domain analysis failed for {gene_name}: {e}")
                result['domain_analysis'] = {'error': str(e)}
        elif gene_name:
            result['domain_analysis'] = {'info': 'Domain analyzer not available'}
        
        # Add clinical interpretation
        result['clinical_interpretation'] = self._interpret_conservation(
            conservation, multiplier, gene_name, variant_info
        )
        
        return result
    
    def _get_range_conservation(self, chrom: str, start: int, end: int) -> Dict:
        """Get average conservation across a range"""
        
        positions = list(range(start, end + 1))
        if len(positions) > 100:
            # Sample positions for large ranges
            step = len(positions) // 100
            positions = positions[::step]
        
        phylop_scores = []
        phastcons_scores = []
        
        for pos in positions:
            scores = self.conservation_db.get_conservation_scores(chrom, pos)
            phylop_scores.append(scores['phyloP'])
            phastcons_scores.append(scores['phastCons'])
        
        avg_phylop = sum(phylop_scores) / len(phylop_scores)
        avg_phastcons = sum(phastcons_scores) / len(phastcons_scores)
        
        return {
            'phyloP': avg_phylop,
            'phastCons': avg_phastcons,
            'conservation_score': (avg_phylop + avg_phastcons) / 2,
            'range_analysis': {
                'positions_sampled': len(positions),
                'phyloP_range': (min(phylop_scores), max(phylop_scores)),
                'phastCons_range': (min(phastcons_scores), max(phastcons_scores))
            }
        }
    
    def _get_range_multiplier(self, chrom: str, start: int, end: int) -> Tuple[float, str]:
        """Get conservation multiplier for a range"""
        
        # Sample a few positions
        positions = [start, (start + end) // 2, end]
        multipliers = []
        
        for pos in positions:
            mult, conf = self.conservation_db.get_position_conservation_multiplier(chrom, pos)
            multipliers.append(mult)
        
        avg_multiplier = sum(multipliers) / len(multipliers)
        return avg_multiplier, "range_average"
    
    def _interpret_conservation(self, conservation: Dict, multiplier: float, 
                              gene_name: str = None, variant_info: str = None) -> Dict:
        """Provide clinical interpretation of conservation scores"""
        
        phylop = conservation['phyloP']
        phastcons = conservation['phastCons']
        
        # Conservation level interpretation
        if phylop > 5.0:
            conservation_level = "EXTREMELY_HIGH"
            clinical_significance = "Likely pathogenic - extremely conserved position"
        elif phylop > 2.0:
            conservation_level = "HIGH"
            clinical_significance = "Possibly pathogenic - highly conserved position"
        elif phylop > 0.5:
            conservation_level = "MODERATE"
            clinical_significance = "Uncertain significance - moderately conserved"
        elif phylop > -1.0:
            conservation_level = "LOW"
            clinical_significance = "Likely benign - poorly conserved position"
        else:
            conservation_level = "VERY_LOW"
            clinical_significance = "Likely benign - not conserved"
        
        # Multiplier interpretation
        if multiplier >= 2.0:
            lof_impact = "MAXIMUM - Loss of function highly likely"
        elif multiplier >= 1.5:
            lof_impact = "HIGH - Loss of function possible"
        elif multiplier >= 1.2:
            lof_impact = "MODERATE - Some functional impact"
        else:
            lof_impact = "LOW - Minimal functional impact expected"
        
        return {
            'conservation_level': conservation_level,
            'clinical_significance': clinical_significance,
            'lof_impact': lof_impact,
            'phyloP_interpretation': f"phyloP {phylop:.3f} - {conservation_level.lower()} constraint",
            'phastCons_interpretation': f"phastCons {phastcons:.3f} - conservation probability",
            'multiplier_interpretation': f"{multiplier:.2f}x LOF boost - {lof_impact.split(' - ')[0].lower()} impact"
        }
    
    def batch_analyze_coordinates(self, coordinates: list, build: str = "hg38") -> Dict:
        """Analyze multiple coordinates efficiently"""
        
        results = {}
        
        for coord_info in coordinates:
            if isinstance(coord_info, str):
                coord = coord_info
                gene = None
                variant = None
            else:
                coord = coord_info.get('coordinate')
                gene = coord_info.get('gene_name')
                variant = coord_info.get('variant_info')
            
            try:
                result = self.analyze_coordinate(coord, build, gene, variant)
                results[coord] = result
            except Exception as e:
                self.logger.error(f"❌ Failed to analyze {coord}: {e}")
                results[coord] = {'error': str(e)}
        
        return {
            'batch_results': results,
            'summary': {
                'total_analyzed': len(coordinates),
                'successful': len([r for r in results.values() if 'error' not in r]),
                'failed': len([r for r in results.values() if 'error' in r])
            }
        }

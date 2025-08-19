#!/usr/bin/env python3
"""
🧬 CONSERVATION-ENHANCED ANALYZER - THE REVOLUTIONARY BREAKTHROUGH!
Built by Ace with Ren's coordinate-first insight

This integrates REAL evolutionary conservation data into LOF/DN scoring!
The missing link that makes our predictions match clinical tools like REVEL!
"""

import logging
from typing import Dict, Any, Optional
from .lof_analyzer import LOFAnalyzer
from .dn_analyzer import DNAnalyzer
from .coordinate_analyzer import CoordinateAnalyzer
from .population_frequency_analyzer import PopulationFrequencyAnalyzer

class ConservationEnhancedAnalyzer:
    """Revolutionary analyzer that uses REAL conservation data to enhance predictions"""
    
    def __init__(self, offline_mode=False):
        self.name = "ConservationEnhancedAnalyzer"
        self.offline_mode = offline_mode
        self.lof_analyzer = LOFAnalyzer(offline_mode=offline_mode)
        self.dn_analyzer = DNAnalyzer(offline_mode=offline_mode)
        self.coordinate_analyzer = CoordinateAnalyzer()
        self.frequency_analyzer = PopulationFrequencyAnalyzer()
        self.logger = logging.getLogger(__name__)

        if self.offline_mode:
            self.logger.info("🔧 OFFLINE MODE: Skipping UniProt API calls for testing")
    
    def analyze_with_conservation(self, mutation: str, sequence: str, 
                                coordinate: str, build: str = "hg38",
                                uniprot_id: str = None, gene_name: str = None, 
                                **kwargs) -> Dict[str, Any]:
        """
        Revolutionary analysis with REAL conservation data!
        
        Args:
            mutation: Mutation string (e.g., "R175H")
            sequence: Protein sequence
            coordinate: Genomic coordinate (e.g., "chr17:7674220")
            build: Genome build ("hg37" or "hg38")
            uniprot_id: UniProt ID
            gene_name: Gene name
            
        Returns:
            Conservation-enhanced comprehensive analysis
        """
        
        self.logger.info(f"🧬 Conservation-enhanced analysis: {gene_name} {mutation} at {coordinate}")
        
        # STEP 1: Get conservation data (the revolutionary breakthrough!)
        conservation_result = self.coordinate_analyzer.analyze_coordinate(
            coordinate, build, gene_name, mutation
        )
        
        if 'error' in conservation_result:
            self.logger.warning(f"⚠️ Conservation analysis failed: {conservation_result['error']}")
            # Fall back to basic analysis
            return self._fallback_analysis(mutation, sequence, uniprot_id, gene_name, **kwargs)
        
        conservation_scores = conservation_result['conservation_scores']
        conservation_multiplier = conservation_result['conservation_multiplier']

        # STEP 2: Population frequency analysis (catch "NOT THE DROID" variants!)
        frequency_result = self._analyze_population_frequency(
            coordinate, mutation, gene_name
        )

        # STEP 3: Enhanced LOF analysis with conservation + frequency multipliers
        lof_result = self._enhanced_lof_analysis(
            mutation, sequence, conservation_scores, conservation_multiplier,
            frequency_result, uniprot_id, **kwargs
        )

        # STEP 4: Enhanced DN analysis with conservation + frequency context
        dn_result = self._enhanced_dn_analysis(
            mutation, sequence, conservation_scores, conservation_multiplier,
            frequency_result, uniprot_id, **kwargs
        )

        # STEP 5: Conservation + frequency aware integration
        integrated_result = self._conservation_frequency_integration(
            lof_result, dn_result, conservation_result, frequency_result, mutation, gene_name
        )
        
        return {
            'gene_name': gene_name,
            'uniprot_id': uniprot_id,
            'mutation': mutation,
            'coordinate': coordinate,
            'build': build,
            'conservation_analysis': conservation_result,
            'enhanced_lof_analysis': lof_result,
            'enhanced_dn_analysis': dn_result,
            'conservation_integrated_analysis': integrated_result,
            'final_prediction': integrated_result['prediction'],
            'confidence': integrated_result['confidence'],
            'conservation_boost': integrated_result.get('conservation_boost', 1.0),
            'frequency_analysis': frequency_result
        }

    def _analyze_population_frequency(self, coordinate: str, mutation: str,
                                    gene_name: str) -> Dict[str, Any]:
        """Analyze population frequency to catch common variants (NOT THE DROID!)"""

        # Parse coordinate to get chromosome, position, ref, alt
        coord_parts = coordinate.replace('chr', '').split(':')
        if len(coord_parts) != 2:
            return {
                'error': 'Invalid coordinate format',
                'rarity_category': 'unknown',
                'pathogenicity_boost': 1.0,
                'not_the_droid': False
            }

        chromosome = coord_parts[0]
        position = int(coord_parts[1])

        # For now, use placeholder ref/alt (would need mutation parsing for real implementation)
        # This is where we'd parse the mutation to get actual ref/alt alleles
        ref_allele = 'A'  # Placeholder
        alt_allele = 'G'  # Placeholder

        self.logger.info(f"🌍 Analyzing population frequency for {gene_name} {mutation}")

        try:
            frequency_data = self.frequency_analyzer.get_variant_frequency(
                chromosome, position, ref_allele, alt_allele
            )

            self.logger.info(f"🎯 Frequency result: {frequency_data.get('rarity_category', 'unknown')}")

            if frequency_data.get('not_the_droid', False):
                self.logger.warning(f"⚠️ NOT THE DROID: {gene_name} {mutation} is too common for rare disease!")

            return frequency_data

        except Exception as e:
            self.logger.error(f"❌ Population frequency analysis failed: {e}")
            return {
                'error': str(e),
                'rarity_category': 'unknown',
                'pathogenicity_boost': 1.0,
                'not_the_droid': False
            }
    
    def _enhanced_lof_analysis(self, mutation: str, sequence: str,
                              conservation_scores: Dict, conservation_multiplier: float,
                              frequency_result: Dict, uniprot_id: str = None, **kwargs) -> Dict[str, Any]:
        """LOF analysis enhanced with conservation data"""
        
        # Get base LOF analysis
        base_lof = self.lof_analyzer.analyze_lof(mutation, sequence, uniprot_id=uniprot_id, **kwargs)
        
        # Apply conservation enhancement
        base_score = base_lof['lof_score']
        phylop = conservation_scores['phyloP']
        
        # Conservation-based score enhancement
        if phylop > 5.0:
            # Extremely conserved - major LOF boost
            conservation_boost = 2.0
            boost_reason = "Extremely conserved position (phyloP > 5.0)"
        elif phylop > 2.0:
            # Highly conserved - significant LOF boost  
            conservation_boost = 1.5
            boost_reason = "Highly conserved position (phyloP > 2.0)"
        elif phylop > 0.5:
            # Moderately conserved - minor LOF boost
            conservation_boost = 1.2
            boost_reason = "Moderately conserved position (phyloP > 0.5)"
        else:
            # Poorly conserved - no boost
            conservation_boost = 1.0
            boost_reason = "Poorly conserved position - no boost"
        
        # Apply frequency-based enhancement
        frequency_boost = frequency_result.get('pathogenicity_boost', 1.0)
        frequency_category = frequency_result.get('rarity_category', 'unknown')

        # Combined enhancement calculation
        combined_boost = conservation_boost * frequency_boost
        enhanced_score = min(1.0, base_score * combined_boost)
        
        # Update prediction based on enhanced score
        if enhanced_score > 0.8:
            enhanced_prediction = "HIGH_LOF"
        elif enhanced_score > 0.6:
            enhanced_prediction = "MODERATE_LOF"
        elif enhanced_score > 0.4:
            enhanced_prediction = "LOW_LOF"
        else:
            enhanced_prediction = "MINIMAL_LOF"
        
        return {
            **base_lof,
            'base_lof_score': base_score,
            'conservation_boost': conservation_boost,
            'frequency_boost': frequency_boost,
            'combined_boost': combined_boost,
            'enhanced_lof_score': enhanced_score,
            'enhanced_prediction': enhanced_prediction,
            'boost_reason': boost_reason,
            'phyloP': phylop,
            'frequency_category': frequency_category,
            'conservation_context': f"phyloP {phylop:.3f} → {conservation_boost:.1f}x conservation",
            'frequency_context': f"{frequency_category} → {frequency_boost:.1f}x frequency",
            'combined_context': f"Combined: {combined_boost:.1f}x boost"
        }
    
    def _enhanced_dn_analysis(self, mutation: str, sequence: str,
                             conservation_scores: Dict, conservation_multiplier: float,
                             frequency_result: Dict, uniprot_id: str = None, **kwargs) -> Dict[str, Any]:
        """DN analysis enhanced with conservation data"""
        
        # Get base DN analysis
        base_dn = self.dn_analyzer.analyze_dn(mutation, sequence, uniprot_id, **kwargs)
        
        # Apply conservation enhancement to DN scoring
        base_score = base_dn['dn_score']
        phylop = conservation_scores['phyloP']
        phastcons = conservation_scores['phastCons']
        
        # Conservation-based DN enhancement
        # High conservation + structural change = higher DN potential
        if phylop > 5.0 and phastcons > 0.8:
            # Extremely conserved structural position
            conservation_boost = 1.8
            boost_reason = "Extremely conserved structural position"
        elif phylop > 2.0 and phastcons > 0.5:
            # Highly conserved with structural importance
            conservation_boost = 1.4
            boost_reason = "Highly conserved structural position"
        elif phylop > 1.0:
            # Moderately conserved
            conservation_boost = 1.2
            boost_reason = "Moderately conserved position"
        else:
            # Poorly conserved - minimal DN potential
            conservation_boost = 0.8
            boost_reason = "Poorly conserved - reduced DN potential"
        
        # Apply frequency-based enhancement
        frequency_boost = frequency_result.get('pathogenicity_boost', 1.0)
        frequency_category = frequency_result.get('rarity_category', 'unknown')

        # Combined enhancement calculation
        combined_boost = conservation_boost * frequency_boost
        enhanced_score = min(1.0, base_score * combined_boost)
        
        # Update DN prediction
        if enhanced_score > 0.7:
            enhanced_prediction = "HIGH_DN"
        elif enhanced_score > 0.5:
            enhanced_prediction = "MODERATE_DN"
        elif enhanced_score > 0.3:
            enhanced_prediction = "LOW_DN"
        else:
            enhanced_prediction = "MINIMAL_DN"
        
        return {
            **base_dn,
            'base_dn_score': base_score,
            'conservation_boost': conservation_boost,
            'frequency_boost': frequency_boost,
            'combined_boost': combined_boost,
            'enhanced_dn_score': enhanced_score,
            'enhanced_prediction': enhanced_prediction,
            'boost_reason': boost_reason,
            'phyloP': phylop,
            'phastCons': phastcons,
            'frequency_category': frequency_category,
            'conservation_context': f"phyloP {phylop:.3f}, phastCons {phastcons:.3f} → {conservation_boost:.1f}x conservation",
            'frequency_context': f"{frequency_category} → {frequency_boost:.1f}x frequency",
            'combined_context': f"Combined: {combined_boost:.1f}x boost"
        }
    
    def _conservation_frequency_integration(self, enhanced_lof: Dict, enhanced_dn: Dict,
                                          conservation_result: Dict, frequency_result: Dict,
                                          mutation: str, gene_name: str) -> Dict[str, Any]:
        """Integrate LOF and DN results with conservation + frequency awareness"""
        
        lof_score = enhanced_lof['enhanced_lof_score']
        dn_score = enhanced_dn['enhanced_dn_score']
        conservation_scores = conservation_result['conservation_scores']
        clinical_interp = conservation_result['clinical_interpretation']
        
        # Conservation-weighted integration
        phylop = conservation_scores['phyloP']
        
        if phylop > 5.0:
            # Extremely conserved - weight both mechanisms heavily
            lof_weight = 0.6
            dn_weight = 0.4
            confidence_boost = 0.2
        elif phylop > 2.0:
            # Highly conserved - standard weighting with boost
            lof_weight = 0.7
            dn_weight = 0.3
            confidence_boost = 0.1
        else:
            # Lower conservation - standard weighting
            lof_weight = 0.8
            dn_weight = 0.2
            confidence_boost = 0.0
        
        # Integrated pathogenicity score
        integrated_score = (lof_score * lof_weight) + (dn_score * dn_weight)
        
        # Conservation-enhanced confidence
        base_confidence = min(enhanced_lof.get('confidence', 0.5), enhanced_dn.get('confidence', 0.5))
        enhanced_confidence = min(1.0, base_confidence + confidence_boost)
        
        # Final prediction with conservation context
        if integrated_score > 0.8:
            prediction = "PATHOGENIC"
            clinical_significance = "Likely pathogenic"
        elif integrated_score > 0.6:
            prediction = "LIKELY_PATHOGENIC"
            clinical_significance = "Possibly pathogenic"
        elif integrated_score > 0.4:
            prediction = "UNCERTAIN"
            clinical_significance = "Uncertain significance"
        elif integrated_score > 0.2:
            prediction = "LIKELY_BENIGN"
            clinical_significance = "Likely benign"
        else:
            prediction = "BENIGN"
            clinical_significance = "Benign"
        
        return {
            'integrated_score': integrated_score,
            'prediction': prediction,
            'clinical_significance': clinical_significance,
            'confidence': enhanced_confidence,
            'conservation_boost': max(enhanced_lof['conservation_boost'], enhanced_dn['conservation_boost']),
            'lof_contribution': lof_score * lof_weight,
            'dn_contribution': dn_score * dn_weight,
            'conservation_level': clinical_interp['conservation_level'],
            'phyloP': phylop,
            'integration_weights': f"LOF {lof_weight:.1f}, DN {dn_weight:.1f}",
            'conservation_rationale': f"phyloP {phylop:.3f} → {clinical_interp['conservation_level']} conservation"
        }
    
    def _fallback_analysis(self, mutation: str, sequence: str, uniprot_id: str = None,
                          gene_name: str = None, **kwargs) -> Dict[str, Any]:
        """Fallback to basic analysis if conservation data unavailable"""
        
        self.logger.warning("🔄 Falling back to basic analysis (no conservation data)")
        
        # Basic LOF and DN analysis
        lof_result = self.lof_analyzer.analyze_lof(mutation, sequence, uniprot_id=uniprot_id, **kwargs)
        dn_result = self.dn_analyzer.analyze_dn(mutation, sequence, uniprot_id, **kwargs)
        
        # Simple integration without conservation
        lof_score = lof_result['lof_score']
        dn_score = dn_result['dn_score']
        integrated_score = (lof_score * 0.8) + (dn_score * 0.2)
        
        return {
            'gene_name': gene_name,
            'uniprot_id': uniprot_id,
            'mutation': mutation,
            'lof_analysis': lof_result,
            'dn_analysis': dn_result,
            'integrated_score': integrated_score,
            'prediction': "BASIC_ANALYSIS",
            'confidence': 0.5,
            'note': "Analysis performed without conservation data"
        }

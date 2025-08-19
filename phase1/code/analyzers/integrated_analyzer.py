#!/usr/bin/env python3
"""
🧬 INTEGRATED ANALYZER - REVOLUTIONARY TWO-BIN APPROACH
Built by Ace for comprehensive variant analysis

This module integrates LOF and DN analysis to provide complete pathogenicity assessment.
The breakthrough that makes our tool work for real clinical cases!
"""

from typing import Dict, Any
from .lof_analyzer import LOFAnalyzer
from .dn_analyzer import DNAnalyzer

class IntegratedAnalyzer:
    """Revolutionary integrated analysis combining LOF and DN mechanisms"""
    
    def __init__(self):
        self.name = "IntegratedAnalyzer"
        self.lof_analyzer = LOFAnalyzer()
        self.dn_analyzer = DNAnalyzer()
    
    def analyze_comprehensive(self, mutation: str, sequence: str, uniprot_id: str = None, 
                            gene_name: str = None, **kwargs) -> Dict[str, Any]:
        """
        Comprehensive variant analysis using two-bin approach
        
        Args:
            mutation: Mutation string (e.g., "R175H")
            sequence: Protein sequence
            uniprot_id: UniProt ID
            gene_name: Gene name for display
            
        Returns:
            Complete integrated analysis
        """
        
        # BIN 1: Loss of Function Analysis
        lof_result = self.lof_analyzer.analyze_lof(mutation, sequence, uniprot_id=uniprot_id, **kwargs)
        
        # BIN 2: Dominant Negative Analysis
        dn_result = self.dn_analyzer.analyze_dn(mutation, sequence, uniprot_id, **kwargs)
        
        # INTEGRATION: Combine results intelligently
        integrated_result = self._integrate_results(lof_result, dn_result, mutation, gene_name)
        
        return {
            'gene_name': gene_name,
            'uniprot_id': uniprot_id,
            'mutation': mutation,
            'lof_analysis': lof_result,
            'dn_analysis': dn_result,
            'integrated_analysis': integrated_result,
            'final_prediction': integrated_result['prediction'],
            'confidence': integrated_result['confidence']
        }
    
    def _integrate_results(self, lof_result: Dict, dn_result: Dict, mutation: str, gene_name: str) -> Dict[str, Any]:
        """Intelligently integrate LOF and DN results"""
        
        lof_score = lof_result['lof_score']
        dn_score = dn_result['dn_score']
        
        # Determine primary mechanism and pathogenicity
        mechanism_classification = self._classify_mechanism(lof_score, dn_score)
        pathogenicity = self._calculate_pathogenicity(lof_score, dn_score, mechanism_classification)
        inheritance_pattern = self._predict_inheritance(mechanism_classification, lof_score, dn_score)
        clinical_significance = self._determine_clinical_significance(pathogenicity, mechanism_classification)
        
        # Calculate integrated confidence
        lof_confidence = lof_result.get('confidence', 0.5)
        dn_confidence = dn_result.get('confidence', 0.5)
        integrated_confidence = self._calculate_integrated_confidence(
            lof_confidence, dn_confidence, mechanism_classification
        )
        
        return {
            'lof_score': lof_score,
            'dn_score': dn_score,
            'mechanism_classification': mechanism_classification,
            'pathogenicity_score': pathogenicity,
            'predicted_inheritance': inheritance_pattern,
            'clinical_significance': clinical_significance,
            'confidence': integrated_confidence,
            'prediction': self._generate_prediction(pathogenicity, mechanism_classification)
        }
    
    def _classify_mechanism(self, lof_score: float, dn_score: float) -> str:
        """Classify the primary pathogenic mechanism"""
        
        # Define thresholds
        lof_threshold = 0.4
        dn_threshold = 0.4
        
        if lof_score >= lof_threshold and dn_score >= dn_threshold:
            return 'LOF_plus_DN'  # Both mechanisms (most severe)
        elif dn_score >= dn_threshold and lof_score < lof_threshold:
            return 'pure_DN'  # Dominant negative only
        elif lof_score >= lof_threshold and dn_score < dn_threshold:
            return 'pure_LOF'  # Loss of function only
        else:
            return 'benign_or_mild'  # Neither mechanism significant
    
    def _calculate_pathogenicity(self, lof_score: float, dn_score: float, mechanism: str) -> float:
        """Calculate overall pathogenicity score"""
        
        if mechanism == 'LOF_plus_DN':
            # Synergistic effect - worse than either alone
            return min(lof_score + dn_score * 0.5, 1.0)
        elif mechanism == 'pure_DN':
            # DN can be pathogenic with single copy
            return dn_score
        elif mechanism == 'pure_LOF':
            # LOF usually needs two copies (recessive)
            return lof_score * 0.7  # Reduced impact for heterozygous
        else:
            # Take the higher of the two
            return max(lof_score, dn_score)
    
    def _predict_inheritance(self, mechanism: str, lof_score: float, dn_score: float) -> str:
        """Predict inheritance pattern based on mechanism"""
        
        if mechanism in ['LOF_plus_DN', 'pure_DN']:
            if dn_score > 0.6:
                return 'autosomal_dominant'
            else:
                return 'possibly_dominant'
        elif mechanism == 'pure_LOF':
            if lof_score > 0.7:
                return 'autosomal_recessive'
            else:
                return 'possibly_recessive'
        else:
            return 'likely_benign'
    
    def _determine_clinical_significance(self, pathogenicity: float, mechanism: str) -> str:
        """Determine clinical significance"""
        
        if pathogenicity > 0.7:
            if mechanism == 'LOF_plus_DN':
                return 'pathogenic_severe'
            else:
                return 'pathogenic'
        elif pathogenicity > 0.5:
            return 'likely_pathogenic'
        elif pathogenicity > 0.3:
            return 'variant_uncertain_significance'
        elif pathogenicity > 0.1:
            return 'likely_benign'
        else:
            return 'benign'
    
    def _calculate_integrated_confidence(self, lof_conf: float, dn_conf: float, mechanism: str) -> float:
        """Calculate integrated confidence"""
        
        if mechanism == 'LOF_plus_DN':
            # High confidence when both mechanisms agree
            return min((lof_conf + dn_conf) / 2 + 0.1, 0.9)
        elif mechanism in ['pure_DN', 'pure_LOF']:
            # Moderate confidence for single mechanism
            return max(lof_conf, dn_conf)
        else:
            # Lower confidence for unclear cases
            return (lof_conf + dn_conf) / 2 * 0.8
    
    def _generate_prediction(self, pathogenicity: float, mechanism: str) -> str:
        """Generate human-readable prediction"""
        
        if mechanism == 'LOF_plus_DN':
            if pathogenicity > 0.7:
                return f"HIGH PATHOGENICITY - Loss of function WITH dominant negative effects (score: {pathogenicity:.3f})"
            else:
                return f"MODERATE PATHOGENICITY - Combined LOF and DN mechanisms (score: {pathogenicity:.3f})"
        
        elif mechanism == 'pure_DN':
            if pathogenicity > 0.6:
                return f"HIGH PATHOGENICITY - Dominant negative mechanism (score: {pathogenicity:.3f})"
            else:
                return f"MODERATE PATHOGENICITY - Possible dominant negative (score: {pathogenicity:.3f})"
        
        elif mechanism == 'pure_LOF':
            if pathogenicity > 0.6:
                return f"MODERATE PATHOGENICITY - Loss of function (likely recessive) (score: {pathogenicity:.3f})"
            else:
                return f"LOW PATHOGENICITY - Mild loss of function (score: {pathogenicity:.3f})"
        
        else:
            return f"LOW PATHOGENICITY - Likely benign or mild effect (score: {pathogenicity:.3f})"
    
    def format_clinical_report(self, result: Dict[str, Any]) -> str:
        """Format results as clinical report"""
        
        integrated = result['integrated_analysis']
        lof = result['lof_analysis']
        dn = result['dn_analysis']
        
        report = f"""
🧬 COMPREHENSIVE VARIANT ANALYSIS REPORT
{'='*60}

VARIANT: {result['gene_name']} {result['mutation']}
UniProt ID: {result['uniprot_id']}

FINAL PREDICTION: {result['final_prediction']}
Confidence: {result['confidence']:.2f}

MECHANISM ANALYSIS:
├── Primary Mechanism: {integrated['mechanism_classification']}
├── Predicted Inheritance: {integrated['predicted_inheritance']}
└── Clinical Significance: {integrated['clinical_significance']}

DETAILED SCORES:
├── Loss of Function Score: {integrated['lof_score']:.3f}
│   ├── Stability Impact: {lof['stability_impact']:.3f}
│   ├── Conservation Impact: {lof['conservation_impact']:.3f}
│   └── Primary LOF Mechanism: {lof['mechanism']}
│
└── Dominant Negative Score: {integrated['dn_score']:.3f}
    ├── Complex Poisoning: {dn['complex_poisoning']:.3f}
    ├── Competitive Binding: {dn['competitive_binding']:.3f}
    └── Primary DN Mechanism: {dn['mechanism']}

CLINICAL INTERPRETATION:
"""
        
        # Add mechanism-specific interpretation
        if integrated['mechanism_classification'] == 'LOF_plus_DN':
            report += """
🚨 DUAL MECHANISM PATHOGENICITY
This variant appears to cause pathogenicity through BOTH loss of function 
AND dominant negative mechanisms. This combination often results in severe 
phenotypes and dominant inheritance patterns.

Clinical Recommendations:
• Consider pathogenic classification
• Expect dominant inheritance pattern
• Functional validation recommended
• Family screening indicated
"""
        
        elif integrated['mechanism_classification'] == 'pure_DN':
            report += """
⚠️  DOMINANT NEGATIVE MECHANISM
This variant likely causes pathogenicity primarily through dominant negative 
effects - the mutant protein interferes with normal protein function.

Clinical Recommendations:
• Consider pathogenic in heterozygous state
• Expect autosomal dominant inheritance
• Single copy may be sufficient for phenotype
• Functional studies of protein interactions recommended
"""
        
        elif integrated['mechanism_classification'] == 'pure_LOF':
            report += """
📉 LOSS OF FUNCTION MECHANISM
This variant likely causes pathogenicity primarily through loss of protein 
function. Typically requires two copies for phenotype (recessive).

Clinical Recommendations:
• Consider pathogenic in homozygous state
• Expect autosomal recessive inheritance
• Heterozygous carriers typically unaffected
• Partner screening recommended for family planning
"""
        
        else:
            report += """
✅ LOW PATHOGENIC POTENTIAL
This variant shows low potential for pathogenicity through either loss of 
function or dominant negative mechanisms.

Clinical Recommendations:
• Consider likely benign classification
• Monitor for additional evidence
• May be population variant
• Functional validation if phenotype strongly suggests pathogenicity
"""
        
        report += f"\n{'='*60}\n"
        
        return report

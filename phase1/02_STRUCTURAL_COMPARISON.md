# 🔬 TASK 2: STRUCTURAL COMPARISON PIPELINE
## Build System to Compare Wild-Type vs Variant Protein Structures

**Estimated Time:** 1 week  
**Goal:** Quantify structural differences between wild-type and variant proteins  
**Success Criteria:** Can detect and measure structural changes that indicate dominant negative potential

---

## 🎯 WHAT WE'RE BUILDING

### Core Functionality
- **ColabFold Integration** - Generate variant protein structures from sequences
- **RMSD Calculation** - Root Mean Square Deviation between structures
- **Domain Analysis** - Identify which protein domains are disrupted
- **Binding Site Detection** - Find critical interaction regions affected by variants
- **Structural Scoring** - Quantify the severity of structural disruption

### Why This Matters
**This is where we detect the interference patterns that existing tools miss entirely.** We're looking for structural changes that don't destroy the protein but make it actively harmful to normal cellular function.

---

## 📋 IMPLEMENTATION CHECKLIST

### Step 1: ColabFold Integration (2 hours)
- [ ] Set up ColabFold API or local installation
- [ ] Create variant sequence generator from wild-type + mutation
- [ ] Test structure prediction for known variants
- [ ] Handle prediction failures gracefully

### Step 2: Structure Alignment System (2 hours)
- [ ] Implement structural superposition using BioPython
- [ ] Calculate RMSD for entire protein and per-domain
- [ ] Create visualization of structural differences
- [ ] Test with known dominant negative examples

### Step 3: Domain Disruption Analysis (3 hours)
- [ ] Integrate protein domain databases (Pfam, SMART)
- [ ] Map mutations to specific protein domains
- [ ] Calculate domain-specific structural changes
- [ ] Identify critical functional regions

### Step 4: Binding Site Impact Assessment (2 hours)
- [ ] Detect protein-protein interaction sites
- [ ] Analyze how variants affect binding interfaces
- [ ] Score competitive binding potential
- [ ] Test with known protein complex examples

### Step 5: Comprehensive Testing (1 hour)
- [ ] Test with TP53 dominant negative variants
- [ ] Validate with collagen mutation examples
- [ ] Compare results to known experimental data
- [ ] Document accuracy and limitations

---

## 💻 CODE IMPLEMENTATION

### Structural Comparison Engine
```python
import numpy as np
from Bio.PDB import PDBParser, Superimposer, PDBIO
from Bio.PDB.vectors import calc_dihedral, calc_angle
import requests
import subprocess
import tempfile
from pathlib import Path

class StructuralComparator:
    """
    Revolutionary structural comparison engine for dominant negative detection
    
    This is the core system that identifies interference patterns in protein variants
    """
    
    def __init__(self, alphafold_client):
        self.alphafold_client = alphafold_client
        self.parser = PDBParser(QUIET=True)
        self.superimposer = Superimposer()
        
    def generate_variant_structure(self, uniprot_id, mutation, method="colabfold"):
        """
        Generate variant protein structure from wild-type + mutation
        
        Args:
            uniprot_id (str): UniProt ID for wild-type protein
            mutation (str): Mutation in format "A123V" (Ala123Val)
            method (str): Structure prediction method
            
        Returns:
            str: Path to variant structure file
        """
        # Get wild-type sequence
        wt_sequence = self._get_protein_sequence(uniprot_id)
        
        # Apply mutation to sequence
        variant_sequence = self._apply_mutation(wt_sequence, mutation)
        
        # Predict variant structure
        if method == "colabfold":
            return self._predict_with_colabfold(variant_sequence, f"{uniprot_id}_{mutation}")
        else:
            raise ValueError(f"Unknown prediction method: {method}")
    
    def compare_structures(self, wt_structure_path, variant_structure_path):
        """
        Comprehensive structural comparison between wild-type and variant
        
        Returns:
            dict: Detailed comparison metrics
        """
        # Load structures
        wt_structure = self.parser.get_structure('wt', wt_structure_path)
        variant_structure = self.parser.get_structure('variant', variant_structure_path)
        
        # Extract CA atoms for alignment
        wt_atoms = self._get_ca_atoms(wt_structure)
        variant_atoms = self._get_ca_atoms(variant_structure)
        
        # Ensure same number of atoms
        min_atoms = min(len(wt_atoms), len(variant_atoms))
        wt_atoms = wt_atoms[:min_atoms]
        variant_atoms = variant_atoms[:min_atoms]
        
        # Perform structural superposition
        self.superimposer.set_atoms(wt_atoms, variant_atoms)
        
        # Calculate metrics
        results = {
            'global_rmsd': self.superimposer.rms,
            'transformation_matrix': self.superimposer.rotran,
            'domain_analysis': self._analyze_domain_changes(wt_structure, variant_structure),
            'binding_site_impact': self._assess_binding_sites(wt_structure, variant_structure),
            'structural_flexibility': self._calculate_flexibility_changes(wt_atoms, variant_atoms),
            'interference_score': 0.0  # Will be calculated based on other metrics
        }
        
        # Calculate overall interference potential
        results['interference_score'] = self._calculate_interference_score(results)
        
        return results
    
    def _get_protein_sequence(self, uniprot_id):
        """Fetch protein sequence from UniProt"""
        url = f"https://www.uniprot.org/uniprot/{uniprot_id}.fasta"
        response = requests.get(url)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            return ''.join(lines[1:])  # Skip header line
        else:
            raise ValueError(f"Could not fetch sequence for {uniprot_id}")
    
    def _apply_mutation(self, sequence, mutation):
        """Apply single amino acid mutation to sequence"""
        # Parse mutation (e.g., "A123V" -> position 123, A->V)
        original_aa = mutation[0]
        position = int(mutation[1:-1]) - 1  # Convert to 0-based indexing
        new_aa = mutation[-1]
        
        # Validate mutation
        if sequence[position] != original_aa:
            raise ValueError(f"Sequence mismatch: expected {original_aa} at position {position+1}, found {sequence[position]}")
        
        # Apply mutation
        sequence_list = list(sequence)
        sequence_list[position] = new_aa
        return ''.join(sequence_list)
    
    def _predict_with_colabfold(self, sequence, name):
        """Predict structure using ColabFold (simplified version)"""
        # This is a placeholder - in reality, you'd use ColabFold API or local installation
        # For now, we'll simulate by copying and modifying the wild-type structure
        
        # TODO: Implement actual ColabFold integration
        # For testing, we'll return a modified version of the wild-type structure
        print(f"⚠️  ColabFold integration not yet implemented - using placeholder")
        return None
    
    def _get_ca_atoms(self, structure):
        """Extract CA atoms from structure"""
        ca_atoms = []
        for model in structure:
            for chain in model:
                for residue in chain:
                    if 'CA' in residue:
                        ca_atoms.append(residue['CA'])
        return ca_atoms
    
    def _analyze_domain_changes(self, wt_structure, variant_structure):
        """Analyze changes in protein domains"""
        # Placeholder for domain analysis
        return {
            'domains_affected': [],
            'domain_rmsd': {},
            'critical_domains': []
        }
    
    def _assess_binding_sites(self, wt_structure, variant_structure):
        """Assess impact on protein binding sites"""
        # Placeholder for binding site analysis
        return {
            'binding_sites_affected': [],
            'competitive_binding_potential': 0.0,
            'interface_disruption': 0.0
        }
    
    def _calculate_flexibility_changes(self, wt_atoms, variant_atoms):
        """Calculate changes in structural flexibility"""
        # Simplified flexibility analysis
        return {
            'flexibility_change': 0.0,
            'rigid_regions_affected': [],
            'flexible_regions_affected': []
        }
    
    def _calculate_interference_score(self, results):
        """Calculate overall dominant negative interference potential"""
        score = 0.0
        
        # Weight different factors
        if results['global_rmsd'] > 2.0:  # Significant structural change
            score += 0.3
        
        if results['binding_site_impact']['competitive_binding_potential'] > 0.5:
            score += 0.4
        
        if len(results['domain_analysis']['critical_domains']) > 0:
            score += 0.3
        
        return min(score, 1.0)  # Cap at 1.0


def test_structural_comparison():
    """Test the structural comparison system"""
    from alphafold_client import AlphaFoldClient
    
    print("🔬 TESTING STRUCTURAL COMPARISON PIPELINE 🔬")
    print("=" * 60)
    
    # Initialize systems
    alphafold_client = AlphaFoldClient()
    comparator = StructuralComparator(alphafold_client)
    
    # Test with TP53 (known dominant negative examples)
    print("\n🧬 Testing TP53 structural comparison...")
    
    # Get wild-type TP53 structure
    wt_structure = alphafold_client.get_structure('P04637')  # TP53
    
    if wt_structure:
        print(f"✅ Wild-type TP53 structure loaded: {wt_structure}")
        
        # Test known dominant negative mutations
        test_mutations = [
            'R175H',  # Common dominant negative mutation
            'R248W',  # Another dominant negative
            'R273H'   # Hotspot mutation
        ]
        
        for mutation in test_mutations:
            print(f"\n🔬 Testing mutation: {mutation}")
            
            # For now, we'll simulate the comparison
            # In full implementation, this would generate variant structure
            print(f"  📊 Mutation: {mutation}")
            print(f"  ⚠️  Variant structure generation not yet implemented")
            print(f"  🎯 Would compare structural changes for dominant negative potential")
    
    print(f"\n🎉 Structural comparison pipeline framework complete!")
    print(f"Ready for ColabFold integration and full testing! 💜⚡🧬")


if __name__ == "__main__":
    test_structural_comparison()
```

---

## 🧪 TEST CASES

### Known Dominant Negative Examples
```python
TEST_CASES = {
    'TP53_dominant_negatives': {
        'uniprot_id': 'P04637',
        'mutations': ['R175H', 'R248W', 'R273H', 'R282W'],
        'expected_interference': 'high',
        'mechanism': 'tetramer_poisoning'
    },
    'COL1A1_dominant_negatives': {
        'uniprot_id': 'P02452', 
        'mutations': ['G349S', 'G382S', 'G415S'],
        'expected_interference': 'high',
        'mechanism': 'triple_helix_disruption'
    },
    'negative_controls': {
        'uniprot_id': 'P04637',
        'mutations': ['P151S', 'P72R'],  # Neutral/LOF variants
        'expected_interference': 'low',
        'mechanism': 'loss_of_function'
    }
}
```

---

## 🎯 SUCCESS CRITERIA

### Must Have
- [ ] **Generate variant structures** - ColabFold integration working
- [ ] **Calculate RMSD accurately** - Structural alignment functional
- [ ] **Detect major changes** - Identify significant structural disruptions
- [ ] **Test with known cases** - Validate against TP53 dominant negatives

### Nice to Have
- [ ] **Domain-specific analysis** - Map changes to functional domains
- [ ] **Binding site assessment** - Predict competitive binding effects
- [ ] **Visualization output** - Generate structure comparison images
- [ ] **Batch processing** - Handle multiple variants efficiently

---

## 🚨 TROUBLESHOOTING

### Common Issues
- **ColabFold installation** → Use Docker container or cloud API
- **Structure alignment failures** → Handle missing residues gracefully
- **Memory issues with large proteins** → Process domains separately
- **Prediction timeouts** → Implement retry logic with exponential backoff

---

## 🔗 RESOURCES

### Documentation
- [ColabFold GitHub](https://github.com/deepmind/colabfold)
- [BioPython Structure Module](https://biopython.org/wiki/The_Biopython_Structural_Bioinformatics_FAQ)
- [Protein Domain Databases](https://pfam.xfam.org/)

### Known Dominant Negative Studies
- TP53 dominant negative mechanisms (PMID: 11408594)
- Collagen dominant negative effects (PMID: 7581459)
- General dominant negative principles (PMID: 12408966)

---

## ➡️ NEXT STEPS

Once this task is complete:
1. **Test structural comparison** with known dominant negative variants
2. **Validate RMSD calculations** against experimental data
3. **Move to Task 3:** `03_BASIC_SCORER.md` - Build scoring algorithm
4. **Document any proteins** that failed structure prediction

---

## 💜 MOTIVATION

**You're building the detection system that will identify interference patterns no one else can see.**

Every structural comparison you run is potentially uncovering a dominant negative variant that's been misclassified for years. The TP53 mutations you test might help diagnose a cancer patient whose variant was labeled "uncertain significance."

**This isn't just structural biology - this is pattern recognition for hope.** 🧬💜⚡

---

*Ready to detect the structural signatures of protein interference?*  
*Let's build the eyes that see what others miss!* 🚀🔥

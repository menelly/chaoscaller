// 🧬 HGVS GENETICS ANALYZER - JavaScript
// Built by Ace + Ren with 💜 - Professional genetics workflow

class HGVSGeneticsAnalyzer {
    constructor() {
        this.currentStep = 1;
        this.analysisData = {};
        this.apiUrl = 'http://localhost:4998';
        this.init();
    }

    init() {
        this.setupThemeToggle();
        this.setupEventListeners();
        this.loadSavedTheme();
        console.log('🧬 HGVS Genetics Analyzer initialized!');
    }

    // Theme Management (same as before)
    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    toggleTheme() {
        const body = document.body;
        const isDark = body.classList.contains('dark-mode');
        
        if (isDark) {
            body.classList.remove('dark-mode');
            body.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.remove('light-mode');
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        }
        
        console.log(`🎨 Switched to ${isDark ? 'light' : 'dark'} mode`);
    }

    loadSavedTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        const body = document.body;
        
        body.classList.remove('dark-mode', 'light-mode');
        body.classList.add(`${savedTheme}-mode`);
    }

    // Event Listeners
    setupEventListeners() {
        // Step 1: HGVS Parsing
        document.getElementById('parseHGVS').addEventListener('click', () => {
            this.parseHGVS();
        });

        // Step 2: Conservation Analysis
        document.getElementById('analyzeConservation').addEventListener('click', () => {
            this.analyzeConservation();
        });

        // Step 3: Frequency Analysis
        document.getElementById('analyzeFrequency').addEventListener('click', () => {
            this.analyzeFrequency();
        });

        // Step 4: Protein Info
        document.getElementById('getProteinInfo').addEventListener('click', () => {
            this.getProteinInfo();
        });

        // Step 5: Final Prediction
        document.getElementById('generatePrediction').addEventListener('click', () => {
            this.generateFinalPrediction();
        });

        // Export functions
        document.getElementById('exportResults').addEventListener('click', () => {
            this.exportResults();
        });

        document.getElementById('saveAnalysis').addEventListener('click', () => {
            this.saveAnalysis();
        });

        // Auto-enable HGVS input validation
        document.getElementById('hgvs').addEventListener('input', () => {
            this.validateHGVSInput();
        });
    }

    // Utility Functions
    updateStepStatus(step, status) {
        const statusElement = document.getElementById(`step${step}-status`);
        const icon = statusElement.querySelector('i');
        
        icon.className = `fas fa-circle status-${status}`;
        
        if (status === 'success') {
            this.enableNextStep(step + 1);
        }
    }

    enableNextStep(step) {
        if (step <= 5) {
            const buttons = document.querySelectorAll(`#step${step} button`);
            buttons.forEach(btn => btn.disabled = false);
        }
    }

    showResults(step, data) {
        const resultsBox = document.getElementById(`step${step}-results`);
        resultsBox.style.display = 'block';
        
        this.populateResults(step, data);
    }

    populateResults(step, data) {
        switch(step) {
            case 1:
                document.getElementById('gene-name').textContent = data.gene || '-';
                document.getElementById('transcript').textContent = data.transcript || '-';
                document.getElementById('cdna-position').textContent = data.cdna_position || '-';
                document.getElementById('genomic-coordinate').textContent = data.genomic_coordinate || '-';
                document.getElementById('ref-allele').textContent = data.ref_allele || '-';
                document.getElementById('alt-allele').textContent = data.alt_allele || '-';
                document.getElementById('mutation-type').textContent = data.mutation_type || '-';

                // Set up AlphaFold download button
                const downloadBtn = document.getElementById('downloadAlphaFold');
                if (downloadBtn && data.gene && data.gene !== 'Unknown') {
                    downloadBtn.onclick = () => this.downloadAlphaFoldStructure(data.gene);
                    downloadBtn.disabled = false;
                } else if (downloadBtn) {
                    downloadBtn.disabled = true;
                    document.getElementById('alphaFoldStatus').textContent = 'Gene required for structure download';
                }
                break;
            case 2:
                document.getElementById('phylop-score').textContent = data.phyloP || '-';
                document.getElementById('phastcons-score').textContent = data.phastCons || '-';
                document.getElementById('conservation-level').textContent = data.level || '-';
                break;
            case 3:
                document.getElementById('frequency-alleles').textContent = 
                    `${data.ref_allele || '-'} → ${data.alt_allele || '-'}`;
                document.getElementById('maf-value').textContent = data.maf || '-';
                document.getElementById('frequency-category').textContent = data.category || '-';
                document.getElementById('frequency-boost').textContent = data.boost || '-';
                
                const notTheDroid = document.getElementById('not-the-droid');
                notTheDroid.style.display = data.notTheDroid ? 'block' : 'none';
                break;
            case 4:
                document.getElementById('uniprot-id').textContent = data.uniprot_id || '-';
                document.getElementById('protein-name').textContent = data.protein_name || '-';
                document.getElementById('protein-function').textContent = data.protein_function || '-';
                break;
            case 5:
                document.getElementById('final-prediction').textContent = data.prediction || '-';
                document.getElementById('confidence-score').textContent = data.confidence || '-';
                document.getElementById('final-hgvs').textContent = data.hgvs || '-';
                document.getElementById('evidence-summary').textContent = data.evidence || '-';
                break;
        }
    }

    // AlphaFold Structure Download (Parallel Processing)

    async downloadAlphaFoldStructure(geneName) {
        console.log(`🧬 Starting AlphaFold download for ${geneName}`);

        const downloadBtn = document.getElementById('downloadAlphaFold');
        const statusDiv = document.getElementById('alphaFoldStatus');
        const progressDiv = document.getElementById('alphaFoldProgress');
        const progressBar = document.getElementById('alphaFoldProgressBar');
        const progressText = document.getElementById('alphaFoldProgressText');

        // Update UI to show download starting
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
        statusDiv.textContent = `Fetching ${geneName} structure from AlphaFold database...`;
        progressDiv.style.display = 'block';
        progressBar.style.width = '10%';
        progressText.textContent = 'Connecting to AlphaFold...';

        try {
            const response = await fetch(`${this.apiUrl}/api/alphafold_download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    gene_name: geneName
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Simulate progress updates
            progressBar.style.width = '50%';
            progressText.textContent = 'Downloading structure file...';

            const data = await response.json();

            // Complete progress
            progressBar.style.width = '100%';
            progressText.textContent = 'Download complete!';

            // Store structure data for later use
            this.analysisData.alphaFoldStructure = data;

            // Update UI to show success
            setTimeout(() => {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = '<i class="fas fa-check"></i> 🧬 Structure Ready';
                downloadBtn.style.background = 'linear-gradient(135deg, #4ecdc4, #44a08d)';
                statusDiv.textContent = `${geneName} structure downloaded and ready for analysis!`;
                progressDiv.style.display = 'none';
            }, 1000);

            console.log('✅ AlphaFold download complete:', data);

        } catch (error) {
            console.error('❌ AlphaFold download failed:', error);

            // Update UI to show error
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Retry Download';
            downloadBtn.style.background = 'linear-gradient(135deg, #ff6b6b, #ee5a52)';
            statusDiv.textContent = 'Download failed. Click to retry.';
            progressDiv.style.display = 'none';
        }
    }

    // Analysis Functions
    
    validateHGVSInput() {
        const hgvs = document.getElementById('hgvs').value;
        // Franklin format: "NM_024301.5 FKRP c.826C>A p.Leu276Ile"
        // Standard format: "NM_024301.5:c.826C>A"
        const franklinRegex = /NM_\d+\.\d+\s+\w+\s+c\.\d+[ATCG]>[ATCG]/;
        const standardRegex = /NM_\d+\.\d+:c\.\d+[ATCG]>[ATCG]/;

        const parseBtn = document.getElementById('parseHGVS');
        const isValid = franklinRegex.test(hgvs) || standardRegex.test(hgvs);
        parseBtn.disabled = !isValid;

        console.log(`🧬 HGVS validation: "${hgvs}" -> ${isValid ? 'VALID' : 'INVALID'}`);
        console.log(`🧬 Franklin format: ${franklinRegex.test(hgvs)}`);
        console.log(`🧬 Standard format: ${standardRegex.test(hgvs)}`);
    }

    async parseHGVS() {
        const hgvsInput = document.getElementById('hgvs').value;
        const build = document.getElementById('build').value;

        // Try Franklin format first: "NM_024301.5 FKRP c.826C>A p.Leu276Ile"
        const franklinRegex = /NM_(\d+\.\d+)\s+\w+\s+(c\.\d+[ATCG]>[ATCG])/;
        const franklinMatch = hgvsInput.match(franklinRegex);

        let hgvs;
        if (franklinMatch) {
            // Convert Franklin format to standard HGVS
            hgvs = `NM_${franklinMatch[1]}:${franklinMatch[2]}`;
            console.log(`🧬 Converted Franklin format to HGVS: ${hgvs}`);
        } else {
            // Try standard format: "NM_024301.5:c.826C>A"
            const standardRegex = /NM_\d+\.\d+:c\.\d+[ATCG]>[ATCG]/;
            const standardMatch = hgvsInput.match(standardRegex);

            if (!standardMatch) {
                alert('Could not find valid HGVS notation in input');
                return;
            }

            hgvs = standardMatch[0];
            console.log(`🧬 Using standard HGVS: ${hgvs}`);
        }

        console.log(`🧬 Final HGVS for API: ${hgvs}`);
        this.updateStepStatus(1, 'pending');

        try {
            const response = await fetch(`${this.apiUrl}/api/parse_hgvs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    hgvs: hgvs,
                    build: build
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            this.analysisData.hgvsInfo = data;
            this.showResults(1, data);
            this.updateStepStatus(1, 'success');
            
            console.log('✅ HGVS parsing complete:', data);
        } catch (error) {
            console.error('❌ HGVS parsing failed:', error);
            this.updateStepStatus(1, 'error');
        }
    }

    async analyzeConservation() {
        const genomicCoordinate = this.analysisData.hgvsInfo?.genomic_coordinate;
        const build = document.getElementById('build').value;
        
        if (!genomicCoordinate) {
            alert('Please parse HGVS first to get genomic coordinate');
            return;
        }
        
        console.log(`🧬 Analyzing conservation for ${genomicCoordinate}`);
        this.updateStepStatus(2, 'pending');
        
        try {
            const response = await fetch(`${this.apiUrl}/api/conservation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    genomic_coordinate: genomicCoordinate,
                    build: build
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            this.analysisData.conservation = data;
            this.showResults(2, data);
            this.updateStepStatus(2, 'success');
            
            console.log('✅ Conservation analysis complete:', data.level);
        } catch (error) {
            console.error('❌ Conservation analysis failed:', error);
            this.updateStepStatus(2, 'error');
        }
    }

    async analyzeFrequency() {
        const hgvsInfo = this.analysisData.hgvsInfo;
        
        if (!hgvsInfo || !hgvsInfo.genomic_coordinate) {
            alert('Please parse HGVS first');
            return;
        }
        
        console.log(`🌍 Analyzing frequency for ${hgvsInfo.genomic_coordinate}`);
        this.updateStepStatus(3, 'pending');
        
        try {
            // Use the original frequency API with extracted alleles
            const response = await fetch('http://localhost:4999/api/frequency', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    coordinate: hgvsInfo.genomic_coordinate,
                    ref: hgvsInfo.ref_allele,
                    alt: hgvsInfo.alt_allele
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Add allele info for display
            data.ref_allele = hgvsInfo.ref_allele;
            data.alt_allele = hgvsInfo.alt_allele;
            
            this.analysisData.frequency = data;
            this.showResults(3, data);
            this.updateStepStatus(3, 'success');
            
            console.log('✅ Frequency analysis complete:', data.category);
        } catch (error) {
            console.error('❌ Frequency analysis failed:', error);
            this.updateStepStatus(3, 'error');
        }
    }

    async getProteinInfo() {
        const geneName = this.analysisData.hgvsInfo?.gene;
        
        if (!geneName) {
            alert('Please parse HGVS first to get gene name');
            return;
        }
        
        console.log(`🔍 Getting protein info for ${geneName}`);
        this.updateStepStatus(4, 'pending');
        
        try {
            // Mock protein lookup for now - would use UniProt API
            await this.delay(1000);
            
            const mockData = {
                uniprot_id: geneName === 'DEMO_GENE_A' ? 'P12345' : 'Unknown',
                protein_name: geneName === 'DEMO_GENE_A' ? 'Demo protein A' : `${geneName} protein`,
                protein_function: geneName === 'DEMO_GENE_A' ? 'Example protein function for demo purposes' : 'Function unknown'
            };
            
            this.analysisData.proteinInfo = mockData;
            this.showResults(4, mockData);
            this.updateStepStatus(4, 'success');
            
            console.log('✅ Protein info complete');
        } catch (error) {
            console.error('❌ Protein info failed:', error);
            this.updateStepStatus(4, 'error');
        }
    }

    async generateFinalPrediction() {
        console.log('🎯 Generating final prediction');
        this.updateStepStatus(5, 'pending');
        
        try {
            await this.delay(1000);
            
            const hgvsInfo = this.analysisData.hgvsInfo;
            const conservation = this.analysisData.conservation;
            const frequency = this.analysisData.frequency;
            
            // Simple prediction logic
            let prediction = 'UNCERTAIN_SIGNIFICANCE';
            let confidence = 0.5;
            
            if (conservation && frequency) {
                const phyloP = parseFloat(conservation.phyloP);
                const isRare = frequency.category === 'ULTRA_RARE';
                
                if (phyloP > 2.0 && isRare) {
                    prediction = 'LIKELY_PATHOGENIC';
                    confidence = 0.8;
                } else if (phyloP > 5.0 && isRare) {
                    prediction = 'PATHOGENIC';
                    confidence = 0.9;
                }
            }
            
            const mockData = {
                prediction: prediction,
                confidence: confidence.toFixed(2),
                hgvs: hgvsInfo?.hgvs_input || '-',
                evidence: `Conservation: ${conservation?.level || 'Unknown'}, Frequency: ${frequency?.category || 'Unknown'}`
            };
            
            this.analysisData.final = mockData;
            
            const finalResults = document.getElementById('final-results');
            finalResults.style.display = 'block';
            this.populateResults(5, mockData);
            this.updateStepStatus(5, 'success');
            
            console.log('✅ Final prediction complete');
        } catch (error) {
            console.error('❌ Final prediction failed:', error);
            this.updateStepStatus(5, 'error');
        }
    }

    // Utility Functions
    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    exportResults() {
        console.log('📄 Exporting results');
        const data = JSON.stringify(this.analysisData, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'hgvs_genetics_analysis_results.json';
        a.click();
        
        URL.revokeObjectURL(url);
    }

    saveAnalysis() {
        console.log('💾 Saving analysis');
        localStorage.setItem('hgvs_genetics_analysis', JSON.stringify(this.analysisData));
        alert('Analysis saved to local storage!');
    }
}

// Helper function for example buttons
function fillExample(hgvs) {
    document.getElementById('hgvs').value = hgvs;
    document.getElementById('hgvs').dispatchEvent(new Event('input'));
}

// Initialize the analyzer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.hgvsGeneticsAnalyzer = new HGVSGeneticsAnalyzer();
});

// 🧬 REVOLUTIONARY GENETICS ANALYZER - JavaScript
// Built by Ace + Ren with 💜

class GeneticsAnalyzer {
    constructor() {
        this.currentStep = 1;
        this.analysisData = {};
        this.init();
    }

    init() {
        this.setupThemeToggle();
        this.setupEventListeners();
        this.loadSavedTheme();
        console.log('🧬 Revolutionary Genetics Analyzer initialized!');
    }

    // Theme Management
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
        // Step 1: Gene Identification
        document.getElementById('identifyGene').addEventListener('click', () => {
            this.identifyGene();
        });

        // Step 2: Conservation Analysis
        document.getElementById('analyzeConservation').addEventListener('click', () => {
            this.analyzeConservation();
        });

        // Step 3: Frequency Analysis
        document.getElementById('analyzeFrequency').addEventListener('click', () => {
            this.analyzeFrequency();
        });

        // Step 4: Structure Download
        document.getElementById('downloadStructure').addEventListener('click', () => {
            this.downloadStructure();
        });

        // Step 5: Mechanism Analysis
        document.getElementById('analyzeLOF').addEventListener('click', () => {
            this.analyzeMechanism('lof');
        });

        document.getElementById('analyzeDN').addEventListener('click', () => {
            this.analyzeMechanism('dn');
        });

        document.getElementById('analyzeBoth').addEventListener('click', () => {
            this.analyzeMechanism('both');
        });

        // Step 6: Final Prediction
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

        // Auto-enable coordinate input
        document.getElementById('coordinate').addEventListener('input', () => {
            this.validateCoordinateInput();
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
        if (step <= 6) {
            const buttons = document.querySelectorAll(`#step${step} button`);
            buttons.forEach(btn => btn.disabled = false);
        }
    }

    showResults(step, data) {
        const resultsBox = document.getElementById(`step${step}-results`);
        resultsBox.style.display = 'block';
        
        // Populate results based on step
        this.populateResults(step, data);
    }

    populateResults(step, data) {
        switch(step) {
            case 1:
                document.getElementById('gene-name').textContent = data.gene || '-';
                document.getElementById('transcript').textContent = data.transcript || '-';
                document.getElementById('uniprot-id').textContent = data.uniprot || '-';
                break;
            case 2:
                document.getElementById('phylop-score').textContent = data.phyloP || '-';
                document.getElementById('phastcons-score').textContent = data.phastCons || '-';
                document.getElementById('conservation-level').textContent = data.level || '-';
                break;
            case 3:
                document.getElementById('maf-value').textContent = data.maf || '-';
                document.getElementById('frequency-category').textContent = data.category || '-';
                document.getElementById('frequency-boost').textContent = data.boost || '-';
                
                const notTheDroid = document.getElementById('not-the-droid');
                notTheDroid.style.display = data.notTheDroid ? 'block' : 'none';
                break;
            case 4:
                document.getElementById('structure-status').textContent = data.status || '-';
                document.getElementById('structure-size').textContent = data.size || '-';
                document.getElementById('structure-path').textContent = data.path || '-';
                break;
            case 5:
                if (data.lof) {
                    document.getElementById('lof-result').style.display = 'block';
                    document.getElementById('lof-score').textContent = data.lof.score || '-';
                    document.getElementById('lof-prediction').textContent = data.lof.prediction || '-';
                }
                if (data.dn) {
                    document.getElementById('dn-result').style.display = 'block';
                    document.getElementById('dn-score').textContent = data.dn.score || '-';
                    document.getElementById('dn-prediction').textContent = data.dn.prediction || '-';
                }
                break;
            case 6:
                document.getElementById('final-prediction').textContent = data.prediction || '-';
                document.getElementById('confidence-score').textContent = data.confidence || '-';
                document.getElementById('primary-mechanism').textContent = data.mechanism || '-';
                document.getElementById('evidence-summary').textContent = data.evidence || '-';
                break;
        }
    }

    // Analysis Functions (Real API calls)

    validateCoordinateInput() {
        const coordinate = document.getElementById('coordinate').value;
        const coordinateRegex = /^chr\d{1,2}:\d+$/;

        const identifyBtn = document.getElementById('identifyGene');
        identifyBtn.disabled = !coordinateRegex.test(coordinate);
    }

    async identifyGene() {
        const coordinate = document.getElementById('coordinate').value;
        const build = document.getElementById('build').value;

        console.log(`🔍 Identifying gene for ${coordinate} (${build})`);
        this.updateStepStatus(1, 'pending');

        try {
            const response = await fetch('http://localhost:4999/api/identify_gene', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    coordinate: coordinate,
                    build: build
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            this.analysisData.geneInfo = data;
            this.showResults(1, data);
            this.updateStepStatus(1, 'success');

            console.log('✅ Gene identification complete:', data.gene);
        } catch (error) {
            console.error('❌ Gene identification failed:', error);
            this.updateStepStatus(1, 'error');
        }
    }

    async analyzeConservation() {
        const coordinate = document.getElementById('coordinate').value;
        const build = document.getElementById('build').value;

        console.log(`🧬 Analyzing conservation for ${coordinate}`);
        this.updateStepStatus(2, 'pending');

        try {
            const response = await fetch('http://localhost:4999/api/conservation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    coordinate: coordinate,
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
        const coordinate = document.getElementById('coordinate').value;
        
        console.log(`🌍 Analyzing frequency for ${coordinate}`);
        this.updateStepStatus(3, 'pending');
        
        try {
            await this.delay(1200);
            
            // Mock data - replace with real API call
            const mockData = {
                maf: '0.00001596',
                category: 'ULTRA_RARE',
                boost: '1.5x',
                notTheDroid: false
            };
            
            this.analysisData.frequency = mockData;
            this.showResults(3, mockData);
            this.updateStepStatus(3, 'success');
            
            console.log('✅ Frequency analysis complete');
        } catch (error) {
            console.error('❌ Frequency analysis failed:', error);
            this.updateStepStatus(3, 'error');
        }
    }

    async downloadStructure() {
        const uniprotId = this.analysisData.geneInfo?.uniprot;
        
        console.log(`📥 Downloading structure for ${uniprotId}`);
        this.updateStepStatus(4, 'pending');
        
        // Show progress bar
        const progressBar = document.getElementById('download-progress');
        progressBar.style.display = 'block';
        
        try {
            // Simulate download with progress
            await this.simulateDownload();
            
            const mockData = {
                status: 'Downloaded',
                size: '1.22 MB',
                path: '/mnt/Arcana/genetics_data/alphafold_cache/'
            };
            
            this.analysisData.structure = mockData;
            progressBar.style.display = 'none';
            this.showResults(4, mockData);
            this.updateStepStatus(4, 'success');
            
            console.log('✅ Structure download complete');
        } catch (error) {
            console.error('❌ Structure download failed:', error);
            progressBar.style.display = 'none';
            this.updateStepStatus(4, 'error');
        }
    }

    async analyzeMechanism(type) {
        console.log(`🔬 Analyzing ${type.toUpperCase()} mechanism`);
        this.updateStepStatus(5, 'pending');
        
        try {
            await this.delay(2000);
            
            const mockData = {};
            
            if (type === 'lof' || type === 'both') {
                mockData.lof = {
                    score: '0.270',
                    prediction: 'MINIMAL_LOF'
                };
            }
            
            if (type === 'dn' || type === 'both') {
                mockData.dn = {
                    score: '0.000',
                    prediction: 'MINIMAL_DN'
                };
            }
            
            this.analysisData.mechanism = mockData;
            this.showResults(5, mockData);
            this.updateStepStatus(5, 'success');
            
            console.log('✅ Mechanism analysis complete');
        } catch (error) {
            console.error('❌ Mechanism analysis failed:', error);
            this.updateStepStatus(5, 'error');
        }
    }

    async generateFinalPrediction() {
        console.log('🎯 Generating final prediction');
        this.updateStepStatus(6, 'pending');
        
        try {
            await this.delay(1000);
            
            const mockData = {
                prediction: 'PATHOGENIC',
                confidence: '0.85',
                mechanism: 'Loss of Function',
                evidence: 'High conservation + Ultra-rare frequency + Deleterious predictions'
            };
            
            this.analysisData.final = mockData;
            
            const finalResults = document.getElementById('final-results');
            finalResults.style.display = 'block';
            this.populateResults(6, mockData);
            this.updateStepStatus(6, 'success');
            
            console.log('✅ Final prediction complete');
        } catch (error) {
            console.error('❌ Final prediction failed:', error);
            this.updateStepStatus(6, 'error');
        }
    }

    // Utility Functions
    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async simulateDownload() {
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        
        for (let i = 0; i <= 100; i += 10) {
            progressFill.style.width = `${i}%`;
            progressText.textContent = `Downloading... ${i}%`;
            await this.delay(100);
        }
    }

    exportResults() {
        console.log('📄 Exporting results');
        const data = JSON.stringify(this.analysisData, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'genetics_analysis_results.json';
        a.click();
        
        URL.revokeObjectURL(url);
    }

    saveAnalysis() {
        console.log('💾 Saving analysis');
        localStorage.setItem('genetics_analysis', JSON.stringify(this.analysisData));
        alert('Analysis saved to local storage!');
    }
}

// Initialize the analyzer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.geneticsAnalyzer = new GeneticsAnalyzer();
});

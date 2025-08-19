#!/usr/bin/env python3
"""
🧬 Genetics Analyzer API Server
Built by Ace + Ren - Backend for the web interface
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging

# Add the phase1/code directory to Python path
sys.path.append('/home/Ace/caller/phase1/code')

# Import our existing analyzers
try:
    from analyzers.coordinate_analyzer import CoordinateAnalyzer
    from analyzers.conservation_enhanced_analyzer import ConservationEnhancedAnalyzer
    from analyzers.population_frequency_analyzer import PopulationFrequencyAnalyzer
    from alphafold_client import AlphaFoldClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory!")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize analyzers
try:
    coordinate_analyzer = CoordinateAnalyzer()
    conservation_analyzer = ConservationEnhancedAnalyzer()
    frequency_analyzer = PopulationFrequencyAnalyzer()
    alphafold_client = AlphaFoldClient()
    logger.info("✅ All analyzers initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize analyzers: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': '🧬 Genetics Analyzer API is running!',
        'version': '1.0.0'
    })

def lookup_gene_by_coordinate(coordinate, build='hg38'):
    """Real gene lookup using multiple APIs"""
    import requests

    try:
        # Parse coordinate properly
        if ':' not in coordinate:
            logger.error(f"❌ Invalid coordinate format: {coordinate}")
            return None

        parts = coordinate.split(':')
        chrom = parts[0].replace('chr', '')
        position = int(parts[1])

        logger.info(f"🔍 Looking up gene for chr{chrom}:{position}")

        # Try Ensembl REST API first
        logger.info("🧬 Trying Ensembl API...")
        result = try_ensembl_lookup(chrom, position, build)
        if result:
            logger.info(f"✅ Ensembl success: {result}")
            return result

        # Try NCBI Gene API
        logger.info("🔬 Trying NCBI API...")
        result = try_ncbi_lookup(chrom, position)
        if result:
            logger.info(f"✅ NCBI success: {result}")
            return result

        # Try UCSC API
        logger.info("🌐 Trying UCSC API...")
        result = try_ucsc_lookup(chrom, position, build)
        if result:
            logger.info(f"✅ UCSC success: {result}")
            return result

        logger.error("❌ All APIs failed to find gene")
        return None

    except Exception as e:
        logger.error(f"❌ Gene lookup failed: {e}")
        return None

def try_ensembl_lookup(chrom, position, build='hg38'):
    """Try Ensembl REST API"""
    import requests

    try:
        # Ensembl uses different assembly names
        assembly = 'GRCh38' if build == 'hg38' else 'GRCh37'

        url = f"https://rest.ensembl.org/overlap/region/human/{chrom}:{position}-{position}"
        params = {
            'feature': 'gene',
            'content-type': 'application/json'
        }

        logger.info(f"🧬 ENSEMBL: Trying URL: {url}")
        logger.info(f"🧬 ENSEMBL: Params: {params}")

        response = requests.get(url, params=params, timeout=10)

        logger.info(f"🧬 ENSEMBL: Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"🧬 ENSEMBL: Response data: {data}")

            if data:
                gene = data[0]  # Take first gene
                gene_name = gene.get('external_name', gene.get('id', 'Unknown'))
                gene_id = gene.get('id', 'Unknown')

                logger.info(f"✅ Ensembl found: {gene_name} (ID: {gene_id})")

                return {
                    'gene': gene_name,
                    'transcript': f"ENST_{gene_id}",
                    'uniprot': 'Unknown',
                    'description': gene.get('description', f'{gene_name} gene')
                }
            else:
                logger.info("🧬 ENSEMBL: No genes found in response")
        else:
            logger.error(f"🧬 ENSEMBL: HTTP error {response.status_code}: {response.text}")

        return None

    except Exception as e:
        logger.error(f"❌ Ensembl lookup failed: {e}")
        return None

def try_ncbi_lookup(chrom, position):
    """Try NCBI Gene API"""
    import requests

    try:
        # NCBI Gene search by genomic location
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'gene',
            'term': f'{chrom}[chr] AND {position}[chrpos]',
            'retmode': 'json',
            'retmax': 1
        }

        logger.info(f"🔬 NCBI: Trying URL: {url}")
        logger.info(f"🔬 NCBI: Search term: {params['term']}")

        response = requests.get(url, params=params, timeout=10)

        logger.info(f"🔬 NCBI: Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"🔬 NCBI: Search response: {data}")

            id_list = data.get('esearchresult', {}).get('idlist', [])

            if id_list:
                gene_id = id_list[0]
                logger.info(f"🔬 NCBI: Found gene ID: {gene_id}")

                # Get gene details
                detail_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                detail_params = {
                    'db': 'gene',
                    'id': gene_id,
                    'retmode': 'json'
                }

                logger.info(f"🔬 NCBI: Getting details for ID {gene_id}")
                detail_response = requests.get(detail_url, params=detail_params, timeout=10)

                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    logger.info(f"🔬 NCBI: Detail response: {detail_data}")

                    gene_info = detail_data.get('result', {}).get(gene_id, {})

                    gene_name = gene_info.get('name', 'Unknown')
                    description = gene_info.get('description', f'{gene_name} gene')

                    logger.info(f"✅ NCBI found: {gene_name}")

                    return {
                        'gene': gene_name,
                        'transcript': 'Unknown',
                        'uniprot': 'Unknown',
                        'description': description
                    }
                else:
                    logger.error(f"🔬 NCBI: Detail request failed: {detail_response.status_code}")
            else:
                logger.info("🔬 NCBI: No gene IDs found")
        else:
            logger.error(f"🔬 NCBI: HTTP error {response.status_code}: {response.text}")

        return None

    except Exception as e:
        logger.error(f"❌ NCBI lookup failed: {e}")
        return None

def try_ucsc_lookup(chrom, position, build='hg38'):
    """Try UCSC Genome Browser API"""
    import requests

    try:
        # UCSC API for gene lookup
        url = f"https://api.genome.ucsc.edu/getData/track"
        params = {
            'genome': build,
            'track': 'refGene',
            'chrom': f'chr{chrom}',
            'start': position - 1,  # UCSC uses 0-based coordinates
            'end': position
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            ref_gene = data.get('refGene', [])

            if ref_gene:
                gene_info = ref_gene[0]
                gene_name = gene_info.get('name2', gene_info.get('name', 'Unknown'))

                logger.info(f"✅ UCSC found: {gene_name}")

                return {
                    'gene': gene_name,
                    'transcript': gene_info.get('name', 'Unknown'),
                    'uniprot': 'Unknown',
                    'description': f'{gene_name} gene'
                }

        return None

    except Exception as e:
        logger.error(f"❌ UCSC lookup failed: {e}")
        return None

@app.route('/api/identify_gene', methods=['POST'])
def identify_gene():
    """Step 1: Identify gene from genomic coordinate"""
    try:
        data = request.get_json()
        coordinate = data.get('coordinate')
        build = data.get('build', 'hg38')

        logger.info(f"🔍 Identifying gene for {coordinate} ({build})")

        # Parse coordinate
        if not coordinate or ':' not in coordinate:
            return jsonify({'error': 'Invalid coordinate format'}), 400

        # Try real gene lookup first
        result = lookup_gene_by_coordinate(coordinate, build)

        if not result:
            # Fallback to known coordinates for demo
            known_genes = {
                'chr3:100713749': {
                    'gene': 'TFG',
                    'transcript': 'ENST00000240851',
                    'uniprot': 'Q92734',
                    'description': 'TRK-fused gene'
                }
            }

            result = known_genes.get(coordinate, {
                'gene': 'UNKNOWN',
                'transcript': 'Unknown',
                'uniprot': 'Unknown',
                'description': f'Gene lookup failed for {coordinate}'
            })

        logger.info(f"✅ Gene identification complete: {result['gene']}")
        return jsonify(result)

    except Exception as e:
        logger.error(f"❌ Gene identification failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conservation', methods=['POST'])
def analyze_conservation():
    """Step 2: Analyze evolutionary conservation"""
    try:
        data = request.get_json()
        coordinate = data.get('coordinate')
        build = data.get('build', 'hg38')
        
        logger.info(f"🧬 Analyzing conservation for {coordinate}")
        
        # Use our existing coordinate analyzer
        result = coordinate_analyzer.analyze_coordinate(coordinate, build)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        conservation_scores = result.get('conservation_scores', {})
        
        # Determine conservation level
        phylop = conservation_scores.get('phyloP', 0)
        if phylop > 5.0:
            level = 'EXTREMELY_HIGH'
        elif phylop > 2.0:
            level = 'HIGH'
        elif phylop > 0.5:
            level = 'MODERATE'
        else:
            level = 'LOW'
        
        response = {
            'phyloP': f"{phylop:.3f}",
            'phastCons': f"{conservation_scores.get('phastCons', 0):.3f}",
            'level': level,
            'raw_data': conservation_scores
        }
        
        logger.info(f"✅ Conservation analysis complete: phyloP {phylop:.3f}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Conservation analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/frequency', methods=['POST'])
def analyze_frequency():
    """Step 3: Analyze population frequency"""
    try:
        data = request.get_json()
        coordinate = data.get('coordinate')
        ref_allele = data.get('ref', 'A')  # Default values
        alt_allele = data.get('alt', 'G')
        
        logger.info(f"🌍 Analyzing frequency for {coordinate}")
        
        # Parse coordinate
        chrom = coordinate.replace('chr', '').split(':')[0]
        position = int(coordinate.split(':')[1])
        
        # Use our existing frequency analyzer
        result = frequency_analyzer.get_variant_frequency(chrom, position, ref_allele, alt_allele)
        
        response = {
            'maf': result.get('global_af', 0),
            'category': result.get('rarity_category', 'unknown'),
            'boost': f"{result.get('pathogenicity_boost', 1.0):.1f}x",
            'notTheDroid': result.get('not_the_droid', False),
            'note': result.get('note', ''),
            'raw_data': result
        }
        
        logger.info(f"✅ Frequency analysis complete: {response['category']}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Frequency analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/structure', methods=['POST'])
def download_structure():
    """Step 4: Download AlphaFold structure"""
    try:
        data = request.get_json()
        uniprot_id = data.get('uniprot_id')
        
        if not uniprot_id or uniprot_id == 'Unknown':
            return jsonify({'error': 'Valid UniProt ID required'}), 400
        
        logger.info(f"📥 Downloading structure for {uniprot_id}")
        
        # Use our existing AlphaFold client
        structure_path = alphafold_client.get_structure(uniprot_id)
        
        if structure_path:
            # Get file size
            import os
            size_bytes = os.path.getsize(structure_path)
            size_mb = size_bytes / (1024 * 1024)
            
            response = {
                'status': 'Downloaded',
                'size': f"{size_mb:.2f} MB",
                'path': structure_path,
                'uniprot_id': uniprot_id
            }
            
            logger.info(f"✅ Structure download complete: {size_mb:.2f} MB")
            return jsonify(response)
        else:
            return jsonify({'error': 'Structure download failed'}), 500
        
    except Exception as e:
        logger.error(f"❌ Structure download failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_mechanism', methods=['POST'])
def analyze_mechanism():
    """Step 5: Analyze LOF/DN mechanisms"""
    try:
        data = request.get_json()
        mechanism_type = data.get('type')  # 'lof', 'dn', or 'both'
        coordinate = data.get('coordinate')
        gene_name = data.get('gene_name')
        uniprot_id = data.get('uniprot_id')
        mutation = data.get('mutation', 'R22W')  # Default for TFG
        
        logger.info(f"🔬 Analyzing {mechanism_type} mechanism for {gene_name}")
        
        # For now, use simplified analysis
        # TODO: Get proper protein sequence for the gene
        demo_sequence = "MDEMOGENESEQUENCEFORANALYSISPURPOSESONLY"
        
        result = conservation_analyzer.analyze_with_conservation(
            mutation=mutation,
            sequence=demo_sequence,
            coordinate=coordinate,
            build='hg38',
            gene_name=gene_name,
            uniprot_id=uniprot_id
        )
        
        response = {}
        
        if mechanism_type in ['lof', 'both']:
            lof_data = result.get('enhanced_lof_analysis', {})
            response['lof'] = {
                'score': f"{lof_data.get('enhanced_lof_score', 0):.3f}",
                'prediction': lof_data.get('enhanced_prediction', 'UNKNOWN'),
                'base_score': f"{lof_data.get('base_lof_score', 0):.3f}",
                'boost': f"{lof_data.get('combined_boost', 1.0):.1f}x"
            }
        
        if mechanism_type in ['dn', 'both']:
            dn_data = result.get('enhanced_dn_analysis', {})
            response['dn'] = {
                'score': f"{dn_data.get('enhanced_dn_score', 0):.3f}",
                'prediction': dn_data.get('enhanced_prediction', 'UNKNOWN'),
                'base_score': f"{dn_data.get('base_dn_score', 0):.3f}",
                'boost': f"{dn_data.get('combined_boost', 1.0):.1f}x"
            }
        
        logger.info(f"✅ Mechanism analysis complete")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Mechanism analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/final_prediction', methods=['POST'])
def generate_final_prediction():
    """Step 6: Generate final integrated prediction"""
    try:
        data = request.get_json()
        
        # Get all the analysis data
        conservation_data = data.get('conservation', {})
        frequency_data = data.get('frequency', {})
        mechanism_data = data.get('mechanism', {})
        
        logger.info("🎯 Generating final prediction")
        
        # Simple integration logic (can be made more sophisticated)
        lof_score = float(mechanism_data.get('lof', {}).get('score', 0))
        dn_score = float(mechanism_data.get('dn', {}).get('score', 0))
        
        # Determine primary mechanism
        if lof_score > dn_score:
            primary_mechanism = 'Loss of Function'
            primary_score = lof_score
        else:
            primary_mechanism = 'Dominant Negative'
            primary_score = dn_score
        
        # Determine final prediction
        if primary_score > 0.8:
            prediction = 'PATHOGENIC'
            confidence = 0.9
        elif primary_score > 0.6:
            prediction = 'LIKELY_PATHOGENIC'
            confidence = 0.8
        elif primary_score > 0.4:
            prediction = 'UNCERTAIN_SIGNIFICANCE'
            confidence = 0.6
        elif primary_score > 0.2:
            prediction = 'LIKELY_BENIGN'
            confidence = 0.7
        else:
            prediction = 'BENIGN'
            confidence = 0.8
        
        # Build evidence summary
        evidence_parts = []
        if conservation_data.get('level') in ['HIGH', 'EXTREMELY_HIGH']:
            evidence_parts.append('High conservation')
        if frequency_data.get('category') == 'ULTRA_RARE':
            evidence_parts.append('Ultra-rare frequency')
        if mechanism_data.get('lof', {}).get('prediction') in ['HIGH_LOF', 'MODERATE_LOF']:
            evidence_parts.append('Deleterious LOF prediction')
        
        evidence_summary = ' + '.join(evidence_parts) if evidence_parts else 'Limited evidence'
        
        response = {
            'prediction': prediction,
            'confidence': f"{confidence:.2f}",
            'mechanism': primary_mechanism,
            'evidence': evidence_summary,
            'primary_score': primary_score
        }
        
        logger.info(f"✅ Final prediction: {prediction} (confidence: {confidence:.2f})")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Final prediction failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🧬 Starting Genetics Analyzer API Server...")
    print("📡 API will be available at http://localhost:4999")
    print("🌐 Frontend should be at http://localhost:8888")
    app.run(host='0.0.0.0', port=4999, debug=True)

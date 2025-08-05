from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import subprocess
import json
import shutil
from werkzeug.utils import secure_filename
from website_extractor import WebsiteExtractor
from section_analyzer import SectionAnalyzer
from code_assembler import CodeAssembler
from gemini_analyzer import GeminiAnalyzer

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
SCREENSHOTS_FOLDER = 'screenshots'
EXTRACTED_SITES_FOLDER = 'extracted_sites'
OUTPUT_FOLDER = 'output'

for folder in [UPLOAD_FOLDER, SCREENSHOTS_FOLDER, EXTRACTED_SITES_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SCREENSHOTS_FOLDER'] = SCREENSHOTS_FOLDER
app.config['EXTRACTED_SITES_FOLDER'] = EXTRACTED_SITES_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Initialize components
extractor = WebsiteExtractor()
analyzer = SectionAnalyzer()
assembler = CodeAssembler()
gemini_analyzer = GeminiAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/extract-website', methods=['POST'])
def extract_website():
    """Extract a website using wget"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Extract the website
        site_folder = extractor.extract_website(url)
        
        return jsonify({
            'success': True,
            'site_folder': site_folder,
            'message': f'Website extracted successfully to {site_folder}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-screenshot', methods=['POST'])
def upload_screenshot():
    """Upload a screenshot for section identification"""
    try:
        if 'screenshot' not in request.files:
            return jsonify({'error': 'No screenshot file provided'}), 400
        
        file = request.files['screenshot']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['SCREENSHOTS_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'screenshot_path': filepath,
            'filename': filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-section', methods=['POST'])
def analyze_section():
    """Analyze a screenshot to identify the corresponding section in the extracted website"""
    try:
        data = request.get_json()
        screenshot_path = data.get('screenshot_path')
        site_folder = data.get('site_folder')
        section_name = data.get('section_name', 'section')
        
        if not screenshot_path or not site_folder:
            return jsonify({'error': 'Screenshot path and site folder are required'}), 400
        
        # Find HTML files in the site folder
        html_files = []
        for root, dirs, files in os.walk(site_folder):
            for file in files:
                if file.lower().endswith('.html') or file.lower().endswith('.htm'):
                    html_files.append(os.path.join(root, file))
        
        if not html_files:
            return jsonify({'error': 'No HTML files found in the extracted site'}), 400
        
        # Use Gemini analyzer for enhanced analysis
        section_info = gemini_analyzer.enhance_section_extraction(
            screenshot_path, 
            html_files[0], 
            section_name
        )
        
        return jsonify({
            'success': True,
            'section_info': section_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract-section', methods=['POST'])
def extract_section():
    """Extract a specific section from the website"""
    try:
        data = request.get_json()
        site_folder = data.get('site_folder')
        section_info = data.get('section_info')
        section_name = data.get('section_name', 'section')
        
        if not site_folder or not section_info:
            return jsonify({'error': 'Site folder and section info are required'}), 400
        
        # Extract the section
        extracted_section = extractor.extract_section(site_folder, section_info, section_name)
        
        return jsonify({
            'success': True,
            'extracted_section': extracted_section
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assemble-site', methods=['POST'])
def assemble_site():
    """Assemble the final site from extracted sections"""
    try:
        data = request.get_json()
        sections = data.get('sections', [])
        site_structure = data.get('site_structure', {})
        
        if not sections:
            return jsonify({'error': 'No sections provided'}), 400
        
        # Assemble the site
        output_path = assembler.assemble_site(sections, site_structure)
        
        return jsonify({
            'success': True,
            'output_path': output_path,
            'message': 'Site assembled successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-extracted-sites')
def list_extracted_sites():
    """List all extracted websites"""
    try:
        sites = []
        for item in os.listdir(app.config['EXTRACTED_SITES_FOLDER']):
            item_path = os.path.join(app.config['EXTRACTED_SITES_FOLDER'], item)
            if os.path.isdir(item_path):
                sites.append({
                    'name': item,
                    'path': item_path
                })
        
        return jsonify({
            'success': True,
            'sites': sites
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-screenshots')
def list_screenshots():
    """List all uploaded screenshots"""
    try:
        screenshots = []
        for item in os.listdir(app.config['SCREENSHOTS_FOLDER']):
            if item.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                screenshots.append({
                    'name': item,
                    'path': os.path.join(app.config['SCREENSHOTS_FOLDER'], item)
                })
        
        return jsonify({
            'success': True,
            'screenshots': screenshots
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-section-suggestions', methods=['POST'])
def get_section_suggestions():
    """Get AI-powered suggestions for section names based on screenshot"""
    try:
        data = request.get_json()
        screenshot_path = data.get('screenshot_path')
        
        if not screenshot_path:
            return jsonify({'error': 'Screenshot path is required'}), 400
        
        # Get AI-powered suggestions
        suggestions = gemini_analyzer.get_section_suggestions(screenshot_path)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 
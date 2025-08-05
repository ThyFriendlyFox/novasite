#!/usr/bin/env python3
"""
Demo script for the Website Section Extractor system.
This script demonstrates how to use the system programmatically.
"""

import os
import sys
import tempfile
import shutil

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from website_extractor import WebsiteExtractor
from section_analyzer import SectionAnalyzer
from code_assembler import CodeAssembler

def create_demo_site():
    """Create a demo website for testing"""
    demo_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Site</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { background: #667eea; color: white; padding: 20px; text-align: center; }
        .hero { background: #f8f9fa; padding: 40px; text-align: center; }
        .content { padding: 20px; }
        .footer { background: #333; color: white; padding: 20px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Demo Website Header</h1>
        <p>This is the header section</p>
    </div>
    
    <div class="hero">
        <h2>Hero Section</h2>
        <p>This is the main hero content</p>
        <button>Call to Action</button>
    </div>
    
    <div class="content">
        <h3>Main Content</h3>
        <p>This is the main content section with lots of text and information.</p>
        <p>It contains multiple paragraphs and various content elements.</p>
    </div>
    
    <div class="footer">
        <p>&copy; 2024 Demo Site. All rights reserved.</p>
    </div>
</body>
</html>"""
    
    return demo_html

def demo_extraction_process():
    """Demonstrate the extraction process"""
    print("🚀 Website Section Extractor Demo")
    print("=" * 50)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        extracted_sites_dir = os.path.join(temp_dir, "extracted_sites")
        screenshots_dir = os.path.join(temp_dir, "screenshots")
        output_dir = os.path.join(temp_dir, "output")
        
        os.makedirs(extracted_sites_dir, exist_ok=True)
        os.makedirs(screenshots_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize components
        extractor = WebsiteExtractor(extracted_sites_folder=extracted_sites_dir)
        analyzer = SectionAnalyzer()
        assembler = CodeAssembler(output_folder=output_dir)
        
        print("1. Creating demo website...")
        demo_site_dir = os.path.join(extracted_sites_dir, "demo_site")
        os.makedirs(demo_site_dir, exist_ok=True)
        
        # Create demo HTML file
        demo_html = create_demo_site()
        demo_html_path = os.path.join(demo_site_dir, "index.html")
        with open(demo_html_path, 'w', encoding='utf-8') as f:
            f.write(demo_html)
        
        print(f"   ✅ Demo site created at: {demo_site_dir}")
        
        # Simulate section analysis (in real usage, this would use actual screenshots)
        print("\n2. Analyzing sections...")
        
        # Create mock section info (in real usage, this comes from screenshot analysis)
        sections = [
            {
                'section_name': 'header',
                'section_folder': os.path.join(temp_dir, 'sections', 'header'),
                'html_file': demo_html_path,
                'css_selector': '.header',
                'css_files': [],
                'js_files': []
            },
            {
                'section_name': 'hero',
                'section_folder': os.path.join(temp_dir, 'sections', 'hero'),
                'html_file': demo_html_path,
                'css_selector': '.hero',
                'css_files': [],
                'js_files': []
            },
            {
                'section_name': 'footer',
                'section_folder': os.path.join(temp_dir, 'sections', 'footer'),
                'html_file': demo_html_path,
                'css_selector': '.footer',
                'css_files': [],
                'js_files': []
            }
        ]
        
        # Create section folders and extract sections
        for section in sections:
            section_folder = section['section_folder']
            os.makedirs(section_folder, exist_ok=True)
            
            # Extract the section HTML
            with open(section['html_file'], 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the section element
            section_element = soup.select_one(section['css_selector'])
            if section_element:
                # Create section HTML
                section_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{section['section_name'].title()} Section</title>
</head>
<body>
    {str(section_element)}
</body>
</html>"""
                
                # Save section HTML
                section_html_path = os.path.join(section_folder, 'section.html')
                with open(section_html_path, 'w', encoding='utf-8') as f:
                    f.write(section_html)
                
                print(f"   ✅ Extracted {section['section_name']} section")
        
        print("\n3. Assembling final website...")
        
        # Define site structure
        site_structure = {
            'title': 'My Assembled Website',
            'section_order': ['header', 'hero', 'footer']
        }
        
        # Assemble the site
        output_path = assembler.assemble_site(sections, site_structure)
        
        print(f"   ✅ Website assembled at: {output_path}")
        
        # Show the final result
        print("\n4. Final Result:")
        print(f"   📁 Output directory: {output_path}")
        print(f"   📄 Main HTML file: {os.path.join(output_path, 'index.html')}")
        print(f"   📋 README file: {os.path.join(output_path, 'README.md')}")
        
        # List files in output directory
        print("\n   📂 Files created:")
        for root, dirs, files in os.walk(output_path):
            level = root.replace(output_path, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}📁 {os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}📄 {file}")
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo use the full system with real websites:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:8080")
        print("3. Follow the web interface to extract real websites")

if __name__ == "__main__":
    try:
        demo_extraction_process()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1) 
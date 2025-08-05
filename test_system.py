#!/usr/bin/env python3
"""
Test script for the Website Section Extractor system.
This script tests the core components without requiring a full website extraction.
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from website_extractor import WebsiteExtractor
from section_analyzer import SectionAnalyzer
from code_assembler import CodeAssembler

def test_website_extractor():
    """Test the WebsiteExtractor class"""
    print("🧪 Testing WebsiteExtractor...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        extractor = WebsiteExtractor(extracted_sites_folder=temp_dir)
        
        # Test that the extractor can be initialized
        assert extractor.extracted_sites_folder == temp_dir
        print("✅ WebsiteExtractor initialization passed")
        
        # Test CSS link generation
        css_files = ['/css/style.css', '/css/main.css']
        css_links = extractor._generate_css_links(css_files)
        assert 'style.css' in css_links
        assert 'main.css' in css_links
        print("✅ CSS link generation passed")
        
        # Test JS link generation
        js_files = ['/js/app.js', '/js/main.js']
        js_links = extractor._generate_js_links(js_files)
        assert 'app.js' in js_links
        assert 'main.js' in js_links
        print("✅ JS link generation passed")

def test_section_analyzer():
    """Test the SectionAnalyzer class"""
    print("🧪 Testing SectionAnalyzer...")
    
    # Mock the Selenium setup to avoid Chrome dependency
    with patch('section_analyzer.ChromeDriverManager') as mock_driver_manager:
        mock_driver_manager.return_value.install.return_value = '/fake/chromedriver'
        
        analyzer = SectionAnalyzer()
        
        # Test text similarity calculation
        similarity = analyzer._calculate_text_similarity("hello world", "hello world test")
        assert 0 < similarity < 1
        print("✅ Text similarity calculation passed")
        
        # Test CSS selector generation
        from bs4 import BeautifulSoup
        html = '<div id="test" class="container">Content</div>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div')
        
        selector = analyzer._generate_css_selector(element)
        assert selector == '#test'
        print("✅ CSS selector generation passed")

def test_code_assembler():
    """Test the CodeAssembler class"""
    print("🧪 Testing CodeAssembler...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        assembler = CodeAssembler(output_folder=temp_dir)
        
        # Test that the assembler can be initialized
        assert assembler.output_folder == temp_dir
        print("✅ CodeAssembler initialization passed")
        
        # Test HTML template creation
        sections = []
        site_structure = {'title': 'Test Site'}
        html = assembler._create_main_html(sections, site_structure)
        assert 'Test Site' in html
        assert '<html' in html
        assert '</html>' in html
        print("✅ HTML template creation passed")

def test_flask_app():
    """Test that the Flask app can be imported"""
    print("🧪 Testing Flask app...")
    
    try:
        from app import app
        assert app is not None
        print("✅ Flask app import passed")
    except ImportError as e:
        print(f"❌ Flask app import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Website Section Extractor Tests\n")
    
    tests = [
        test_website_extractor,
        test_section_analyzer,
        test_code_assembler,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
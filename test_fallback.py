#!/usr/bin/env python3
"""
Test script to verify the fallback method works when wget fails
"""

import os
import sys
import tempfile
import shutil

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from website_extractor import WebsiteExtractor

def test_fallback_method():
    """Test the fallback method using Python requests"""
    print("🧪 Testing Website Extractor Fallback Method...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        extractor = WebsiteExtractor(extracted_sites_folder=temp_dir)
        
        # Test with a simple website that should work
        test_url = "https://httpbin.org/html"
        
        try:
            print(f"Testing with URL: {test_url}")
            site_folder = extractor._extract_with_requests(test_url, os.path.join(temp_dir, "test_site"))
            
            # Check if files were created
            if os.path.exists(site_folder):
                files = os.listdir(site_folder)
                print(f"✅ Fallback method created files: {files}")
                
                # Check if index.html exists
                index_file = os.path.join(site_folder, "index.html")
                if os.path.exists(index_file):
                    with open(index_file, 'r') as f:
                        content = f.read()
                    print(f"✅ HTML content length: {len(content)} characters")
                    return True
                else:
                    print("❌ index.html not found")
                    return False
            else:
                print("❌ Site folder not created")
                return False
                
        except Exception as e:
            print(f"❌ Fallback method failed: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Testing Website Extractor Fallback Method")
    print("=" * 50)
    
    success = test_fallback_method()
    
    if success:
        print("\n🎉 Fallback method test passed!")
        print("The system can handle websites that block wget requests.")
    else:
        print("\n❌ Fallback method test failed!")
        print("There may be an issue with the requests-based fallback.")
    
    print("\n💡 The system now has:")
    print("• Enhanced wget with user agent headers")
    print("• Python requests fallback method")
    print("• Better error messages and suggestions")
    print("• Example URLs for testing") 
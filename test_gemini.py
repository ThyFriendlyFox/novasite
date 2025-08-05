#!/usr/bin/env python3
"""
Test script for Gemini API integration.
"""

import os
import sys
from gemini_analyzer import GeminiAnalyzer

def test_gemini_analyzer():
    """Test the GeminiAnalyzer class"""
    print("🧪 Testing GeminiAnalyzer...")
    
    # Test without API key (fallback mode)
    analyzer = GeminiAnalyzer()
    
    # Test fallback analysis
    result = analyzer._fallback_analysis("test_screenshot.jpg", "<html><body><div class='header'>Test</div></body></html>", "header")
    
    assert result['css_selector'] is not None
    assert result['confidence'] == 0.3
    assert result['method'] == 'fallback'
    
    print("✅ GeminiAnalyzer fallback mode working")
    
    # Test with API key (if available)
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print("🔑 Testing with Gemini API key...")
        analyzer_with_key = GeminiAnalyzer(api_key)
        
        # Test section suggestions
        suggestions = analyzer_with_key.get_section_suggestions("test_screenshot.jpg")
        assert isinstance(suggestions, list)
        
        print("✅ GeminiAnalyzer with API key working")
    else:
        print("⚠️  No GEMINI_API_KEY found. Install with: export GEMINI_API_KEY='your_key_here'")
    
    print("🎉 Gemini integration test completed!")

if __name__ == "__main__":
    test_gemini_analyzer() 
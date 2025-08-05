import os
import base64
from PIL import Image
import io
import json
from bs4 import BeautifulSoup
import re

# Try to import the new Google GenAI SDK, but handle gracefully if not available
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("Warning: google-genai not available. Install with: pip install google-genai")
    GEMINI_AVAILABLE = False

class GeminiAnalyzer:
    def __init__(self, api_key=None):
        """Initialize Gemini analyzer with API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not GEMINI_AVAILABLE:
            print("Warning: google-genai not available. Using fallback analysis methods.")
            self.client = None
        elif self.api_key:
            try:
                # Set the API key as environment variable for the new SDK
                os.environ['GEMINI_API_KEY'] = self.api_key
                self.client = genai.Client()
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
                self.client = None
        else:
            print("Warning: No Gemini API key provided. Using fallback analysis methods.")
            self.client = None
    
    def analyze_screenshot_with_gemini(self, screenshot_path, html_content, section_name):
        """Use Gemini to analyze screenshot and identify the corresponding section"""
        try:
            if not self.client:
                return self._fallback_analysis(screenshot_path, html_content, section_name)
            
            # Load and encode the screenshot
            with open(screenshot_path, 'rb') as img_file:
                image_data = img_file.read()
            
            # Create the prompt for Gemini
            prompt = self._create_analysis_prompt(html_content, section_name)
            
            # Generate response from Gemini using the new SDK
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_data}
                ]
            )
            
            # Parse the response
            analysis_result = self._parse_gemini_response(response.text)
            
            return analysis_result
            
        except Exception as e:
            print(f"Gemini analysis failed: {e}")
            return self._fallback_analysis(screenshot_path, html_content, section_name)
    
    def _create_analysis_prompt(self, html_content, section_name):
        """Create a detailed prompt for Gemini analysis"""
        return f"""
You are an expert web developer analyzing a screenshot of a website section. Your task is to identify which HTML element in the provided HTML code corresponds to the section shown in the screenshot.

HTML Content:
{html_content[:2000]}...

Section Name: {section_name}

Instructions:
1. Look at the screenshot carefully and identify the visual elements, text content, and layout
2. Find the corresponding HTML element in the code that creates this section
3. Provide a CSS selector that uniquely identifies this section
4. If you can't find an exact match, provide the best approximation

Please respond in JSON format with the following structure:
{{
    "css_selector": "the CSS selector for the section",
    "confidence": 0.95,
    "reasoning": "explanation of why this selector was chosen",
    "section_type": "header|hero|content|footer|sidebar|etc",
    "text_content": "key text found in the section",
    "visual_elements": ["list", "of", "visual", "elements", "found"]
}}

Focus on finding the most specific and reliable CSS selector that will extract exactly the section shown in the screenshot.
"""
    
    def _parse_gemini_response(self, response_text):
        """Parse Gemini's response and extract the analysis results"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                return {
                    'css_selector': result.get('css_selector', 'body'),
                    'confidence': result.get('confidence', 0.5),
                    'reasoning': result.get('reasoning', 'Gemini analysis'),
                    'section_type': result.get('section_type', 'unknown'),
                    'text_content': result.get('text_content', ''),
                    'visual_elements': result.get('visual_elements', []),
                    'method': 'gemini_ai'
                }
            else:
                # Fallback parsing if JSON extraction fails
                return self._parse_text_response(response_text)
                
        except Exception as e:
            print(f"Failed to parse Gemini response: {e}")
            return self._parse_text_response(response_text)
    
    def _parse_text_response(self, response_text):
        """Parse text response when JSON parsing fails"""
        # Look for CSS selectors in the text
        css_selectors = re.findall(r'[.#][a-zA-Z0-9_-]+', response_text)
        
        return {
            'css_selector': css_selectors[0] if css_selectors else 'body',
            'confidence': 0.7,
            'reasoning': 'Gemini analysis (text parsing)',
            'section_type': 'unknown',
            'text_content': '',
            'visual_elements': [],
            'method': 'gemini_ai_text'
        }
    
    def _fallback_analysis(self, screenshot_path, html_content, section_name):
        """Fallback analysis when Gemini is not available"""
        from section_analyzer import SectionAnalyzer
        
        analyzer = SectionAnalyzer()
        
        # Create a mock screenshot analysis
        return {
            'css_selector': f'.{section_name}, #{section_name}, [class*="{section_name}"]',
            'confidence': 0.3,
            'reasoning': 'Fallback analysis - no Gemini API key provided',
            'section_type': section_name,
            'text_content': '',
            'visual_elements': [],
            'method': 'fallback'
        }
    
    def enhance_section_extraction(self, screenshot_path, html_file, section_name):
        """Enhanced section extraction using Gemini analysis"""
        try:
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Analyze with Gemini
            analysis = self.analyze_screenshot_with_gemini(screenshot_path, html_content, section_name)
            
            # Parse HTML to find the section
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try the Gemini-provided selector
            section_element = soup.select_one(analysis['css_selector'])
            
            if not section_element:
                # Try alternative selectors
                alternative_selectors = [
                    f'.{section_name}',
                    f'#{section_name}',
                    f'[class*="{section_name}"]',
                    'main',
                    'section',
                    'article'
                ]
                
                for selector in alternative_selectors:
                    section_element = soup.select_one(selector)
                    if section_element:
                        analysis['css_selector'] = selector
                        analysis['confidence'] = max(0.1, analysis['confidence'] - 0.2)
                        break
            
            if not section_element:
                section_element = soup.find('body')
                analysis['css_selector'] = 'body'
                analysis['confidence'] = 0.1
            
            return {
                'html_file': html_file,
                'css_selector': analysis['css_selector'],
                'confidence': analysis['confidence'],
                'method': analysis['method'],
                'reasoning': analysis['reasoning'],
                'section_type': analysis['section_type'],
                'element_text': section_element.get_text(strip=True)[:200] if section_element else '',
                'notes': f"Gemini analysis: {analysis.get('reasoning', 'No reasoning provided')}"
            }
            
        except Exception as e:
            print(f"Enhanced extraction failed: {e}")
            return {
                'html_file': html_file,
                'css_selector': 'body',
                'confidence': 0.1,
                'method': 'error_fallback',
                'reasoning': f'Error in enhanced extraction: {str(e)}',
                'section_type': section_name,
                'element_text': '',
                'notes': 'Error occurred during analysis'
            }
    
    def get_section_suggestions(self, screenshot_path):
        """Get AI-powered suggestions for section names based on screenshot content"""
        try:
            if not self.client:
                return ['section', 'content', 'main']
            
            # Load and encode the screenshot
            with open(screenshot_path, 'rb') as img_file:
                image_data = img_file.read()
            
            prompt = """
Look at this screenshot of a website section and suggest appropriate names for this section.
Consider common web development naming conventions.

Respond with a JSON array of 3-5 suggested names, ordered by relevance:
["header", "navigation", "nav"]

Focus on descriptive, semantic names that web developers would use.
"""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_data}
                ]
            )
            
            # Parse suggestions
            suggestions_match = re.search(r'\[.*\]', response.text)
            if suggestions_match:
                suggestions = json.loads(suggestions_match.group())
                return suggestions
            else:
                return ['header', 'content', 'section']
                
        except Exception as e:
            print(f"Failed to get section suggestions: {e}")
            return ['header', 'content', 'section'] 
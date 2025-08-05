import cv2
import numpy as np
from PIL import Image
import os
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class SectionAnalyzer:
    def __init__(self):
        self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver for screenshot comparison"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Warning: Could not setup Selenium: {e}")
            self.driver = None
    
    def analyze_section(self, screenshot_path, site_folder):
        """Analyze a screenshot to identify the corresponding section in the extracted website"""
        try:
            # Load the screenshot
            screenshot = cv2.imread(screenshot_path)
            if screenshot is None:
                raise Exception(f"Could not load screenshot: {screenshot_path}")
            
            # Find HTML files in the site folder
            html_files = self._find_html_files(site_folder)
            
            # For each HTML file, try to match the screenshot
            best_match = None
            best_score = 0
            
            for html_file in html_files:
                match_info = self._analyze_html_file(html_file, screenshot)
                if match_info and match_info.get('confidence', 0) > best_score:
                    best_score = match_info['confidence']
                    best_match = match_info
            
            if best_match:
                return best_match
            else:
                # Fallback: return basic info about the first HTML file
                if html_files:
                    return {
                        'html_file': html_files[0],
                        'confidence': 0.1,
                        'method': 'fallback',
                        'css_selector': 'body',
                        'notes': 'Could not find exact match, using fallback'
                    }
                else:
                    raise Exception("No HTML files found in the extracted site")
            
        except Exception as e:
            print(f"Error analyzing section: {str(e)}")
            raise
    
    def _find_html_files(self, site_folder):
        """Find all HTML files in the site folder"""
        html_files = []
        
        for root, dirs, files in os.walk(site_folder):
            for file in files:
                if file.lower().endswith('.html') or file.lower().endswith('.htm'):
                    html_files.append(os.path.join(root, file))
        
        return html_files
    
    def _analyze_html_file(self, html_file, screenshot):
        """Analyze a single HTML file against the screenshot"""
        try:
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try different methods to find the section
            methods = [
                self._analyze_by_visual_elements,
                self._analyze_by_text_content,
                self._analyze_by_structure
            ]
            
            best_result = None
            best_confidence = 0
            
            for method in methods:
                try:
                    result = method(soup, screenshot, html_file)
                    if result and result.get('confidence', 0) > best_confidence:
                        best_confidence = result['confidence']
                        best_result = result
                except Exception as e:
                    print(f"Method {method.__name__} failed: {e}")
                    continue
            
            return best_result
            
        except Exception as e:
            print(f"Error analyzing HTML file {html_file}: {e}")
            return None
    
    def _analyze_by_visual_elements(self, soup, screenshot, html_file):
        """Analyze by looking for visual elements that might match the screenshot"""
        try:
            # Extract text content from the screenshot using OCR (simplified)
            # In a real implementation, you'd use Tesseract or similar OCR
            screenshot_text = self._extract_text_from_screenshot(screenshot)
            
            # Find elements with similar text content
            matching_elements = []
            
            for element in soup.find_all(['div', 'section', 'article', 'main']):
                element_text = element.get_text(strip=True)
                if element_text and len(element_text) > 10:
                    # Simple text similarity (in practice, use more sophisticated methods)
                    similarity = self._calculate_text_similarity(screenshot_text, element_text)
                    if similarity > 0.3:  # Threshold
                        matching_elements.append({
                            'element': element,
                            'similarity': similarity,
                            'text': element_text[:100]  # First 100 chars
                        })
            
            if matching_elements:
                # Sort by similarity
                matching_elements.sort(key=lambda x: x['similarity'], reverse=True)
                best_match = matching_elements[0]
                
                return {
                    'html_file': html_file,
                    'confidence': best_match['similarity'],
                    'method': 'visual_elements',
                    'css_selector': self._generate_css_selector(best_match['element']),
                    'element_text': best_match['text'],
                    'notes': f"Found {len(matching_elements)} potential matches"
                }
            
            return None
            
        except Exception as e:
            print(f"Error in visual analysis: {e}")
            return None
    
    def _analyze_by_text_content(self, soup, screenshot, html_file):
        """Analyze by comparing text content"""
        try:
            # Extract all text from the HTML
            html_text = soup.get_text(strip=True)
            
            # Extract text from screenshot (simplified)
            screenshot_text = self._extract_text_from_screenshot(screenshot)
            
            # Calculate similarity
            similarity = self._calculate_text_similarity(screenshot_text, html_text)
            
            if similarity > 0.2:  # Lower threshold for text-based matching
                return {
                    'html_file': html_file,
                    'confidence': similarity,
                    'method': 'text_content',
                    'css_selector': 'body',
                    'notes': f"Text similarity: {similarity:.2f}"
                }
            
            return None
            
        except Exception as e:
            print(f"Error in text analysis: {e}")
            return None
    
    def _analyze_by_structure(self, soup, screenshot, html_file):
        """Analyze by looking at the structure of the HTML"""
        try:
            # Look for common section containers
            section_selectors = [
                'main',
                'section',
                'article',
                '.container',
                '.content',
                '.main-content',
                '#content',
                '#main'
            ]
            
            for selector in section_selectors:
                elements = soup.select(selector)
                if elements:
                    return {
                        'html_file': html_file,
                        'confidence': 0.5,
                        'method': 'structure',
                        'css_selector': selector,
                        'notes': f"Found section using selector: {selector}"
                    }
            
            return None
            
        except Exception as e:
            print(f"Error in structure analysis: {e}")
            return None
    
    def _extract_text_from_screenshot(self, screenshot):
        """Extract text from screenshot (simplified - in practice use OCR)"""
        # This is a placeholder - in a real implementation, you'd use OCR
        # For now, we'll return a placeholder text
        return "screenshot_text_placeholder"
    
    def _calculate_text_similarity(self, text1, text2):
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0
        
        # Simple similarity calculation
        # In practice, you'd use more sophisticated methods like cosine similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0
    
    def _generate_css_selector(self, element):
        """Generate a CSS selector for an element"""
        try:
            # Try to generate a unique selector
            if element.get('id'):
                return f"#{element['id']}"
            elif element.get('class'):
                classes = ' '.join(element['class'])
                return f".{classes.replace(' ', '.')}"
            else:
                # Fallback to tag name
                return element.name
        except:
            return 'body'
    
    def __del__(self):
        """Cleanup Selenium driver"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass 
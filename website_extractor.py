import os
import subprocess
import shutil
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests

class WebsiteExtractor:
    def __init__(self, extracted_sites_folder='extracted_sites'):
        self.extracted_sites_folder = extracted_sites_folder
        os.makedirs(extracted_sites_folder, exist_ok=True)
    
    def extract_website(self, url):
        """Extract a website using wget command with fallback to requests"""
        try:
            # Parse URL to get domain name for folder
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('.', '_')
            
            # Create folder for this site
            site_folder = os.path.join(self.extracted_sites_folder, domain)
            if os.path.exists(site_folder):
                shutil.rmtree(site_folder)
            
            os.makedirs(site_folder, exist_ok=True)
            
            # Try wget first
            try:
                return self._extract_with_wget(url, site_folder)
            except Exception as wget_error:
                print(f"Wget failed: {wget_error}")
                print("Trying fallback method with Python requests...")
                return self._extract_with_requests(url, site_folder)
            
        except Exception as e:
            print(f"Error extracting website: {str(e)}")
            raise
    
    def _extract_with_wget(self, url, site_folder):
        """Extract website using wget command"""
        # Run wget command with user agent and additional options to avoid 403 errors
        wget_command = [
            'wget',
            '--mirror',
            '--convert-links',
            '--adjust-extension',
            '--page-requisites',
            '--no-parent',
            '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--header=Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            '--header=Accept-Language: en-US,en;q=0.5',
            '--header=Accept-Encoding: gzip, deflate',
            '--header=Connection: keep-alive',
            '--header=Upgrade-Insecure-Requests: 1',
            '--timeout=30',
            '--tries=3',
            '--retry-connrefused',
            '--directory-prefix', site_folder,
            url
        ]
        
        print(f"Running wget command: {' '.join(wget_command)}")
        
        result = subprocess.run(
            wget_command,
            capture_output=True,
            text=True,
            cwd=site_folder
        )
        
        if result.returncode != 0:
            print(f"Wget stderr: {result.stderr}")
            
            # Check if it's a 403 error and provide helpful message
            if "403 Forbidden" in result.stderr:
                raise Exception(
                    f"Website blocked the request (403 Forbidden). This website may have anti-bot protection. "
                    f"Error details: {result.stderr}"
                )
            elif "404 Not Found" in result.stderr:
                raise Exception(
                    f"Website not found (404). Please check the URL and try again. "
                    f"Error details: {result.stderr}"
                )
            elif "Connection refused" in result.stderr:
                raise Exception(
                    f"Connection refused. The website may be down or blocking requests. "
                    f"Error details: {result.stderr}"
                )
            else:
                raise Exception(f"Wget failed with return code {result.returncode}. Error: {result.stderr}")
        
        print(f"Website extracted successfully to {site_folder}")
        return site_folder
    
    def _extract_with_requests(self, url, site_folder):
        """Fallback method using Python requests library"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            print(f"Downloading website using Python requests: {url}")
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Ensure the site folder exists
            os.makedirs(site_folder, exist_ok=True)
            
            # Save the main HTML file
            index_file = os.path.join(site_folder, 'index.html')
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"Website downloaded successfully to {site_folder} (fallback method)")
            return site_folder
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                raise Exception(
                    f"Website blocked the request (403 Forbidden). This website has anti-bot protection. "
                    f"Try a different website or contact the site administrator."
                )
            elif e.response.status_code == 404:
                raise Exception(
                    f"Website not found (404). Please check the URL and try again."
                )
            else:
                raise Exception(f"HTTP error {e.response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {e}")
    
    def extract_section(self, site_folder, section_info, section_name):
        """Extract a specific section from the website"""
        try:
            # Create output folder for this section
            section_folder = os.path.join('extracted_sections', section_name)
            os.makedirs(section_folder, exist_ok=True)
            
            # Get the HTML file that contains the section
            html_file = section_info.get('html_file')
            if not html_file:
                raise Exception("No HTML file specified in section info")
            
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract the specific section based on section_info
            section_element = self._find_section_element(soup, section_info)
            
            if not section_element:
                raise Exception("Could not find the specified section")
            
            # Extract CSS and JS dependencies
            css_files = self._extract_css_dependencies(soup, site_folder)
            js_files = self._extract_js_dependencies(soup, site_folder)
            
            # Create the extracted section HTML
            extracted_html = self._create_section_html(section_element, css_files, js_files)
            
            # Save the extracted section
            section_html_file = os.path.join(section_folder, 'section.html')
            with open(section_html_file, 'w', encoding='utf-8') as f:
                f.write(extracted_html)
            
            # Copy CSS files
            css_folder = os.path.join(section_folder, 'css')
            os.makedirs(css_folder, exist_ok=True)
            for css_file in css_files:
                if os.path.exists(css_file):
                    filename = os.path.basename(css_file)
                    shutil.copy2(css_file, os.path.join(css_folder, filename))
            
            # Copy JS files
            js_folder = os.path.join(section_folder, 'js')
            os.makedirs(js_folder, exist_ok=True)
            for js_file in js_files:
                if os.path.exists(js_file):
                    filename = os.path.basename(js_file)
                    shutil.copy2(js_file, os.path.join(js_folder, filename))
            
            return {
                'section_folder': section_folder,
                'html_file': section_html_file,
                'css_files': css_files,
                'js_files': js_files,
                'section_name': section_name
            }
            
        except Exception as e:
            print(f"Error extracting section: {str(e)}")
            raise
    
    def _find_section_element(self, soup, section_info):
        """Find the section element based on section_info"""
        # This is a simplified version - in practice, you'd use more sophisticated
        # image analysis and DOM matching techniques
        
        # Try to find by CSS selector if provided
        if 'css_selector' in section_info:
            element = soup.select_one(section_info['css_selector'])
            if element:
                return element
        
        # Try to find by class name
        if 'class_name' in section_info:
            element = soup.find(class_=section_info['class_name'])
            if element:
                return element
        
        # Try to find by ID
        if 'element_id' in section_info:
            element = soup.find(id=section_info['element_id'])
            if element:
                return element
        
        # Fallback: return the body or a main container
        return soup.find('body') or soup.find('main') or soup.find('div', class_='container')
    
    def _extract_css_dependencies(self, soup, site_folder):
        """Extract CSS file dependencies"""
        css_files = []
        
        # Find all link tags with CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                # Resolve relative paths
                if href.startswith('/'):
                    css_path = os.path.join(site_folder, href[1:])
                elif href.startswith('http'):
                    # Skip external CSS for now
                    continue
                else:
                    css_path = os.path.join(site_folder, href)
                
                if os.path.exists(css_path):
                    css_files.append(css_path)
        
        return css_files
    
    def _extract_js_dependencies(self, soup, site_folder):
        """Extract JavaScript file dependencies"""
        js_files = []
        
        # Find all script tags
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                # Resolve relative paths
                if src.startswith('/'):
                    js_path = os.path.join(site_folder, src[1:])
                elif src.startswith('http'):
                    # Skip external JS for now
                    continue
                else:
                    js_path = os.path.join(site_folder, src)
                
                if os.path.exists(js_path):
                    js_files.append(js_path)
        
        return js_files
    
    def _create_section_html(self, section_element, css_files, js_files):
        """Create a standalone HTML file for the section"""
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Extracted Section</title>
    {self._generate_css_links(css_files)}
</head>
<body>
    {str(section_element)}
    {self._generate_js_links(js_files)}
</body>
</html>"""
        
        return html_template
    
    def _generate_css_links(self, css_files):
        """Generate CSS link tags"""
        links = []
        for css_file in css_files:
            filename = os.path.basename(css_file)
            links.append(f'<link rel="stylesheet" href="css/{filename}">')
        return '\n    '.join(links)
    
    def _generate_js_links(self, js_files):
        """Generate JavaScript script tags"""
        scripts = []
        for js_file in js_files:
            filename = os.path.basename(js_file)
            scripts.append(f'<script src="js/{filename}"></script>')
        return '\n    '.join(scripts) 
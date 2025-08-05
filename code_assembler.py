import os
import shutil
from bs4 import BeautifulSoup
import json

class CodeAssembler:
    def __init__(self, output_folder='output'):
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
    
    def assemble_site(self, sections, site_structure):
        """Assemble the final site from extracted sections"""
        try:
            # Create a unique output directory
            import uuid
            site_id = str(uuid.uuid4())[:8]
            site_output_dir = os.path.join(self.output_folder, f"assembled_site_{site_id}")
            os.makedirs(site_output_dir, exist_ok=True)
            
            # Create the main HTML file
            main_html = self._create_main_html(sections, site_structure)
            main_html_path = os.path.join(site_output_dir, 'index.html')
            
            with open(main_html_path, 'w', encoding='utf-8') as f:
                f.write(main_html)
            
            # Copy all section assets
            self._copy_section_assets(sections, site_output_dir)
            
            # Create additional pages if specified
            if site_structure.get('pages'):
                self._create_additional_pages(sections, site_structure, site_output_dir)
            
            # Create a CSS file that combines all styles
            combined_css = self._combine_css_files(sections, site_output_dir)
            if combined_css:
                css_path = os.path.join(site_output_dir, 'styles.css')
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(combined_css)
            
            # Create a JavaScript file that combines all scripts
            combined_js = self._combine_js_files(sections, site_output_dir)
            if combined_js:
                js_path = os.path.join(site_output_dir, 'scripts.js')
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(combined_js)
            
            # Create a README file
            self._create_readme(sections, site_structure, site_output_dir)
            
            return site_output_dir
            
        except Exception as e:
            print(f"Error assembling site: {str(e)}")
            raise
    
    def _create_main_html(self, sections, site_structure):
        """Create the main HTML file with all sections"""
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    {sections_html}
    <script src="scripts.js"></script>
</body>
</html>"""
        
        # Extract sections in the specified order
        ordered_sections = []
        if site_structure.get('section_order'):
            for section_name in site_structure['section_order']:
                for section in sections:
                    if section.get('section_name') == section_name:
                        ordered_sections.append(section)
                        break
        else:
            # Use sections in the order they were provided
            ordered_sections = sections
        
        # Build the sections HTML
        sections_html = ""
        for section in ordered_sections:
            section_html = self._extract_section_html(section)
            if section_html:
                sections_html += f"\n    <!-- Section: {section.get('section_name', 'Unknown')} -->\n"
                sections_html += f"    {section_html}\n"
        
        return html_template.format(
            title=site_structure.get('title', 'Assembled Site'),
            sections_html=sections_html
        )
    
    def _extract_section_html(self, section):
        """Extract the HTML content from a section"""
        try:
            section_folder = section.get('section_folder')
            if not section_folder:
                return ""
            
            # Look for the section HTML file
            section_html_file = os.path.join(section_folder, 'section.html')
            if os.path.exists(section_html_file):
                with open(section_html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse and extract the body content
                soup = BeautifulSoup(content, 'html.parser')
                body = soup.find('body')
                if body:
                    return str(body)
                else:
                    return content
            else:
                # Try to find any HTML file in the section folder
                for file in os.listdir(section_folder):
                    if file.endswith('.html'):
                        with open(os.path.join(section_folder, file), 'r', encoding='utf-8') as f:
                            return f.read()
                
                return ""
                
        except Exception as e:
            print(f"Error extracting section HTML: {e}")
            return ""
    
    def _copy_section_assets(self, sections, site_output_dir):
        """Copy all assets from sections to the output directory"""
        try:
            assets_dir = os.path.join(site_output_dir, 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            
            for section in sections:
                section_folder = section.get('section_folder')
                if not section_folder or not os.path.exists(section_folder):
                    continue
                
                # Copy CSS files
                css_dir = os.path.join(section_folder, 'css')
                if os.path.exists(css_dir):
                    for file in os.listdir(css_dir):
                        if file.endswith('.css'):
                            src = os.path.join(css_dir, file)
                            dst = os.path.join(assets_dir, f"{section.get('section_name', 'section')}_{file}")
                            shutil.copy2(src, dst)
                
                # Copy JS files
                js_dir = os.path.join(section_folder, 'js')
                if os.path.exists(js_dir):
                    for file in os.listdir(js_dir):
                        if file.endswith('.js'):
                            src = os.path.join(js_dir, file)
                            dst = os.path.join(assets_dir, f"{section.get('section_name', 'section')}_{file}")
                            shutil.copy2(src, dst)
                
                # Copy images and other assets
                for root, dirs, files in os.walk(section_folder):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
                            src = os.path.join(root, file)
                            dst = os.path.join(assets_dir, file)
                            shutil.copy2(src, dst)
                            
        except Exception as e:
            print(f"Error copying assets: {e}")
    
    def _create_additional_pages(self, sections, site_structure, site_output_dir):
        """Create additional pages as specified in site_structure"""
        try:
            pages = site_structure.get('pages', {})
            
            for page_name, page_config in pages.items():
                page_sections = page_config.get('sections', [])
                page_title = page_config.get('title', page_name.title())
                
                # Create HTML for this page
                page_html = self._create_page_html(page_sections, page_title, sections)
                page_path = os.path.join(site_output_dir, f"{page_name}.html")
                
                with open(page_path, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                    
        except Exception as e:
            print(f"Error creating additional pages: {e}")
    
    def _create_page_html(self, page_sections, page_title, all_sections):
        """Create HTML for a specific page"""
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    {sections_html}
    <script src="scripts.js"></script>
</body>
</html>"""
        
        # Find the sections for this page
        sections_html = ""
        for section_name in page_sections:
            for section in all_sections:
                if section.get('section_name') == section_name:
                    section_html = self._extract_section_html(section)
                    if section_html:
                        sections_html += f"\n    <!-- Section: {section_name} -->\n"
                        sections_html += f"    {section_html}\n"
                    break
        
        return html_template.format(
            title=page_title,
            sections_html=sections_html
        )
    
    def _combine_css_files(self, sections, site_output_dir):
        """Combine all CSS files from sections"""
        try:
            combined_css = []
            
            for section in sections:
                section_folder = section.get('section_folder')
                if not section_folder:
                    continue
                
                css_dir = os.path.join(section_folder, 'css')
                if os.path.exists(css_dir):
                    for file in os.listdir(css_dir):
                        if file.endswith('.css'):
                            css_path = os.path.join(css_dir, file)
                            with open(css_path, 'r', encoding='utf-8') as f:
                                css_content = f.read()
                                combined_css.append(f"/* Section: {section.get('section_name', 'Unknown')} */")
                                combined_css.append(css_content)
                                combined_css.append("")
            
            return "\n".join(combined_css)
            
        except Exception as e:
            print(f"Error combining CSS files: {e}")
            return ""
    
    def _combine_js_files(self, sections, site_output_dir):
        """Combine all JavaScript files from sections"""
        try:
            combined_js = []
            
            for section in sections:
                section_folder = section.get('section_folder')
                if not section_folder:
                    continue
                
                js_dir = os.path.join(section_folder, 'js')
                if os.path.exists(js_dir):
                    for file in os.listdir(js_dir):
                        if file.endswith('.js'):
                            js_path = os.path.join(js_dir, file)
                            with open(js_path, 'r', encoding='utf-8') as f:
                                js_content = f.read()
                                combined_js.append(f"// Section: {section.get('section_name', 'Unknown')}")
                                combined_js.append(js_content)
                                combined_js.append("")
            
            return "\n".join(combined_js)
            
        except Exception as e:
            print(f"Error combining JS files: {e}")
            return ""
    
    def _create_readme(self, sections, site_structure, site_output_dir):
        """Create a README file with information about the assembled site"""
        try:
            readme_content = f"""# Assembled Website

This website was assembled from extracted sections using the Website Section Extractor.

## Site Information
- Title: {site_structure.get('title', 'Assembled Site')}
- Created: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Sections Used
"""
            
            for section in sections:
                readme_content += f"- {section.get('section_name', 'Unknown')}\n"
            
            readme_content += f"""
## File Structure
- `index.html` - Main page
- `styles.css` - Combined CSS styles
- `scripts.js` - Combined JavaScript
- `assets/` - Images and other assets

## Pages
"""
            
            if site_structure.get('pages'):
                for page_name, page_config in site_structure['pages'].items():
                    readme_content += f"- `{page_name}.html` - {page_config.get('title', page_name.title())}\n"
            else:
                readme_content += "- Single page site\n"
            
            readme_path = os.path.join(site_output_dir, 'README.md')
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
                
        except Exception as e:
            print(f"Error creating README: {e}") 
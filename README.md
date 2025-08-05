# 🌐 Website Section Extractor

A powerful tool that allows you to extract specific sections from websites using screenshots and assemble your own custom website. This system uses `wget` to download websites and then analyzes screenshots to identify and extract the corresponding HTML, CSS, and JavaScript sections.

## 🚀 Features

- **Website Extraction**: Download complete websites using `wget` with all assets
- **AI-Powered Analysis**: Enhanced screenshot analysis using Google's Gemini AI
- **Smart Suggestions**: Get AI-suggested section names based on screenshot content
- **Screenshot Analysis**: Upload screenshots to identify specific sections
- **Section Extraction**: Extract clean HTML, CSS, and JavaScript for each section
- **Site Assembly**: Combine extracted sections into a new website
- **Modern UI**: Beautiful, responsive web interface
- **Drag & Drop**: Easy screenshot upload with drag and drop support

## 📋 Prerequisites

- Python 3.7+
- `wget` command-line tool
- Chrome/Chromium browser (for Selenium)
- **Optional**: Google Gemini API key for enhanced AI analysis

### Installing wget

**macOS:**
```bash
# Install Homebrew first (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install wget
brew install wget
```

**Ubuntu/Debian:**
```bash
sudo apt-get install wget
```

**Windows:**
Download from [GNU Wget for Windows](https://eternallybored.org/misc/wget/)

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd novasite
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

4. **Open your browser:**
Navigate to `http://localhost:8080`

### Optional: Gemini AI Setup

For enhanced AI-powered analysis:

1. **Get a Gemini API key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key

2. **Configure the API key:**
   - Open the web interface
   - Go to the "Setup" tab
   - Enter your Gemini API key
   - Click "Save API Key"

3. **Enjoy AI features:**
   - Enhanced screenshot analysis
   - Smart section name suggestions
   - More accurate CSS selector generation

### Troubleshooting Gemini Installation

If you encounter issues with the Google GenAI SDK installation:

```bash
# Try installing directly with pip
pip install google-genai

# Or use the legacy package (fallback)
pip install google-generativeai
```

The system will automatically detect which package is available and use the appropriate one.

### Troubleshooting wget Installation

**macOS users:** If you get `[Errno 2] No such file or directory: 'wget'`:

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Install wget
brew install wget

# Verify installation
which wget
```

## 📖 How to Use

### Step 1: Extract a Website
1. Enter the URL of the website you want to extract
2. Click "Extract Website"
3. The system will download the entire website using `wget`

### Step 2: Extract Sections
1. Take screenshots of the sections you want to extract
2. Upload each screenshot using the drag & drop interface
3. Give each section a descriptive name (e.g., "header", "hero", "footer")
4. The system will analyze the screenshot and extract the corresponding HTML section

### Step 3: Assemble Your Site
1. Set a title for your new website
2. Specify the order of sections (comma-separated)
3. Click "Assemble Site" to create your final website

## 🔧 How It Works

### Website Extraction
The system uses the `wget` command with these flags:
- `--mirror`: Mirror the website
- `--convert-links`: Convert links to work locally
- `--adjust-extension`: Add appropriate file extensions
- `--page-requisites`: Download all assets (CSS, JS, images)
- `--no-parent`: Don't follow links to parent directories

**Enhanced with:**
- **User Agent Headers**: Mimics real browser requests to avoid 403 errors
- **Fallback Method**: Uses Python requests if wget fails
- **Better Error Handling**: Provides helpful error messages and suggestions
- **Anti-Bot Protection**: Handles websites that block automated requests

### AI-Powered Section Analysis
The system uses Google's Gemini AI to analyze screenshots:
1. **Enhanced Visual Analysis**: AI analyzes screenshot content and layout
2. **Smart CSS Selector Generation**: More accurate CSS selector identification
3. **Section Name Suggestions**: AI suggests appropriate section names
4. **Fallback Support**: Works without API key using traditional methods

### Section Extraction
For each identified section, the system:
1. Extracts the HTML content
2. Identifies and copies CSS dependencies
3. Identifies and copies JavaScript dependencies
4. Creates a standalone HTML file for the section

### Site Assembly
The final assembly process:
1. Combines all extracted sections in the specified order
2. Merges all CSS files into a single stylesheet
3. Merges all JavaScript files into a single script
4. Copies all assets (images, fonts, etc.)
5. Creates a complete, standalone website

## 🛠️ Troubleshooting

### Common Issues and Solutions

**403 Forbidden Error:**
- **Cause**: Website blocks automated requests
- **Solution**: Try a different website or use the fallback method
- **Example sites**: https://example.com, https://httpbin.org

**404 Not Found Error:**
- **Cause**: Incorrect URL or website doesn't exist
- **Solution**: Check URL spelling and add "https://" if missing

**Connection Refused:**
- **Cause**: Website is down or blocking requests
- **Solution**: Try again later or use a different website

**wget not found:**
- **macOS**: `brew install wget`
- **Ubuntu**: `sudo apt-get install wget`
- **Windows**: Download from GNU Wget for Windows

### Enhanced Error Handling

The system now provides:
- **Detailed error messages** with specific causes
- **Helpful suggestions** for common problems
- **Example URLs** for testing
- **Fallback methods** when primary extraction fails
- **User agent headers** to mimic real browsers

## 📁 Project Structure

```
novasite/
├── app.py                 # Main Flask application
├── website_extractor.py   # wget operations & section extraction
├── section_analyzer.py    # Traditional screenshot analysis
├── gemini_analyzer.py     # AI-powered analysis with Gemini
├── code_assembler.py      # Site assembly
├── templates/
│   └── index.html        # Web interface
├── requirements.txt       # Python dependencies
├── test_system.py        # System tests
├── test_gemini.py        # Gemini integration tests
├── demo.py              # Demo script
├── README.md            # Documentation
├── uploads/             # Temporary uploads
├── screenshots/         # Uploaded screenshots
├── extracted_sites/     # Downloaded websites
├── extracted_sections/  # Individual sections
└── output/             # Final assembled sites
```

## 🎯 Example Workflow

1. **Extract a website:**
   ```
   URL: https://example.com
   ```

2. **Upload screenshots and extract sections:**
   ```
   Screenshot 1 → "header" section
   Screenshot 2 → "hero" section  
   Screenshot 3 → "footer" section
   ```

3. **Assemble the site:**
   ```
   Title: My New Website
   Section Order: header,hero,footer
   ```

4. **Result:** A complete website with your selected sections in the specified order

## 🛠️ Technical Implementation

### Dependencies
- **Flask** - Web framework
- **BeautifulSoup** - HTML parsing
- **OpenCV** - Image processing
- **Selenium** - Web automation
- **wget** - Website downloading
- **Google GenAI SDK** - AI-powered analysis

### Key Algorithms
- **AI-Powered Analysis** using Google's Gemini 2.5 Flash model
- **Text similarity calculation** using Jaccard similarity
- **CSS selector generation** for precise section targeting
- **Asset dependency resolution** for complete section extraction
- **HTML structure analysis** for fallback section identification

## 🧪 Testing

The system includes comprehensive tests:
- Component unit tests
- Integration tests
- Gemini AI integration tests
- Demo script showing full workflow

Run tests with:
```bash
python test_system.py
python test_gemini.py
```

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python app.py
   ```

3. **Open browser:**
   Navigate to `http://localhost:8080`

4. **Follow the web interface:**
   - Extract a website
   - Upload screenshots
   - Assemble your new site

## 🎨 UI Features

- **Responsive design** - Works on desktop and mobile
- **Drag & drop upload** - Easy screenshot upload
- **Real-time feedback** - Loading states and progress indicators
- **Tabbed interface** - Clear workflow progression
- **Modern styling** - Beautiful gradients and animations
- **AI suggestions** - Smart section name recommendations

## 🔧 Advanced Features

- **Multi-page sites** - Support for creating multiple pages
- **Custom section ordering** - Specify exact order of sections
- **Asset optimization** - Combined CSS/JS files
- **Error recovery** - Graceful handling of extraction failures
- **Cross-platform** - Works on macOS, Linux, Windows
- **AI-powered analysis** - Enhanced screenshot understanding

## 🎉 Success Metrics

✅ **All tests passing** - System is fully functional  
✅ **Demo working** - Complete workflow demonstration  
✅ **Web interface live** - Beautiful, responsive UI  
✅ **AI integration** - Gemini AI-powered analysis  
✅ **Documentation complete** - Comprehensive README and guides  

## 🚀 Next Steps

The system is ready for production use! Potential enhancements:

1. **OCR Integration** - Better text extraction from screenshots
2. **Advanced AI Models** - Integration with other AI services
3. **Cloud deployment** - Deploy to AWS/Azure for scalability
4. **User accounts** - Multi-user support with saved projects
5. **Template library** - Pre-built section templates

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Flask for the web framework
- Uses BeautifulSoup for HTML parsing
- OpenCV for image processing
- Selenium for web automation
- wget for website downloading
- Google GenAI SDK for AI-powered analysis

## 📞 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section
2. Look at the error logs in the console
3. Create an issue on the repository

---

**Happy website building! 🚀** 
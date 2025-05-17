# 🌟 Ghata AI Website Generator v2.5.0

> AI-powered website generation tool that creates custom websites from text descriptions in seconds.

![GitHub](https://img.shields.io/badge/version-2.5.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.24+-red)

Enhanced version of [Ghata Website Generator v1.0.0](https://github.com/Just-a-code-lover/Ghata-AI-Powered-website-generation-tool_v1.0.0)

## 🚀 Live Demo

Try the app here: [https://ghata-ai.streamlit.app](https://ghata-ai.streamlit.app)

## 📋 Features

- 💬 **Text-to-Website**: Turn natural language descriptions into fully functional websites
- 🖼️ **Image Integration**: Automatic image search via Pexels API
- 🔄 **Version Control**: Save and navigate between different website versions
- 📦 **Export Options**: Download as ZIP files (single or all versions)
- 👀 **Live Preview**: Instant preview of generated websites

## 🧠 Architecture Diagram

![Architecture Diagram](https://github.com/Just-a-code-lover/Ghata-AI-Powered-website-generation-tool_v2.0.0/blob/Version_2.5.0/diagram-export-4-24-2025-1_16_22-AM.png?raw=true)

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8+
- Git

### Clone the Repository

```bash
git clone https://github.com/Just-a-code-lover/Ghata-AI-Powered-website-generation-tool_v2.0.0.git
cd Ghata-AI-Powered-website-generation-tool_v2.0.0
```

### Environment Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (create a `.env` file):

```
NVIDIA_API_KEY=your_nvidia_api_key
PEXELS_API_KEY=your_pexels_api_key
```

### Running Locally

Start the Streamlit app:

```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## 🚢 Deployment to Streamlit Cloud

1. Fork this repository to your GitHub account

2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)

3. Click "New app" and select the forked repository

4. Configure the app:
   - Set the main file path to `app.py`
   - Add the required secrets (NVIDIA_API_KEY and PEXELS_API_KEY) in the "Secrets" section
   - Choose the Python version (3.8+)

5. Click "Deploy" and wait for the build to complete

## 🏗️ Core Components

## 🔄 System Flow

```mermaid
graph TD
    A[User Input] --> B[Image Search]
    A --> C[Website Generation]
    B --> D[Pexels API]
    D --Images--> C
    C --> E[LLM/Nemotron]
    E --Response--> F[Code Generation]
    F --> G[Version Management]
    G --> H[Preview System]
    G --> I[Export System]

### 1. AI Website Generation Engine
- **Key File**: `llm_handler.py`
- **Main Functions**:
  - `generate_response()` - Handles API communication with NVIDIA's Nemotron model
  - `get_system_prompt()` - Manages the system prompt with detailed instructions
  - `extract_code_from_response()` - Parses HTML, CSS, and JS from AI responses

### 2. Version Control System
- **Key Files**: 
  - `website_version.py` - Version data structure
  - `app_utilities.py` - State management
- **Features**:
  - Unique ID generation for each version
  - Timestamp tracking
  - Version history navigation
  - State persistence between sessions

### 3. UI Components
- **Key File**: `ui_components.py`
- **Major Components**:
  - Custom header and styling
  - Chat interface
  - Code display panels
  - Version history cards
  - Download buttons

### 4. Image Integration
- **Key File**: `image_handler.py`
- **Main Function**: `get_images_from_pexels()`
- **Features**:
  - Pexels API integration
  - Image metadata handling
  - Dynamic image search

### 5. File Management
- **Key File**: `file_handler.py`
- **Main Functions**:
  - `create_download_zip()` - Single version export
  - `create_all_versions_zip()` - Multiple version export
  - File structure organization

## 📁 Project Structure

```
project/
├── app.py              # Main application
├── llm_handler.py      # AI model integration
├── image_handler.py    # Pexels API integration
├── website_version.py  # Version management
├── file_handler.py     # File operations
├── ui_components.py    # UI elements
├── app_utilities.py    # Utilities and state management
├── requirements.txt    # Project dependencies
└── .env                # Environment variables (create this)
```

## 💻 Technical Implementation

### Website Generation Process
```python
# In app.py
def main():
    # User input handling
    with chat_tab:
        user_input = st.text_area(...)
        image_query = st.text_input(...)
        
    # Generation process
    if st.session_state.submitted:
        # Get images if requested
        image_data = get_images_from_pexels(image_query, num_images)
        
        # Generate website
        system_prompt = get_system_prompt(image_data)
        response = generate_response(user_input, history, system_prompt)
        
        # Extract and save code
        html_code, css_code, js_code = extract_code_from_response(response)
```

### Version Management
```python
# In website_version.py
class WebsiteVersion:
    def __init__(self, html="", css="", js="", description=""):
        self.id = str(uuid.uuid4())[:8]  # Unique version ID
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # ... store code and description
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- NVIDIA NIM for AI text generation
- Pexels for image API access
- Streamlit for the web framework

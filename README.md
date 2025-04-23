# Ghata-AI-Powered-website-generation-tool_v2.5.0 (Latest/Stable)
My final year project and version 2 of https://github.com/Just-a-code-lover/Ghata-AI-Powered-website-generation-tool_v1.0.0


# Ghata AI Website Generator - Technical Documentation

## Core Components

### 1. AI Website Generation Engine
- **Key File**: llm_handler.py
- **Main Functions**:
  - `generate_response()` - Handles API communication with NVIDIA's Nemotron model
  - `get_system_prompt()` - Manages the system prompt with detailed instructions
  - `extract_code_from_response()` - Parses HTML, CSS, and JS from AI responses

### 2. Version Control System
- **Key Files**: 
  - website_version.py - Version data structure
  - app_utilities.py - State management
- **Features**:
  - Unique ID generation for each version
  - Timestamp tracking
  - Version history navigation
  - State persistence between sessions

### 3. UI Components
- **Key File**: ui_components.py
- **Major Components**:
  - Custom header and styling
  - Chat interface
  - Code display panels
  - Version history cards
  - Download buttons

### 4. Image Integration
- **Key File**: image_handler.py
- **Main Function**: `get_images_from_pexels()`
- **Features**:
  - Pexels API integration
  - Image metadata handling
  - Dynamic image search

### 5. File Management
- **Key File**: file_handler.py
- **Main Functions**:
  - `create_download_zip()` - Single version export
  - `create_all_versions_zip()` - Multiple version export
  - File structure organization

## Key Features & Implementation

### 1. Website Generation Process
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

### 2. Version Management
```python
# In website_version.py
class WebsiteVersion:
    def __init__(self, html="", css="", js="", description=""):
        self.id = str(uuid.uuid4())[:8]  # Unique version ID
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # ... store code and description
```

### 3. UI Layout
```python
# In app.py
def render_website_preview():
    tab1, tab2, tab3, tab4 = st.tabs(["Preview", "HTML", "CSS", "JavaScript"])
    # Each tab shows different aspects of the generated website
```

### 4. State Management
```python
# In app_utilities.py
def initialize_session_state():
    # Initialize all required session variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "website_versions" not in st.session_state:
        st.session_state.website_versions = []
```

## Technical Features

1. **Stateless Architecture with State Management**
   - Uses Streamlit's session state
   - Maintains conversation history
   - Preserves version history

2. **Modular Design**
   - Separated concerns (UI, LLM, file handling)
   - Easy to extend or modify components
   - Clean code organization

3. **Error Handling & Safety**
   - API error handling
   - Input validation
   - Safe file operations

4. **User Experience**
   - Live preview
   - Code highlighting
   - Responsive design
   - Interactive version management

## File Structure
```
project/
├── app.py              # Main application
├── llm_handler.py      # AI model integration
├── image_handler.py    # Pexels API integration
├── website_version.py  # Version management
├── file_handler.py     # File operations
├── ui_components.py    # UI elements
└── app_utilities.py    # Utilities and state management
```


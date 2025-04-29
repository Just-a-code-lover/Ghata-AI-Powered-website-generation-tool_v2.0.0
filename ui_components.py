import streamlit as st

def load_custom_css():
    """Load custom CSS for better UI styling and scrollbars"""
    st.markdown("""
    <style>
        /* Global styles */
        .stApp {
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }

        /* Hide Streamlit default elements */
        #MainMenu, footer, header {
            visibility: hidden;
        }

        /* Custom header styles */
        .custom-header {
            background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .custom-header h1 {
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .custom-header p {
            font-size: 1rem;
            opacity: 0.9;
        }

        /* Version history styles */
        .version-card {
            padding: 12px;
            margin-bottom: 15px;
            border-radius: 8px;
            transition: all 0.3s ease;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .version-card.active {
            border-left: 4px solid #4b6cb7;
            background-color: #EEF2FF;
        }

        .version-card:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        /* Model selection styling */
        .model-selection {
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
        }

        /* Radio button container */
        .st-emotion-cache-1vbkxwb {
            margin: 10px 0;
        }

        /* Selected radio button */
        .st-emotion-cache-1vbkxwb input:checked + label {
            font-weight: 600;
            color: #4b6cb7;
        }

        /* Radio button hover */
        .st-emotion-cache-1vbkxwb label:hover {
            background-color: #eef2ff;
        }
        
        /* Chat interface styles */
        .chat-message {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            word-wrap: break-word;
        }

        .chat-message.user {
            background-color: #E3F2FD;
            border-radius: 15px 15px 15px 5px;
        }

        .chat-message.assistant {
            background-color: #F3E5F5;
            border-radius: 15px 15px 5px 15px;
        }

        /* Fixed scrollable containers - Add !important to ensure priority */
        .scrollable-container {
            max-height: 400px !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            border: 1px solid rgba(49, 51, 63, 0.1);
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 15px;
            display: block !important;
        }
        
        /* Ensure code containers have proper scroll */
        .scrollable-code-container {
            max-height: 400px !important;
            overflow-y: auto !important;
            overflow-x: auto !important;
            display: block !important;
        }
        
        /* Specific fix for Streamlit code blocks */
        .stCodeBlock {
            max-height: 400px !important;
            overflow-y: auto !important;
        }
        
        div[data-testid="stCodeBlock"] pre {
            max-height: 380px !important;
            overflow-y: auto !important;
        }

        /* Webkit scrollbar styling */
        .scrollable-container::-webkit-scrollbar,
        .scrollable-code-container::-webkit-scrollbar,
        .stCodeBlock::-webkit-scrollbar,
        div[data-testid="stCodeBlock"] pre::-webkit-scrollbar {
            width: 8px;
            height: 8px;
            background: transparent;
        }

        .scrollable-container::-webkit-scrollbar-track,
        .scrollable-code-container::-webkit-scrollbar-track,
        .stCodeBlock::-webkit-scrollbar-track,
        div[data-testid="stCodeBlock"] pre::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        .scrollable-container::-webkit-scrollbar-thumb,
        .scrollable-code-container::-webkit-scrollbar-thumb,
        .stCodeBlock::-webkit-scrollbar-thumb,
        div[data-testid="stCodeBlock"] pre::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 10px;
        }

        .scrollable-container::-webkit-scrollbar-thumb:hover,
        .scrollable-code-container::-webkit-scrollbar-thumb:hover,
        .stCodeBlock::-webkit-scrollbar-thumb:hover,
        div[data-testid="stCodeBlock"] pre::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8;
        }

        /* Firefox scrollbar styling */
        * {
            scrollbar-width: thin;
            scrollbar-color: #c1c1c1 #f1f1f1;
        }

        /* Code display styles */
        .code-block {
            border-radius: 8px;
            padding: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            margin-bottom: 15px;
        }

        /* Preview container styles */
        .preview-container {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }

        /* Form and input styles */
        textarea {
            border-radius: 8px;
        }

        .input-label {
            font-weight: 500;
            margin-bottom: 5px;
            color: #555;
        }

        /* Button styles */
        .stButton button {
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 10px 16px;
            border-radius: 4px 4px 0 0;
        }

        /* Download section styles */
        .download-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }

        .download-buttons > div {
            flex: 1;
        }

        /* Override Streamlit's default overflow handling */
        .stMarkdown {
            overflow: visible !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
def create_custom_header():
    """Create a custom header with title and description"""
    st.markdown("""
    <div class="custom-header">
        <h1>🌐 GHATA-AI Website Generator</h1>
        <p>Describe your website idea and watch it come to life instantly</p>
    </div>
    """, unsafe_allow_html=True)

def format_chat_message(message, role):
    """Format a chat message with custom styling"""
    return f"""
    <div class="chat-message {role}">
        <strong>{"You" if role == "user" else "AI"}:</strong><br>
        {message}
    </div>
    """

def create_version_card(version, index, is_active=False):
    """Create a styled version card element"""
    active_class = "active" if is_active else ""
    return f"""
    <div class="version-card {active_class}">
        <strong>V{index+1}: {version.description[:20]}{'...' if len(version.description) > 20 else ''}</strong>
        <div style="font-size: 0.8em; color: #666;">{version.timestamp}</div>
        <div style="font-size: 0.8em; color: #888;">ID: {version.id}</div>
    </div>
    """
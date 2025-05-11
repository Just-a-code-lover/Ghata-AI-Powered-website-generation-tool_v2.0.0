import streamlit as st

def load_custom_css():
    """Load custom CSS for better UI styling and scrollbars"""
    st.markdown("""
    <style>
        /* Global styles */
        .stApp {
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        
        /* Layout fixes - full height content */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            max-width: 100%;
        }
        
        section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
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
            width: 100%;
            position: sticky;
            top: 0;
            z-index: 999;
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
            white-space: pre-wrap;
        }

        .chat-message.user {
            background-color: #E3F2FD;
            border-radius: 15px 15px 15px 5px;
        }

        .chat-message.assistant {
            background-color: #F3E5F5;
            border-radius: 15px 15px 5px 15px;
        }

        /* Fix markdown content inside chat messages */
        .chat-message strong {
            font-weight: 600;
        }
        
        .chat-message ul, .chat-message ol {
            margin-left: 20px;
            padding-left: 10px;
        }
        
        .chat-message code {
            background-color: rgba(0, 0, 0, 0.05);
            padding: 2px 4px;
            border-radius: 3px;
        }

        /* FIXED SCROLLABLE CONTAINERS - Stronger specificity and !important flags */
        .scrollable-container {
            max-height: 70vh !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            border: 1px solid rgba(49, 51, 63, 0.1) !important;
            border-radius: 4px !important;
            padding: 10px !important;
            margin-bottom: 15px !important;
            display: block !important;
        }
        
        /* Force Streamlit elements to respect overflow */
        [data-testid="stVerticalBlock"] .scrollable-container {
            max-height: 70vh !important;
            overflow-y: auto !important;
        }
        
        /* Ensure code containers have proper scroll */
        .scrollable-code-container {
            max-height: 60vh !important;
            overflow-y: auto !important;
            overflow-x: auto !important;
            display: block !important;
        }
        
        /* Specific fix for Streamlit code blocks */
        .stCodeBlock {
            max-height: 60vh !important;
            overflow-y: auto !important;
        }
        
        div[data-testid="stCodeBlock"] pre {
            max-height: 55vh !important;
            overflow-y: auto !important;
        }

        /* Apply scrollbars to all tab content */
        .stTabs [data-baseweb="tab-panel"] {
            max-height: 70vh !important;
            overflow-y: auto !important;
        }

        /* Tabs with overflow-y content should scroll */
        .stTabs [role="tabpanel"] > div {
            overflow-y: auto !important;
            max-height: 65vh !important;
        }

        /* Chat section specific scrollbar fix */
        [data-testid="stVerticalBlock"] > div:has(.chat-message) {
            max-height: 70vh !important;
            overflow-y: auto !important;
            padding-right: 5px !important;
        }

        /* Webkit scrollbar styling - make more specific */
        *::-webkit-scrollbar {
            width: 10px !important;
            height: 10px !important;
            background: transparent !important;
        }

        *::-webkit-scrollbar-track {
            background: #f1f1f1 !important;
            border-radius: 10px !important;
        }

        *::-webkit-scrollbar-thumb {
            background: #c1c1c1 !important;
            border-radius: 10px !important;
        }

        *::-webkit-scrollbar-thumb:hover {
            background: #a8a8a8 !important;
        }

        /* Firefox scrollbar styling */
        * {
            scrollbar-width: thin !important;
            scrollbar-color: #c1c1c1 #f1f1f1 !important;
        }

        /* Override Streamlit's overflow handling */
        div[data-testid="stVerticalBlock"] {
            overflow: visible !important;
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
            height: 70vh;
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
        
        /* Footer styles */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f9f9f9;
            border-top: 1px solid #e0e0e0;
            padding: 10px 0;
            text-align: center;
            z-index: 100;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .custom-header h1 {
                font-size: 1.8rem;
            }
            
            .custom-header p {
                font-size: 0.9rem;
            }
            
            /* Adjust column layout for mobile */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
            
            /* Make sure buttons stack well on mobile */
            .stButton button {
                width: 100%;
                margin-bottom: 10px;
            }
            
            /* Make scrollable areas smaller on mobile */
            .scrollable-container,
            .scrollable-code-container,
            .stCodeBlock,
            .stTabs [data-baseweb="tab-panel"],
            .stTabs [role="tabpanel"] > div {
                max-height: 50vh !important;
            }
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
    """Format a chat message with custom styling and ensure proper markdown rendering"""
    # Ensure markdown code blocks and lists render properly
    formatted_message = message.replace("```", "<pre><code>", 1)
    while "```" in formatted_message:
        formatted_message = formatted_message.replace("```", "</code></pre>", 1)
    
    # Format markdown list elements properly
    message_lines = []
    for line in formatted_message.split('\n'):
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            message_lines.append(f"• {line.strip()[2:]}")
        elif line.strip().startswith('1. ') or line.strip().startswith('2. ') or line.strip().startswith('3. ') or line.strip().startswith('4. '):
            number = line.strip().split('.')[0]
            message_lines.append(f"{number}. {line.strip()[len(number)+2:]}")
        else:
            message_lines.append(line)
    
    formatted_message = '\n'.join(message_lines)
    
    # Convert **bold** to proper HTML
    formatted_message = formatted_message.replace("**", "<strong>", 1)
    while "**" in formatted_message:
        formatted_message = formatted_message.replace("**", "</strong>", 1)
    
    return f"""
    <div class="chat-message {role}">
        <strong>{"You" if role == "user" else "AI"}:</strong><br>
        {formatted_message}
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
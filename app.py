import os
import streamlit as st
import zipfile
import io
import re
import json
import uuid
import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class WebsiteVersion:
    def __init__(self, html="", css="", js="", description="", timestamp=None):
        self.html = html
        self.css = css
        self.js = js
        self.description = description
        self.timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.id = str(uuid.uuid4())[:8]  # Generate a short unique ID
        
    def to_dict(self):
        return {
            "id": self.id,
            "html": self.html,
            "css": self.css,
            "js": self.js,
            "description": self.description,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        version = cls(
            html=data["html"],
            css=data["css"],
            js=data["js"],
            description=data["description"],
            timestamp=data["timestamp"]
        )
        version.id = data["id"]
        return version

def get_system_prompt():
    return """You are an elite web developer and designer AI with a reputation for creating stunning, 
    production-ready websites that exceed client expectations.

    When generating website code:
    1. Create clean, responsive HTML5, CSS3, and JavaScript that works seamlessly across all modern browsers
    2. Use semantic HTML elements and implement responsive design with a mobile-first approach
    3. Generate lightweight, vanilla JavaScript for interactivity and effects without external dependencies
    4. Ensure designs are visually compelling with modern aesthetic elements and thoughtful color schemes
    5. Include helpful, detailed comments in the code that explain your design choices
    6. Leverage CSS flexbox and grid for sophisticated layouts
    7. Use placeholder imagery from sources like 'https://placehold.co/' or 'https://picsum.photos/' 
       with appropriate dimensions and descriptive alt text
    8. Implement subtle animations and transitions for a polished user experience
    9. Ensure accessibility compliance with proper ARIA attributes and semantic structure
    
    Format your code responses as:
    ```html
    <!-- Your HTML code here -->
    ```
    
    ```css
    /* Your CSS code here */
    ```
    
    ```javascript
    // Your JavaScript code here
    ```
    
    Be creative and artistic in your designs, push boundaries while maintaining usability.
    When the user asks for modifications, carefully integrate their requests while enhancing the overall design.
    Always provide a complete solution that can be immediately deployed.

    IMPORTANT: If you're being asked to modify an existing website, review the existing code carefully before making changes.
    Maintain consistency with the existing design language while implementing the requested updates.
    """

def generate_response(prompt, conversation_history=None):
    """Generate a response using the NVIDIA API with conversation history"""
    try:
        # Initialize OpenAI client with only required parameters
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY")
        )
        
        messages = [
            {"role": "system", "content": get_system_prompt()},
        ]
        
        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add the current prompt
        messages.append({"role": "user", "content": prompt})
        
        response_text = ""
        
        # Stream the response
        with st.spinner("Generating website..."):
            completion = client.chat.completions.create(
                model="nvidia/llama-3.3-nemotron-super-49b-v1",
                messages=messages,
                temperature=0.75,
                top_p=0.98,
                max_tokens=16384,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                stream=True
            )
            
            # Create a placeholder to display the streaming response
            response_placeholder = st.empty()
            
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content
                    # Update the placeholder with the current response
                    response_placeholder.markdown(clean_response_for_display(response_text))
        
        return response_text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return f"I encountered an error: {str(e)}. Please check your API key and connection."

def extract_code_from_response(response):
    """Extract HTML, CSS, and JS code blocks from the AI response."""
    html_code = ""
    css_code = ""
    js_code = ""
    
    # Look for HTML code blocks
    html_start = response.find("```html")
    if html_start != -1:
        html_end = response.find("```", html_start + 6)
        if html_end != -1:
            html_code = response[html_start + 6:html_end].strip()
    
    # Look for CSS code blocks
    css_start = response.find("```css")
    if css_start != -1:
        css_end = response.find("```", css_start + 6)
        if css_end != -1:
            css_code = response[css_start + 6:css_end].strip()
    
    # Look for JS code blocks
    js_start = response.find("```javascript")
    if js_start != -1:
        js_end = response.find("```", js_start + 13)
        if js_end != -1:
            js_code = response[js_start + 13:js_end].strip()
    
    # Alternative JS block format
    if not js_code:
        js_start = response.find("```js")
        if js_start != -1:
            js_end = response.find("```", js_start + 5)
            if js_end != -1:
                js_code = response[js_start + 5:js_end].strip()
    
    return html_code, css_code, js_code

def clean_response_for_display(response):
    """Remove code blocks for cleaner display in the chat."""
    # Remove code blocks with language specifiers
    cleaned = re.sub(r'```(html|css|javascript|js)[\s\S]*?```', '[Code block removed for clarity]', response)
    # Remove any remaining generic code blocks
    cleaned = re.sub(r'```[\s\S]*?```', '[Code block removed for clarity]', cleaned)
    return cleaned

def create_download_zip(version):
    """Create a ZIP file with all website files for a specific version."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("index.html", f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Generated Website</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            {version.html}
            <script src="script.js"></script>
        </body>
        </html>
        """)
        
        zipf.writestr("styles.css", version.css)
        zipf.writestr("script.js", version.js)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def get_conversation_history_for_llm():
    """Convert the session history to a format suitable for the LLM."""
    # Extract only the necessary information for the LLM
    history = []
    
    # Include the latest website version code context if available
    if st.session_state.website_versions:
        latest_version = st.session_state.website_versions[-1]
        code_context = f"""
        Here's the current website code:
        
        HTML:
        ```html
        {latest_version.html}
        ```
        
        CSS:
        ```css
        {latest_version.css}
        ```
        
        JavaScript:
        ```javascript
        {latest_version.js}
        ```
        
        Please reference this code when making modifications.
        """
        history.append({"role": "assistant", "content": code_context})
    
    # Add the chat history (limited to last 6 messages to avoid token limits)
    for message in st.session_state.messages[-6:]:
        history.append({"role": message["role"], "content": message["content"]})
    
    return history

def main():
    st.set_page_config(layout="wide", page_title="AI Website Generator", page_icon="🌐")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "website_versions" not in st.session_state:
        st.session_state.website_versions = []
    if "current_version_index" not in st.session_state:
        st.session_state.current_version_index = -1
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    
    # Page header
    col_header1, col_header2 = st.columns([1, 4])
    with col_header1:
        st.image("https://placehold.co/80x80?text=G", width=80)
    with col_header2:
        st.title("Ghata AI-Powered Website Generator")
    
    st.markdown("---")
    
    # Create three columns for history, chat, and preview
    col_history, col_chat, col_preview = st.columns([1, 2, 2])
    
    with col_history:
        st.subheader("Version History")
        
        if st.session_state.website_versions:
            for i, version in enumerate(st.session_state.website_versions):
                # Create a unique key for each expander
                with st.expander(f"V{i+1}: {version.description[:20]}... ({version.timestamp})", expanded=(i == st.session_state.current_version_index)):
                    st.text(f"ID: {version.id}")
                    st.text(f"Created: {version.timestamp}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Load", key=f"load_{version.id}"):
                            st.session_state.current_version_index = i
                            st.rerun()
                    
                    with col2:
                        # Create a download button for this version
                        download_zip = create_download_zip(version)
                        st.download_button(
                            label="Download",
                            data=download_zip,
                            file_name=f"website_v{i+1}_{version.id}.zip",
                            mime="application/zip",
                            key=f"download_{version.id}"
                        )
        else:
            st.info("No versions available yet. Start by describing your website!")
    
    with col_chat:
        st.subheader("Chat with AI Designer")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"**You**: {message['content']}")
                else:
                    # Only display the cleaned response (without code blocks)
                    st.markdown(f"**AI**: {message['content']}")
        
        # Reference previous versions
        reference_col1, reference_col2 = st.columns(2)
        with reference_col1:
            use_reference = st.checkbox("Reference a previous version")
        
        referenced_version = None
        if use_reference and st.session_state.website_versions:
            with reference_col2:
                # Create a dropdown with version options
                version_options = {f"V{i+1}: {v.description[:20]}... ({v.id})": i 
                                   for i, v in enumerate(st.session_state.website_versions)}
                selected_version = st.selectbox("Select version to reference:", 
                                               options=list(version_options.keys()),
                                               index=0)
                referenced_version = version_options[selected_version]
        
        # Use a standard text input instead of chat_input for compatibility
        with st.form("website_input_form", clear_on_submit=True):
            user_input = st.text_area(
                "What would you like to create or modify?", 
                height=100,
                placeholder=("e.g., 'Create a portfolio website for a photographer' or "
                            "'Add a contact form to the current website'")
            )
            
            # Add reference context if a previous version is selected
            if use_reference and referenced_version is not None:
                ref_version = st.session_state.website_versions[referenced_version]
                reference_text = f"\n\nPlease reference version {ref_version.id} with description: '{ref_version.description}'"
                user_input += reference_text
            
            submit_button = st.form_submit_button("Generate Website")
            
            # Handle form submission
            if submit_button and user_input:
                st.session_state.user_input = user_input
                st.session_state.submitted = True
                
                # If referencing a previous version, set it as current
                if use_reference and referenced_version is not None:
                    st.session_state.current_version_index = referenced_version
        
        # Process the submission outside of the form
        if st.session_state.submitted:
            user_input = st.session_state.user_input
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get the conversation history for the LLM
            conversation_history = get_conversation_history_for_llm()
            
            # Generate response with the model
            response = generate_response(user_input, conversation_history)
            
            # Extract code from the response
            html_code, css_code, js_code = extract_code_from_response(response)
            
            # Clean the response for display (remove code blocks)
            display_response = clean_response_for_display(response)
            
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": display_response})
            
            # Create a new version if we have code
            if html_code or css_code or js_code:
                # If there's a current version, use its code as a base
                base_html = ""
                base_css = ""
                base_js = ""
                
                if st.session_state.current_version_index >= 0:
                    current_version = st.session_state.website_versions[st.session_state.current_version_index]
                    base_html = current_version.html
                    base_css = current_version.css
                    base_js = current_version.js
                
                # Use the new code if provided, otherwise keep the current code
                new_html = html_code if html_code else base_html
                new_css = css_code if css_code else base_css
                new_js = js_code if js_code else base_js
                
                # Create a new version
                description = user_input.split('\n')[0][:50]  # Use the first line of the user input as a description
                new_version = WebsiteVersion(
                    html=new_html,
                    css=new_css,
                    js=new_js,
                    description=description
                )
                
                # Add the new version to the history
                st.session_state.website_versions.append(new_version)
                st.session_state.current_version_index = len(st.session_state.website_versions) - 1
            
            # Reset the submitted flag
            st.session_state.submitted = False
            
            # Rerun to update the UI
            st.rerun()
    
    with col_preview:
        st.subheader("Website Preview")
        
        # Tabs for code and preview
        tab1, tab2, tab3, tab4 = st.tabs(["Preview", "HTML", "CSS", "JavaScript"])
        
        # Get the current version
        current_version = None
        if st.session_state.website_versions and st.session_state.current_version_index >= 0:
            current_version = st.session_state.website_versions[st.session_state.current_version_index]
        
        with tab1:
            if current_version:
                # Combine HTML, CSS, JS for preview
                combined_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>{current_version.css}</style>
                </head>
                <body>
                    {current_version.html}
                    <script>{current_version.js}</script>
                </body>
                </html>
                """
                st.components.v1.html(combined_code, height=600)
            else:
                st.info("Describe your website to see a preview here.")
        
        with tab2:
            if current_version:
                st.code(current_version.html, language="html")
            else:
                st.info("No HTML code available yet.")
        
        with tab3:
            if current_version:
                st.code(current_version.css, language="css")
            else:
                st.info("No CSS code available yet.")
        
        with tab4:
            if current_version:
                st.code(current_version.js, language="javascript")
            else:
                st.info("No JavaScript code available yet.")
        
        # Download options
        if current_version:
            download_zip = create_download_zip(current_version)
            st.download_button(
                label="Download Current Version (ZIP)",
                data=download_zip,
                file_name=f"website_v{st.session_state.current_version_index+1}_{current_version.id}.zip",
                mime="application/zip"
            )
            
            # Add a button to download all versions
            if len(st.session_state.website_versions) > 1:
                # Create a zip with all versions
                all_versions_zip = io.BytesIO()
                with zipfile.ZipFile(all_versions_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for i, version in enumerate(st.session_state.website_versions):
                        folder_name = f"version_{i+1}_{version.id}"
                        zipf.writestr(f"{folder_name}/index.html", f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Generated Website - Version {i+1}</title>
                            <link rel="stylesheet" href="styles.css">
                        </head>
                        <body>
                            {version.html}
                            <script src="script.js"></script>
                        </body>
                        </html>
                        """)
                        
                        zipf.writestr(f"{folder_name}/styles.css", version.css)
                        zipf.writestr(f"{folder_name}/script.js", version.js)
                        
                        # Add metadata file
                        metadata = {
                            "version": i+1,
                            "id": version.id,
                            "description": version.description,
                            "timestamp": version.timestamp
                        }
                        zipf.writestr(f"{folder_name}/metadata.json", json.dumps(metadata, indent=2))
                
                all_versions_zip.seek(0)
                st.download_button(
                    label="Download All Versions (ZIP)",
                    data=all_versions_zip.getvalue(),
                    file_name="all_website_versions.zip",
                    mime="application/zip"
                )
    
    # Footer with version info
    st.markdown("---")
    st.markdown("Built with Streamlit and NIM 🚀")

if __name__ == "__main__":
    main()
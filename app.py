import os
import streamlit as st
import zipfile
import io
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def get_system_prompt():
    return """You are an expert web developer AI assistant specialized in generating complete, 
    production-ready websites from natural language descriptions.

    When generating website code:
    1. Create clean, responsive HTML5, CSS3, and JavaScript that works across all modern browsers
    2. Use semantic HTML elements and responsive design principles
    3. Generate lightweight, vanilla JavaScript without external dependencies
    4. Create a responsive design that looks good on mobile and desktop
    5. Include helpful comments in the code
    
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
    
    When the user asks for modifications, carefully integrate their requests with the existing code.
    Always provide a complete solution that can be immediately deployed.
    """

def generate_response(prompt):
    """Generate a response using the NVIDIA API"""
    try:
        # Initialize OpenAI client with only required parameters
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY")
        )
        
        messages = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response_text = ""
        
        # Stream the response
        with st.spinner("Generating website..."):
            completion = client.chat.completions.create(
                model="nvidia/llama-3.3-nemotron-super-49b-v1",
                messages=messages,
                temperature=0.6,
                top_p=0.95,
                max_tokens=16384,
                frequency_penalty=0,
                presence_penalty=0,
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

def create_download_zip():
    """Create a ZIP file with all website files."""
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
            {st.session_state.current_website_code["html"]}
            <script src="script.js"></script>
        </body>
        </html>
        """)
        
        zipf.writestr("styles.css", st.session_state.current_website_code["css"])
        zipf.writestr("script.js", st.session_state.current_website_code["js"])
        
        # Add logo if available
        if st.session_state.logo_url:
            # Logic to include the logo file
            pass
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def main():
    st.set_page_config(layout="wide", page_title="AI Website Generator")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_website_code" not in st.session_state:
        st.session_state.current_website_code = {"html": "", "css": "", "js": ""}
    if "logo_url" not in st.session_state:
        st.session_state.logo_url = None
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    
    # Page header
    st.title("NVIDIA LLM-Powered Website Generator")
    
    # Create two columns for the chat interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Describe Your Website")
        
        # Display chat history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"**You**: {message['content']}")
            else:
                st.markdown(f"**AI**: {message['content']}")
        
        # Use a standard text input instead of chat_input for compatibility
        with st.form("website_input_form", clear_on_submit=True):
            user_input = st.text_area("Describe your website (e.g., 'Create a portfolio website for a photographer')...", height=100)
            submit_button = st.form_submit_button("Generate Website")
            
            # Handle form submission
            if submit_button and user_input:
                st.session_state.user_input = user_input
                st.session_state.submitted = True
        
        # Process the submission outside of the form
        if st.session_state.submitted:
            user_input = st.session_state.user_input
            
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Generate response with the model
            response = generate_response(user_input)
            
            # Extract code from the response
            html_code, css_code, js_code = extract_code_from_response(response)
            
            # Update the website code
            if html_code:
                st.session_state.current_website_code["html"] = html_code
            if css_code:
                st.session_state.current_website_code["css"] = css_code
            if js_code:
                st.session_state.current_website_code["js"] = js_code
            
            # Clean the response for display (remove code blocks)
            display_response = clean_response_for_display(response)
            
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": display_response})
            
            # Reset the submitted flag
            st.session_state.submitted = False
    
    with col2:
        st.subheader("Website Preview")
        
        # Tabs for code and preview
        tab1, tab2, tab3, tab4 = st.tabs(["Preview", "HTML", "CSS", "JavaScript"])
        
        with tab1:
            if st.session_state.current_website_code["html"]:
                # Combine HTML, CSS, JS for preview
                combined_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>{st.session_state.current_website_code["css"]}</style>
                </head>
                <body>
                    {st.session_state.current_website_code["html"]}
                    <script>{st.session_state.current_website_code["js"]}</script>
                </body>
                </html>
                """
                st.components.v1.html(combined_code, height=600)
            else:
                st.info("Describe your website to see a preview here.")
        
        with tab2:
            st.code(st.session_state.current_website_code["html"], language="html")
        
        with tab3:
            st.code(st.session_state.current_website_code["css"], language="css")
        
        with tab4:
            st.code(st.session_state.current_website_code["js"], language="javascript")
        
        # Download options
        if st.session_state.current_website_code["html"]:
            download_zip = create_download_zip()
            st.download_button(
                label="Download Website Files (ZIP)",
                data=download_zip,
                file_name="website.zip",
                mime="application/zip"
            )

if __name__ == "__main__":
    main()
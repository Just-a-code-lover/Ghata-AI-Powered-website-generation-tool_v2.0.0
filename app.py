import os
import streamlit as st
import io
import json
import zipfile
from dotenv import load_dotenv
from app_utilities import clear_session_state, initialize_session_state
import random
import time
from image_handler import get_images_from_pexels
from website_version import WebsiteVersion
from ui_components import load_custom_css, create_custom_header, format_chat_message, create_version_card
from llm_handler import generate_response, extract_code_from_response, clean_response_for_display, get_system_prompt
from file_handler import create_download_zip


LOADING_GIFS = [
    "https://media0.giphy.com/media/XfDiixCqdH7OrEBg5z/giphy.gif",
    "https://media1.giphy.com/media/HjyfGGLxtaPbhrJWEg/giphy.gif",
    "https://media0.giphy.com/media/xCej66aMjFBgqgWtQV/giphy.gif",
    "https://media.giphy.com/media/tHIRLHtNwxpjIFqPdV/giphy.gif",
    "https://media4.giphy.com/media/vHslzlGM9vKUgFNx0y/giphy.gif",
    "https://media3.giphy.com/media/5tiNlHkA1WdUh3jRDW/giphy.gif",
    "https://media4.giphy.com/media/axsN0Wx9AjwOJBvBLu/giphy.gif",
    "https://media3.giphy.com/media/QHEt9Q8bZXp2ukQ10z/giphy.gif",
    "https://media.giphy.com/media/Wgzw6BvYYDXYBKqoJE/giphy.gif",
    "https://media2.giphy.com/media/QAB3dfWbviuR0iIC1T/giphy.gif",
    "https://media.giphy.com/media/paThDtNido1kiskB5E/giphy.gif"
]

LOADING_MESSAGES = [
    "Cooking up something special... 👨‍🍳",
    "Adding some magic ingredients... ✨",
    "Stirring the creative pot... 🪄",
    "Preparing your website... 🌐",
    "Almost ready to serve... 🍽️",
    "Making it pixel-perfect... 🎨",
    "Adding the secret sauce... 🥫",
    "Mixing the perfect blend... 🎯",
    "Just a few more touches... ⚡",
    "Creating something delicious... 🍪"
]

# Load environment variables
load_dotenv()

def get_conversation_history_for_llm():
    """Convert the session history to a format suitable for the LLM."""
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

def render_version_history():
    """Render the version history with proper error handling and reset button."""
    st.markdown("<h3>Version History</h3>", unsafe_allow_html=True)

    # Initialize the toggle state in session state if not already set
    if "show_history" not in st.session_state:
        st.session_state.show_history = True

    # Toggle button to show/hide version history
    toggle_text = "Hide Version History" if st.session_state.show_history else "Show Version History"
    if st.button(toggle_text):
        # Flip the state of show_history
        st.session_state.show_history = not st.session_state.show_history

    # Reset app state button
    if st.button("🧹 Reset All Versions & Chat"):
        clear_session_state()
        st.rerun()

    # If version history is hidden, return early
    if not st.session_state.show_history:
        return

    # Render version history if available
    if st.session_state.website_versions:
        # Important: Using HTML instead of container for better scroll control
        st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        try:
            for i, version in enumerate(st.session_state.website_versions):
                if not isinstance(version, WebsiteVersion):
                    st.warning(f"Skipping corrupted version at index {i}")
                    continue

                is_active = i == st.session_state.current_version_index
                st.markdown(create_version_card(version, i, is_active), unsafe_allow_html=True)

                # Avoid nested columns - use side-by-side buttons with HTML/CSS instead
                col1, col2 = st.columns(2)
                with col1:
                    load_btn = st.button("Load", key=f"load_{version.id}")
                with col2:
                    download_zip = create_download_zip(version)
                    st.download_button(
                        label="Download",
                        data=download_zip,
                        file_name=f"website_v{i+1}_{version.id}.zip",
                        mime="application/zip",
                        key=f"download_{version.id}"
                    )

                if load_btn:
                    st.session_state.current_version_index = i
                    st.rerun()

                st.markdown("<hr style='margin: 10px 0; opacity: 0.3'>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error rendering versions: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No versions available yet. Start by describing your website!")

def render_chat_interface():
    """Display chat history with proper scrolling."""
    # Important: Use CSS class to force vertical scrolling
    st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        role = "user" if message["role"] == "user" else "assistant"
        content = message["content"]
        if role == "assistant":
            content = clean_response_for_display(content)
        st.markdown(format_chat_message(content, role), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_website_preview():
    """Render the website preview with scrollable sections for HTML, CSS, JS"""
    st.markdown("<h3>Website Preview</h3>", unsafe_allow_html=True)

    current_version = None
    if st.session_state.website_versions and st.session_state.current_version_index >= 0:
        current_version = st.session_state.website_versions[st.session_state.current_version_index]

    if not current_version:
        st.info("Describe your website to see a preview here.")
        return

    # Independent scrollable sections
    tab1, tab2, tab3, tab4 = st.tabs(["Preview", "HTML", "CSS", "JavaScript"])

    with tab1:
        combined_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>{current_version.css}</style>
        </head>
        <body>
            {current_version.html}
            <script>{current_version.js}</script>
        </body>
        </html>
        """
        st.components.v1.html(combined_code, height=500, scrolling=True)

    with tab2:
        # Use scrollable-code-container for proper scrolling
        st.markdown('<div class="scrollable-code-container">', unsafe_allow_html=True)
        st.code(current_version.html, language="html")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="scrollable-code-container">', unsafe_allow_html=True)
        st.code(current_version.css, language="css")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="scrollable-code-container">', unsafe_allow_html=True)
        st.code(current_version.js, language="javascript")
        st.markdown('</div>', unsafe_allow_html=True)

    # Simplified download section - avoid nesting issues
    st.markdown("### Download Options")
    
    # Create simple buttons without nesting columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="Download Current Version",
            data=create_download_zip(current_version),
            file_name=f"website_v{st.session_state.current_version_index+1}_{current_version.id}.zip",
            mime="application/zip",
            key="download_current"
        )
    
    # Second button (shown conditionally)
    if len(st.session_state.website_versions) > 1:
        with col2:
            all_versions_zip = io.BytesIO()
            with zipfile.ZipFile(all_versions_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                for i, version in enumerate(st.session_state.website_versions):
                    folder = f"version_{i+1}_{version.id}"
                    zipf.writestr(f"{folder}/index.html", f"""<!DOCTYPE html>
                    <html><head><meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Generated Website - Version {i+1}</title>
                    <link rel="stylesheet" href="styles.css">
                    </head><body>{version.html}<script src="script.js"></script></body></html>""")
                    zipf.writestr(f"{folder}/styles.css", version.css)
                    zipf.writestr(f"{folder}/script.js", version.js)
                    zipf.writestr(f"{folder}/metadata.json", json.dumps({
                        "version": i+1,
                        "id": version.id,
                        "description": version.description,
                        "timestamp": version.timestamp
                    }, indent=2))
            all_versions_zip.seek(0)
            
            st.download_button(
                label="Download All Versions",
                data=all_versions_zip.getvalue(),
                file_name="all_website_versions.zip",
                mime="application/zip",
                key="download_all"
            )
            #download_container.markdown("</div>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        layout="wide", 
        page_title="GHATA-AI Website Generator", 
        page_icon="🌐",
        initial_sidebar_state="collapsed"
    )

    # Init session
    initialize_session_state()

    # UI basics
    load_custom_css()
    create_custom_header()

    # Main layout structure - avoid nested columns
    left_panel, right_panel = st.columns([1, 3])
    
    # Left column - Version history
    with left_panel:
        render_version_history()

    # Right column - Chat and preview
    with right_panel:
        # Use tabs instead of columns to avoid nesting issues
        chat_tab, preview_tab = st.tabs(["Chat with GHATA-AI", "Website Preview"])
        
        with chat_tab:
            # Chat interface
            render_chat_interface()
            
            # Input Form
            with st.form("website_input_form", clear_on_submit=True):
                user_input = st.text_area(
                    "What would you like to create or modify?",
                    height=100,
                    placeholder="e.g., 'Create a landing page for a bakery with contact form'"
                )
                
                # Image search section
                col1, col2 = st.columns([3, 1])
                with col1:
                    image_query = st.text_input(
                        "Search for images (optional)",
                        placeholder="e.g., bakery, coffee, pastries",
                        key="image_query_input"
                    )
                with col2:
                    num_images = st.number_input(
                        "Number of images",
                        min_value=1,
                        max_value=10,
                        value=5,
                        key="num_images_input"
                    )             
        
                with st.expander("🚀 Advanced: Choose AI Model"):
                    model_info = {
                        "Good (Fastest)  ": "⚡ Fastest response, good for simple websites",
                        "Better (Default)": "🎯 Balanced speed and quality, recommended for most cases",
                        "Best (Slowest)  ": "✨ Highest quality, best for complex requirements"
                    }
                    
                    model_choice = st.radio(
                        "Select AI Model",
                        options=list(model_info.keys()),
                        index=1,
                        key="model_selector"
                    )
                    
                    st.info(model_info[model_choice])

                # Reference version checkbox
                use_reference = st.checkbox("Reference a previous version")
                
                # Only show version selector if checkbox is checked and versions exist
                referenced_version = None
                if use_reference and st.session_state.website_versions:
                    version_options = {
                        f"V{i+1}: {v.description[:20]}... ({v.id})": i
                        for i, v in enumerate(st.session_state.website_versions)
                    }
                    selected_version = st.selectbox(
                        "Select version to reference:",
                        options=list(version_options.keys()),
                        index=0
                    )
                    referenced_version = version_options[selected_version]
                
                # Submit button
                submit_button = st.form_submit_button("Generate Website")

                if submit_button and user_input:
                    st.session_state.user_input = user_input
                    st.session_state.image_query = image_query  # Store image query
                    st.session_state.num_images = num_images    # Store num_images
                    st.session_state.submitted = True
                    st.session_state.use_reference = use_reference
                    st.session_state.referenced_version = referenced_version
                    st.rerun()
        
        with preview_tab:
            # Preview section
            render_website_preview()

    # Submission handler
    # In app.py, replace the submission handler section with this code:

        # Submission handler
    # Replace the submission handler portion with this:

    # Submission handler
    if st.session_state.submitted:
        user_input = st.session_state.user_input
        image_query = st.session_state.get("image_query")
        num_images = st.session_state.get("num_images", 5)

        # Fetch images if query provided
        image_data = []
        if image_query:
            with st.spinner("Fetching images..."):
                image_data = get_images_from_pexels(image_query, num_images)
                if not image_data:
                    st.warning("No images found. Using placeholder images instead.")

        # Add version reference if enabled
        if st.session_state.get("use_reference") and st.session_state.get("referenced_version") is not None:
            ref = st.session_state.website_versions[st.session_state.referenced_version]
            user_input += f"\n\nPlease reference version {ref.id} with description: '{ref.description}'"

        st.session_state.messages.append({"role": "user", "content": user_input})

        # Store timestamp of last animation update in session state
        if "last_animation_update" not in st.session_state:
            st.session_state.last_animation_update = time.time()
            st.session_state.current_gif = random.choice(LOADING_GIFS)
            st.session_state.current_message = random.choice(LOADING_MESSAGES)
        
        # Initialize the loading placeholder
        loading_placeholder = st.empty()
        
        # Show initial loading animation
        loading_placeholder.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; margin: 20px 0;">
            <img src="{st.session_state.current_gif}" 
                alt="Loading animation" 
                width="300" 
                style="border-radius: 15px; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
                        margin-bottom: 15px;">
            <p style="font-size: 20px; 
                    font-weight: 500; 
                    color: #4b6cb7; 
                    text-align: center;
                    margin: 10px 0;">
                {st.session_state.current_message}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate the response
        history = get_conversation_history_for_llm()
        system_prompt = get_system_prompt(image_data)
        
        # Generate the response with a timeout mechanism
        response = None
        timeout = 300  # 5-minute timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if we need to update the animation
            current_time = time.time()
            if current_time - st.session_state.last_animation_update > 10:  # 10 seconds interval
                st.session_state.current_gif = random.choice(LOADING_GIFS)
                st.session_state.current_message = random.choice(LOADING_MESSAGES)
                st.session_state.last_animation_update = current_time
                
                # Force a rerun to update the UI
                st.rerun()
            
            try:
                # Try to generate a response
                response = generate_response(user_input, history, system_prompt, model_choice)
                if response:
                    break
                
                # Small sleep to prevent CPU hogging
                time.sleep(0.5)
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
                break
        
        # Check if the response was generated successfully
        if not response:
            loading_placeholder.empty()
            st.error("❌ Website generation timed out or failed. Please try again.")
            st.session_state.submitted = False
            return
        
        # Clear the loading animation
        loading_placeholder.empty()
        
        # Reset animation-related session state
        if "last_animation_update" in st.session_state:
            del st.session_state.last_animation_update
        if "current_gif" in st.session_state:
            del st.session_state.current_gif
        if "current_message" in st.session_state:
            del st.session_state.current_message
        
        # Extract code from response
        html_code, css_code, js_code = extract_code_from_response(response)
        
        # Create user guide message
        guide_message = """
    🎉 **Website Generated Successfully!**

    📱 To see your website:
    1. Click the "Website Preview" tab above
    2. Use the preview panel to interact with your site
    3. Check the HTML, CSS, and JS tabs for the code

    💡 You can:
    - Continue chatting to refine the website
    - Use version history to track changes
    - Download your website using the buttons below the preview

    🔄 Want to make changes?
    - Simply describe what you'd like to modify
    - Reference previous versions if needed
    - Add images by using the image search feature
    """
        
        # Add both LLM response and guide to chat
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"{response}\n\n{guide_message}"
        })

        if html_code or css_code or js_code:
            base_html = base_css = base_js = ""
            if st.session_state.current_version_index >= 0:
                current = st.session_state.website_versions[st.session_state.current_version_index]
                base_html, base_css, base_js = current.html, current.css, current.js

            new_version = WebsiteVersion(
                html=html_code or base_html,
                css=css_code or base_css,
                js=js_code or base_js,
                description=user_input.split('\n')[0][:50]
            )
            st.session_state.website_versions.append(new_version)

            # Update current_version_index
            if st.session_state.current_version_index == -1:
                st.session_state.current_version_index = 0
            else:
                st.session_state.current_version_index = len(st.session_state.website_versions) - 1

        st.session_state.submitted = False
        st.rerun()
        
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 10px;'>
        <p>Built with Streamlit and NIM 🚀</p>
        <p style='font-size: 0.8rem;'>© 2025 Ghata AI Website Generator</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
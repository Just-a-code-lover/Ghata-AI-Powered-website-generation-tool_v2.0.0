import os
import streamlit as st
import io
import json
import zipfile
from dotenv import load_dotenv
from app_utilities import clear_session_state, initialize_session_state


# Import from local modules
from image_handler import get_images_from_pexels
from website_version import WebsiteVersion
from ui_components import load_custom_css, create_custom_header, format_chat_message, create_version_card
from llm_handler import generate_response, extract_code_from_response, clean_response_for_display, get_system_prompt
from file_handler import create_download_zip

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
    """Render the version history with proper error handling and reset button"""
    st.markdown("<h3>Version History</h3>", unsafe_allow_html=True)

    # Safety checks
    if not isinstance(st.session_state.website_versions, list):
        st.error("⚠️ Internal error: version history is not a list.")
        return

    toggle_key = "hide_history" if st.session_state.show_history else "show_history"
    toggle_text = "Hide Version History" if st.session_state.show_history else "Show Version History"

    show_history_toggle = st.session_state.get("show_history", True)  # Default to True
    if st.button(toggle_text, key=toggle_key):
        show_history_toggle = not show_history_toggle
        st.session_state.show_history = show_history_toggle
        st.rerun()

    # 🔁 Reset app state button
    if st.button("🧹 Reset All Versions & Chat"):
        clear_session_state()
        st.rerun()

    if not st.session_state.show_history:
        return

    if st.session_state.website_versions:
        with st.container():
            st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
            try:
                for i, version in enumerate(st.session_state.website_versions):
                    if not isinstance(version, WebsiteVersion):
                        st.warning(f"Skipping corrupted version at index {i}")
                        continue

                    is_active = i == st.session_state.current_version_index
                    st.markdown(create_version_card(version, i, is_active), unsafe_allow_html=True)

                    # Avoid nesting columns by using buttons directly
                    load_btn = st.button("Load", key=f"load_{version.id}")
                    download_zip = create_download_zip(version)
                    download_btn = st.download_button(
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
    """Display chat history without the input form."""
    with st.container():
        st.markdown('<div class="scrollable-container" style="max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
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

    # Download buttons section
    st.markdown("### Download Options")
    
    # Use a container instead of columns to avoid nesting issues
    download_container = st.container()
    
    # Place buttons side by side with custom CSS
    download_container.markdown(
        """
        <style>
        .download-buttons {
            display: flex;
            gap: 10px;
        }
        .download-buttons > div {
            flex: 1;
        }
        </style>
        <div class="download-buttons">
        """, 
        unsafe_allow_html=True
    )
    
    # First button (always shown)
    download_current = st.download_button(
        label="Download Current Version",
        data=create_download_zip(current_version),
        file_name=f"website_v{st.session_state.current_version_index+1}_{current_version.id}.zip",
        mime="application/zip",
        key="download_current"
    )
    
    # Second button (shown conditionally)
    if len(st.session_state.website_versions) > 1:
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
        
        download_all = st.download_button(
            label="Download All Versions",
            data=all_versions_zip.getvalue(),
            file_name="all_website_versions.zip",
            mime="application/zip",
            key="download_all"
        )
    
    download_container.markdown("</div>", unsafe_allow_html=True)


def main():
    st.set_page_config(
        layout="wide", 
        page_title="AI Website Generator", 
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
        chat_tab, preview_tab = st.tabs(["Chat with AI Designer", "Website Preview"])
        
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

        with st.spinner("Generating website..."):
            history = get_conversation_history_for_llm()
            # Pass image data to get_system_prompt
            system_prompt = get_system_prompt(image_data)
            response = generate_response(user_input, history, system_prompt)
            html_code, css_code, js_code = extract_code_from_response(response)

            st.session_state.messages.append({"role": "assistant", "content": response})
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
                # Add the new version
                st.session_state.website_versions.append(new_version)

                # Properly update the current_version_index
                if st.session_state.current_version_index == -1:
                    # First version ever added, set to index 0
                    st.session_state.current_version_index = 0
                else:
                    # On subsequent adds, point to the latest version
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
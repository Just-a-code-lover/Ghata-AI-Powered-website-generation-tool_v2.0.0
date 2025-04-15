import streamlit as st
import json
import os
import datetime
from website_version import WebsiteVersion

def initialize_session_state():
    """Initialize all session state variables with defaults."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if "website_versions" not in st.session_state:
        st.session_state.website_versions = []
        
    if "current_version_index" not in st.session_state:
        st.session_state.current_version_index = -1
        
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
        
    if "show_history" not in st.session_state:
        st.session_state.show_history = True
        
    if "loading" not in st.session_state:
        st.session_state.loading = False
        
    if "last_saved" not in st.session_state:
        st.session_state.last_saved = None

def save_state_to_file(filename="website_state.json"):
    """Save the current session state to a JSON file."""
    data = {
        "messages": st.session_state.messages,
        "website_versions": [v.to_dict() for v in st.session_state.website_versions],
        "current_version_index": st.session_state.current_version_index,
        "saved_at": datetime.datetime.now().isoformat()
    }
    
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        st.session_state.last_saved = datetime.datetime.now()
        return True
    except Exception as e:
        st.error(f"Error saving state: {str(e)}")
        return False

def load_state_from_file(filename="website_state.json"):
    """Load session state from a JSON file."""
    if not os.path.exists(filename):
        return False
    
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        
        # Load messages
        st.session_state.messages = data.get("messages", [])
        
        # Load website versions
        versions = []
        for v_data in data.get("website_versions", []):
            versions.append(WebsiteVersion.from_dict(v_data))
        st.session_state.website_versions = versions
        
        # Load current version index
        st.session_state.current_version_index = data.get("current_version_index", -1)
        
        # Set last loaded time
        st.session_state.last_saved = datetime.datetime.fromisoformat(data.get("saved_at", datetime.datetime.now().isoformat()))
        
        return True
    except Exception as e:
        st.error(f"Error loading state: {str(e)}")
        return False

def clear_session_state():
    """Clear all session state data (reset the app)."""
    if "messages" in st.session_state:
        st.session_state.messages = []
    
    if "website_versions" in st.session_state:
        st.session_state.website_versions = []
    
    if "current_version_index" in st.session_state:
        st.session_state.current_version_index = -1
    
    if "submitted" in st.session_state:
        st.session_state.submitted = False
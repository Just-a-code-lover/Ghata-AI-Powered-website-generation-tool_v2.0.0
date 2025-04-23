#website_version.py
import uuid
import datetime

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
        return cls(
            html=data.get("html", ""),
            css=data.get("css", ""),
            js=data.get("js", ""),
            description=data.get("description", "No description provided."),
            timestamp=data.get("timestamp") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

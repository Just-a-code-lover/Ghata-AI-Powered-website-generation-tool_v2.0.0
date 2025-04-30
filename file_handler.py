import io
import zipfile
import json
import datetime

def create_download_zip(version):
    """Create a ZIP file with all website files for a specific version."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Create main HTML file with proper DOCTYPE and metadata
        zipf.writestr("index.html", f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{version.description}">
    <title>Generated Website</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
{version.html}
<script src="script.js"></script>
</body>
</html>""")
        
        # Add CSS file
        zipf.writestr("styles.css", version.css)
        
        # Add JavaScript file
        zipf.writestr("script.js", version.js)
        
        # Add a README file with useful information
        zipf.writestr("README.md", f"""# Generated Website

## Version Information
- ID: {version.id}
- Description: {version.description}
- Created: {version.timestamp}

## Files
- `index.html`: Main HTML structure of the website
- `styles.css`: CSS styling rules
- `script.js`: JavaScript functionality

## How to Use
1. Open `index.html` in any modern web browser to view the website
2. Edit the files with any text editor to make changes

This website was generated with AI Website Generator.
        """)
        
        # Add a metadata.json file for programmatic use
        metadata = {
            "id": version.id,
            "description": version.description,
            "timestamp": version.timestamp,
            "generated_on": datetime.datetime.now().isoformat()
        }
        zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def create_all_versions_zip(website_versions):
    """Create a ZIP file with all website versions organized in folders."""
    all_versions_zip = io.BytesIO()
    
    with zipfile.ZipFile(all_versions_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add a root README file
        zipf.writestr("README.md", f"""# AI Website Generator - All Versions
        
Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This archive contains {len(website_versions)} version(s) of your website.
Each version is stored in its own folder with all necessary files.

## Versions Summary
{generate_versions_summary(website_versions)}

## How to Use
Navigate to any version folder and open `index.html` in your web browser.
        """)
        
        # Create a versions.json file with summary data
        versions_data = []
        
        for i, version in enumerate(website_versions):
            folder_name = f"v{i+1}_{version.id}"
            
            # Add this version's data to the summary
            versions_data.append({
                "number": i+1,
                "id": version.id,
                "folder": folder_name,
                "description": version.description,
                "timestamp": version.timestamp
            })
            
            # Create folder for this version
            zipf.writestr(f"{folder_name}/index.html", f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{version.description}">
    <title>Website - Version {i+1}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
{version.html}
<script src="script.js"></script>
</body>
</html>""")
            
            zipf.writestr(f"{folder_name}/styles.css", version.css)
            zipf.writestr(f"{folder_name}/script.js", version.js)
            
            # Add version-specific metadata file
            metadata = {
                "version": i+1,
                "id": version.id,
                "description": version.description,
                "timestamp": version.timestamp
            }
            zipf.writestr(f"{folder_name}/metadata.json", json.dumps(metadata, indent=2))
        
        # Add the versions summary JSON
        zipf.writestr("versions.json", json.dumps(versions_data, indent=2))
    
    all_versions_zip.seek(0)
    return all_versions_zip.getvalue()

def generate_versions_summary(versions):
    """Generate a markdown summary of versions for the README."""
    summary = ""
    for i, version in enumerate(versions):
        summary += f"- **Version {i+1}** ({version.id}): {version.description[:50]}"
        summary += f" - Created: {version.timestamp}\n"
    return summary

def create_preview_html(version):
    """Create complete HTML for previewing in the app."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Website Preview</title>
        <style>
            {version.css}
        </style>
    </head>
    <body>
        {version.html}
        <script>
            {version.js}
        </script>
    </body>
    </html>
    """
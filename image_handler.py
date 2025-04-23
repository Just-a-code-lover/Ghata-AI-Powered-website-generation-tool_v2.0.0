import os
import requests
from typing import List, Dict

def get_images_from_pexels(query: str, per_page: int = 5) -> List[Dict]:
    """Fetch images from Pexels API based on query"""
    api_key = os.getenv("PEXELS_API_KEY")
    headers = {
        "Authorization": api_key
    }
    
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant image information
        images = []
        for photo in data.get("photos", []):
            images.append({
                "url": photo["src"]["large"],
                "width": photo["width"],
                "height": photo["height"],
                "alt": photo["alt"],
                "thumbnail": photo["src"]["tiny"]
            })
        return images
    except Exception as e:
        print(f"Error fetching images: {str(e)}")
        return []
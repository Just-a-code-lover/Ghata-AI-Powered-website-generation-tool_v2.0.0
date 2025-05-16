#llm_hander.py
import os
import re
import streamlit as st
from openai import OpenAI

def get_system_prompt(image_data=None):
    """Get the system prompt with optional image context"""
    base_prompt = """You are an elite web developer AI that generates and iterates on production-ready websites. Follow these rules strictly:

1. **Image Integration**  
   - Use the provided Pexels image URLs when available
   - Each image comes with metadata (dimensions, alt text)
   - Adapt image layout based on aspect ratios
   - Fallback to placeholders only if no images provided:
     - Unsplash: `https://source.unsplash.com/random/WxH/?keyword`
     - Picsum: `https://picsum.photos/WxH`

2. **Code Completeness Rule**
   - ALWAYS return the COMPLETE, FULL website code
   - Never return partial updates or code snippets
   - Include ALL HTML, CSS, and JavaScript in every response
   - Only give one HTML(index.html),CSS(style.css) and JS(script.js) in every response
   - Maintain all existing features when making changes
   Example:
     User: "Add a contact form"
     You must return: Complete HTML (with existing + new form), all CSS (including form styles), all JS (with form handling)

3. **Stateless Architecture**
   - Each response must be a fully functional standalone website
   - Include ALL previous features plus requested changes
   - Never assume code persistence between interactions
   Example:
     User: "Make the background darker"
     Wrong: Just return CSS changes
     Correct: Return entire website with updated background
     

4. **Stateless Continuity**  
   - Treat each interaction as part of an ongoing project
   - Never acknowledge statelessness
   - Preserve existing functionality when modifying

5. **Modification Pattern**
   - When modifying features:
     1. Start with the complete previous version
     2. Make requested changes
     3. Return entire codebase with changes integrated
   Example:
     User: "Add dark mode toggle"
     Response must include:
     ```html
     <!-- Complete HTML including navigation, content, AND new toggle -->
     ```
     ```css
     /* ALL existing styles PLUS new dark mode styles */
     ```
     ```javascript
     // ALL existing functionality PLUS dark mode logic */
     ```
      
6. **Deep Analysis Mode**
   - Analyze layout, colors, and typography choices
   - Consider user experience and accessibility
   - Optimize for performance and responsiveness
   - Document key decisions in comments
   - Think step by step

7. **Response Format**  
   Always structure responses as:
   ```html
   <!-- Complete HTML Code -->
   ```
   ```css
   /* Complete CSS Code*/
   ```
   ```javascript
   // Complete JavaScript Code
   ```

8. **Feature Integration**
   - Implement responsive design in ALL versions
   - Include error handling in ALL JavaScript
   - Maintain accessibility in ALL components
   - Document ALL code sections with comments

9. **Content Safety Filter**

   - Always scan user requests for inappropriate content (NSFW, harmful, toxic, etc.)
   - If detected, respond with: "I'm unable to generate content that may be inappropriate, harmful, or violate content policies."
   - Decline requests for adult content, violence, discrimination, illegal activities, or harmful material
   - Redirect conversation to appropriate and constructive website creation
   - Never generate code that could be used for harmful purposes, even if the request seems ambiguous

Remember: NEVER return partial code. ALWAYS return the COMPLETE website code with ALL features.
"""
    
    if image_data:
        # Build image context section
        image_context = "\nAvailable Images:\n"
        for idx, img in enumerate(image_data):
            image_context += (
                f"Image {idx + 1}:\n"
                f"- URL: {img['url']}\n"
                f"- Dimensions: {img['width']}x{img['height']}\n"
                f"- Alt text: {img['alt']}\n"
            )
        # Append image context to base prompt
        base_prompt += f"\n{image_context}\nUse these images appropriately in the generated website."
    
    return base_prompt

def generate_response(prompt, conversation_history=None, custom_system_prompt=None, model_choice="Better"):
    """Generate a response using the selected LLM with timeout handling."""
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY")
        )
        
        # Model configurations
        model_configs = {
            "Good": {
                "model": "nvidia/llama-3.3-nemotron-super-49b-v1",
                "temperature": 0.6,
                "top_p": 0.95,
                "max_tokens": 16384,
            },
            "Better": {
                "model": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
                "temperature": 0.6,
                "top_p": 0.95,
                "max_tokens": 16384,
            },
            "Best": {
                "model": "deepseek-ai/deepseek-r1",
                "temperature": 0.6,
                "top_p": 0.7,
                "max_tokens": 4096,
            }
        }
        
        # Select model config based on choice
        model_type = model_choice.split(" ")[0]  # Extract "Good", "Better", or "Best"
        config = model_configs[model_type]
        
        system_prompt = custom_system_prompt if custom_system_prompt else get_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})
        
        response_text = ""
        response_placeholder = st.empty()
        
        try:
            with st.spinner(f"Generating website using {model_type} model..."):
                completion = client.chat.completions.create(
                    model=config["model"],
                    messages=messages,
                    temperature=config["temperature"],
                    top_p=config["top_p"],
                    max_tokens=config["max_tokens"],
                    frequency_penalty=0.2,
                    presence_penalty=0.2,
                    stream=True
                )
                
                for chunk in completion:
                    if chunk.choices[0].delta.content is not None:
                        response_text += chunk.choices[0].delta.content
                        
        except Exception as api_error:
            st.error(f"Error with {model_type} model. Trying fallback model...")
            # Fallback to Good model if any error occurs
            fallback_config = model_configs["Good"]
            completion = client.chat.completions.create(
                model=fallback_config["model"],
                messages=messages,
                temperature=fallback_config["temperature"],
                top_p=fallback_config["top_p"],
                max_tokens=fallback_config["max_tokens"],
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content
        
        response_placeholder.empty()
        return response_text
        
    except Exception as e:
        st.error(f"Error connecting to API. Please check your API key and try again.")
        st.error(f"Detailed error: {str(e)}")
        return None
    
def extract_code_from_response(response):
    """Extract HTML, CSS, and JS code blocks from the LLM response."""
    html_code = ""
    css_code = ""
    js_code = ""

    # Extract HTML
    html_matches = re.findall(r"```html\s*([\s\S]*?)\s*```", response)
    if html_matches:
        html_code = html_matches[0].strip()

    # Extract CSS
    css_matches = re.findall(r"```css\s*([\s\S]*?)\s*```", response)
    if css_matches:
        css_code = css_matches[0].strip()

    # Extract JavaScript
    js_matches = re.findall(r"```(?:javascript|js)\s*([\s\S]*?)\s*```", response)
    if js_matches:
        js_code = js_matches[0].strip()

    # Handle inline CSS/JS in HTML (for models like DeepSeek)
    if not css_code and not js_code:
        inline_css = re.findall(r"<style>([\s\S]*?)</style>", html_code, re.IGNORECASE)
        inline_js = re.findall(r"<script>([\s\S]*?)</script>", html_code, re.IGNORECASE)

        if inline_css:
            css_code = inline_css[0].strip()
        if inline_js:
            js_code = inline_js[0].strip()

    return html_code, css_code, js_code

def clean_response_for_display(response):
    cleaned = re.sub(r'```(html|css|javascript|js)[\s\S]*?```', '[Code block removed for clarity]', response)
    cleaned = re.sub(r'```[\s\S]*?```', '[Code block removed for clarity]', cleaned)
    return cleaned
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

def generate_response(prompt, conversation_history=None, custom_system_prompt=None):
    """Generate a response using the LLM.
    
    Args:
        prompt (str): The user's input prompt
        conversation_history (list, optional): Previous conversation messages
        custom_system_prompt (str, optional): Custom system prompt to override default
    """
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY")
        )
        
        # Use custom system prompt if provided, otherwise get default
        system_prompt = custom_system_prompt if custom_system_prompt else get_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
            
        messages.append({"role": "user", "content": prompt})
        
        response_text = ""
        response_placeholder = st.empty()
        
        with st.spinner("Generating website..."):
            completion = client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
                messages=messages,
                temperature=0.75,
                top_p=0.98,
                max_tokens=16384,
                frequency_penalty=0.1,
                presence_penalty=0.1,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content
                    #response_placeholder.markdown(clean_response_for_display(response_text))
                    
        response_placeholder.empty()
        return response_text
        
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "Error: Unable to connect to the API."
    
def extract_code_from_response(response):
    html_code = ""
    css_code = ""
    js_code = ""

    html_matches = re.findall(r"```html\s*([\s\S]*?)\s*```", response)
    if html_matches:
        html_code = html_matches[0].strip()

    css_matches = re.findall(r"```css\s*([\s\S]*?)\s*```", response)
    if css_matches:
        css_code = css_matches[0].strip()

    js_matches = re.findall(r"```(?:javascript|js)\s*([\s\S]*?)\s*```", response)
    if js_matches:
        js_code = js_matches[0].strip()

    return html_code, css_code, js_code

def clean_response_for_display(response):
    cleaned = re.sub(r'```(html|css|javascript|js)[\s\S]*?```', '[Code block removed for clarity]', response)
    cleaned = re.sub(r'```[\s\S]*?```', '[Code block removed for clarity]', cleaned)
    return cleaned

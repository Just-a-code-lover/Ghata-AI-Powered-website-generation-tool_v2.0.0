import os
import re
import streamlit as st
from openai import OpenAI

def get_system_prompt():
    return """You are an elite web developer and designer AI with a reputation for creating stunning, 
    production-ready websites that exceed client expectations.
    
    ... (same system prompt rules as before) ...
    
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
    """

def generate_response(prompt, conversation_history=None):
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.environ.get("NVIDIA_API_KEY")
        )

        messages = [
            {"role": "system", "content": get_system_prompt()},
        ]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})

        response_text = ""
        response_placeholder = st.empty()

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
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content
                    response_placeholder.markdown(clean_response_for_display(response_text))

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
    cleaned = re.sub(r'```(html|css|javascript|js)[\s\S]*?```', '<em>[Code block removed for clarity]</em>', response)
    cleaned = re.sub(r'```[\s\S]*?```', '<em>[Code block removed for clarity]</em>', cleaned)
    return cleaned

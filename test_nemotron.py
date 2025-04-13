from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the key
API_KEY = os.getenv("NVIDIA_API_KEY")

from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Initialize client
client = ChatNVIDIA(
    model="nvidia/llama-3.3-nemotron-super-49b-v1",
    api_key=API_KEY,
    temperature=0.6,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    max_tokens=4096,
)

def test_llama_codegen(prompt: str):
    print("🧠 Sending prompt to LLaMA 3.3 NEMOTRON 49B...\n")
    generated_code = ""

    try:
        for chunk in client.stream([{"role": "user", "content": prompt}]):
            print(chunk.content, end="")  # Stream to console
            generated_code += chunk.content
        return generated_code
    except Exception as e:
        print(f"\n🚨 Error during generation: {e}")
        return None

if __name__ == "__main__":
    test_prompt = """
Generate a complete one-page travel agency website named 'GlobeTrek' with:
- Hero section with catchy tagline and background
- 3 travel package cards (with prices)
- Contact form
- Responsive layout
-Include some realed images from the web via links
-Recheck the css
Use a modern, clean design in blue and white.

Format as markdown code blocks:
```html
<!DOCTYPE html>...
/* styles.css */
// script.js
"""
    code = test_llama_codegen(test_prompt)

    if code:
        with open("llama3_nemotron_test_output.md", "w", encoding="utf-8") as f:
            f.write(code)
        print("\n✅ Output saved to llama3_nemotron_test_output.md")
    else:
        print("❌ Generation failed.")

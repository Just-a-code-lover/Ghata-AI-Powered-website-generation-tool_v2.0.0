from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the key
API_KEY = os.getenv("NVIDIA_API_KEY")

from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Now you can use the API_KEY
#chat = ChatNVIDIA(api_key=API_KEY)

# Initialize client
client = ChatNVIDIA(
    model="deepseek-ai/deepseek-r1",
    api_key=API_KEY,
    temperature=0.6,
    top_p=0.7,
    frequency_penalty=0,
    presence_penalty=0,
    max_tokens=4096,
)

def test_deepseek_codegen(prompt: str):
    print("🧠 Sending prompt to DeepSeek-R1...\n")
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
code = test_deepseek_codegen(test_prompt)

if code:
    with open("deepseek_r1_test_output1.md", "w", encoding="utf-8") as f:
        f.write(code)
    print("\n✅ Output saved to deepseek_r1_test_output.md")
else:
    print("❌ Generation failed.")

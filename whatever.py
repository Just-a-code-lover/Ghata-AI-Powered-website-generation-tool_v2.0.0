# Just use this and ignore everything else  
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the key
#API_KEY = os.getenv("NVIDIA_API_KEY")  

llm = ChatNVIDIA(  
    model="deepseek-ai/deepseek-r1",  
    api_key="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",  
    max_tokens=32768  # Max they allow  
)  

# Done. No fallbacks, no hybrid crap.  
response = llm.invoke("Make a damn website")  
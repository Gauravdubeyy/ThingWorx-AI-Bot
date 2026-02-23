import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

print("ALL AVAILABLE MODELS:")
try:
    for model in genai.list_models():
        print(f"Name: {model.name} | Methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")

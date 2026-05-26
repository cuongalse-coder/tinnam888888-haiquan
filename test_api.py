import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Try reading from Streamlit secrets if possible, or just print warning
    print("No GEMINI_API_KEY found in .env")

# We will just print the error message for each layer
models = [
    ('deep-research-max-preview-04-2026', 'google_search_retrieval'),
    ('gemini-3.1-pro-preview', 'google_search_retrieval'),
    ('gemini-pro-latest', 'google_search_retrieval'),
    ('gemini-3.5-flash', 'google_search_retrieval'),
    ('gemini-2.5-flash', 'google_search_retrieval'),
    ('gemini-1.5-pro', 'google_search_retrieval'),
    ('gemini-2.5-flash', None)
]

genai.configure(api_key=api_key)

for m, tool in models:
    try:
        if tool:
            model = genai.GenerativeModel(m, tools=tool)
        else:
            model = genai.GenerativeModel(m)
        response = model.generate_content("hello")
        print(f"SUCCESS: {m} with tools={tool}")
    except Exception as e:
        print(f"FAILED: {m} with tools={tool} -> {e}")

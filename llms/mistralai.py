import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

# Debug print - but be careful not to log your actual API key in production
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    print("WARNING: MISTRAL_API_KEY environment variable not found!")
else:
    print("MISTRAL_API_KEY is set (length:", len(api_key), "characters)")

model = "mistral-large-latest"

# Only create the LLM if we have an API key
if api_key:
    mistral_llm = ChatMistralAI(api_key=api_key, model=model)
else:
    raise ValueError("MISTRAL_API_KEY not found in environment variables!")
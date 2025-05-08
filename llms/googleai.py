from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI




load_dotenv()
api_key = os.environ["GOOGLE_API_KEY"]
google_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    api_key = api_key,
    temperature=0,
    max_tokens=None,
    timeout=10,
    max_retries=2,
)
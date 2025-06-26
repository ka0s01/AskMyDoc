import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini 1.5 Flash model
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Create a chat instance (use one per session)
chat_session = model.start_chat(history=[])

def chat_with_document(document_text, user_question):
    full_prompt = f"""
You are an AI assistant. Answer questions based on the following document.

DOCUMENT:
\"\"\"
{document_text}
\"\"\"
"""
    chat_session.send_message(full_prompt)  # Prime the model with the document
    response = chat_session.send_message(user_question)
    return response.text

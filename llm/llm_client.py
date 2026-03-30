import os
import google.generativeai as genai

def generate_answer(context, question):
    # Configure lazily inside the function so import never crashes
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable is not set."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""Answer based on context:

{context}

Question: {question}
"""
    response = model.generate_content(prompt)
    return response.text

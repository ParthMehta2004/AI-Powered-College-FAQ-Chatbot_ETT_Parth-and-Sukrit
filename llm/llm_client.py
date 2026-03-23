import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def generate_answer(context, question):
    prompt = f"""
Answer based on context:

{context}

Question: {question}
"""

    response = model.generate_content(prompt)
    return response.text

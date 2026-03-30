import os
from google import genai

def generate_answer(context, question):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable is not set."

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""You are a helpful college FAQ assistant. Answer the question using only the context below.
If the answer is not in the context, say "I don't have information on that."

Context:
{context}

Question: {question}

Answer:"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Error generating answer: {str(e)}"

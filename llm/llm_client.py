import os
import google.generativeai as genai
 
def generate_answer(context, question):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable is not set."
 
    genai.configure(api_key=api_key)
 
    # ✅ FIX: "gemini-pro" is shut down — use "gemini-2.5-flash" instead
    model = genai.GenerativeModel("gemini-2.5-flash")
 
    prompt = f"""You are a helpful college FAQ assistant. Answer the question using only the context below.
If the answer is not in the context, say "I don't have information on that."
 
Context:
{context}
 
Question: {question}
 
Answer:"""
 
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating answer: {str(e)}"
 

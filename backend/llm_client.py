import os
from groq import Groq


def generate_answer(context: str, question: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY environment variable is not set."
    try:
        client = Groq(api_key=api_key)
        prompt = (
            f"You are MUJ Chat, a helpful and friendly assistant for Manipal University "
            f"Jaipur (MUJ) students and staff. Answer the question using ONLY the context "
            f"provided below. If the answer is not found in the context, say 'I don't have "
            f"information on that in my current knowledge base. Please contact the university "
            f"office directly.' Be concise, friendly, and accurate.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        )
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM error: {e}"

import os
from groq import Groq

def generate_answer(context: str, question: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY is not set."

    try:
        client = Groq(api_key=api_key)
        prompt = f"""You are MUJ Chat, a helpful assistant for Manipal University Jaipur students and staff.
Answer the question using ONLY the context provided below.
If the answer is not in the context, say "I don't have information on that in my current knowledge base."
Be concise, friendly, and helpful.

Context:
{context}

Question: {question}
Answer:"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

import os
from groq import Groq

def generate_answer(context, question):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY environment variable is not set."

    try:
        client = Groq(api_key=api_key)

        prompt = f"""You are a helpful college FAQ assistant. Answer the question using only the context below.
If the answer is not in the context, say "I don't have information on that."

Context:
{context}

Question: {question}

Answer:"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.3,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating answer: {str(e)}"

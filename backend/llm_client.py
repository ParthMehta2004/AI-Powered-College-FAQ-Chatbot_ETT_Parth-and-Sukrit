import os
from groq import Groq

def generate_answer(context: str, question: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY environment variable is not set."
    try:
        client = Groq(api_key=api_key)
        prompt = f"""You are MUJ Chat, a helpful assistant for Manipal University Jaipur (MUJ) students and staff.

Your job is to answer questions using the context below, which is extracted from official MUJ documents.

IMPORTANT RULES:
- Use the context to answer even if it's in table or list format
- If the context has course codes, subject names, credits — present them clearly
- If the question is about a syllabus or curriculum, list out the subjects/courses from the context
- If the answer truly isn't in the context at all, say: "I don't have complete information on that. Please check the MUJ official website or contact the relevant department."
- Never say you lack information if the context clearly contains relevant data
- Be helpful, structured, and clear

Context:
{context}

Question: {question}

Answer:"""
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM error: {e}"

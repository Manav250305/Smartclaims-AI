import os
import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def reason_with_clauses(parsed_json, relevant_clauses):
    prompt = f"""
You are an insurance policy analyzer. Based on the user info:
{parsed_json}

And these retrieved clauses:
{relevant_clauses}

Decide if the procedure is approved. Respond in JSON format:
{{
  "decision": "Approved/Rejected",
  "amount": "...",
  "justification": [
    {{
      "clause": "...",
      "explanation": "..."
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a claim decision engine."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_query(raw_query):
    system_prompt = """Extract the following from the query:
- Age
- Gender
- Procedure
- City
- Policy Age (in months)

Return as JSON:
{
  "age": ...,
  "gender": "...",
  "procedure": "...",
  "location": "...",
  "policy_duration_months": ...
}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_query}
        ]
    )
    return response.choices[0].message.content
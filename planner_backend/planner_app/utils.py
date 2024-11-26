from openai import OpenAI
from django.conf import settings


client = OpenAI(

  base_url="https://openrouter.ai/api/v1",
  api_key="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",

)

completion = client.chat.completions.create(
  model="google/gemma-2-27b-it",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
)

print(completion.choices[0].message.content)
from openai import OpenAI
import os
os.environ["http_proxy"]="127.0.0.1:7890"
os.environ["https_proxy"]="127.0.0.1:7890"

# OPENAI_API_BASE="https://key.wenwen-ai.com/v1"
# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
# os.environ["OPENAI_API_BASE"] = OPENAI_API_BASE
client = OpenAI(api_key = "")

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
  ]
)
print(response.choices[0].message)

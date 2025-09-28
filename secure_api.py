# # from api_utils import test_openrouter_api

# # # ... rest of your code ...
# # # --- SCRIPT EXECUTION ---
# # if __name__ == "__main__":
# #     test_openrouter_api()

# # from openai import OpenAI

# # client = OpenAI(
# #   base_url="https://openrouter.ai/api/v1",
# #   api_key="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",
# # )

# # completion = client.chat.completions.create(
# #   extra_headers={
# #     "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
# #     "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
# #   },
# #   model="mistralai/mistral-7b-instruct:free",
# #   messages=[
# #     {
# #       "role": "user",
# #       "content": "What is the meaning of life?"
# #     }
# #   ]
# # )

# # print(completion.choices[0].message.content)
# import requests
# import json

# response = requests.post(
#   url="https://openrouter.ai/api/v1/chat/completions",
#   headers={
#     "Authorization": "Bearer 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",
#     "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
#     "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
#   },
#   data=json.dumps({
#     "model": "mistralai/mistral-7b-instruct:free", # Optional
#     "messages": [
#       {
#         "role": "user",
#         "content": "What is the meaning of life?"
#       }
#     ]
#   })
# )

import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",   # ⚠️ rotate this key!
    "HTTP-Referer": "<YOUR_SITE_URL>",        # optional
    "X-Title": "<YOUR_SITE_NAME>",            # optional
  },
  data=json.dumps({
    "model": "mistralai/mistral-7b-instruct:free",
    "messages": [
      {"role": "user", "content": "What is the meaning of life?"}
    ]
  })
)

# Raw response text (JSON string)
print(response.text)

# Or as parsed JSON
data = response.json()
print(json.dumps(data, indent=2))

# Extract the model's reply
print("Model reply:", data["choices"][0]["message"]["content"])

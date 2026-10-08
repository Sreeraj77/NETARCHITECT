from google import genai
from ai.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello to Sreeraj in one sentence."
)

print("\n===== Gemini Response =====\n")
print(response.text)
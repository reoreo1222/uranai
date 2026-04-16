import os
from dotenv import load_dotenv

load_dotenv()

PERSONA = {
    "credentials": "住職歴15年・鑑定実績1,200件",
    "tagline": "煩悩はあなたの潜在的な力の裏側にある",
    "stance": "悩みを肯定し、その人の本来の力を引き出す",
}

GENERATION = {
    "model": os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile"),
    "max_tokens": 5000,
    "temperature": 0.8,
    "target_char_min": 3500,
    "target_char_max": 4500,
}

OUTPUT = {
    "dir": os.getenv("OUTPUT_DIR", "./output"),
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

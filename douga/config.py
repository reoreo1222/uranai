import os
from dotenv import load_dotenv

load_dotenv()

# ペルソナ設定（住職×AI占いブランド）
PERSONA = {
    "credentials": "住職歴15年・鑑定実績1,200件",
    "brand_tagline": "1500年続く仏教の教えで、あなたの因縁を読み解く",
    "cta_line": "プロフのLINEへ",
    "free_offer": "初回無料鑑定",
    "cta_action": "「無料鑑定」と送るだけでOK",
}

# 生成設定
GENERATION = {
    "model": os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile"),
    "max_tokens": 800,
    "temperature": 0.9,
    "target_char_min": 150,
    "target_char_max": 300,
}

# 出力設定
OUTPUT = {
    "dir": os.getenv("OUTPUT_DIR", "./output"),
    "default_format": "both",
    "partial_save_interval": 10,
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

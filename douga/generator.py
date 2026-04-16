import time
import random
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

from groq import Groq

from config import GROQ_API_KEY, GENERATION, PERSONA
from templates import ContentTemplate


@dataclass
class TikTokScript:
    script_id: str
    category: str
    category_label: str
    title: str
    duration_estimate: str
    hook: str
    content: str
    cta: str
    full_script: str
    char_count: int
    hashtags: str
    notes: str
    generated_at: str


SYSTEM_PROMPT = f"""あなたはTikTok動画台本の専門家です。
仏教住職×AI占いブランドのTikTok動画台本を作成します。

キャラクター設定:
- {PERSONA['credentials']}の仏教僧侶
- {PERSONA['brand_tagline']}
- 仏教の慈悲の心で相談者に寄り添う
- 「煩悩があるのは当然、それでも救われる」という温かいスタンス
- 権威と親しみやすさを両立する話し方

台本の必須要件:
- 合計150〜300文字（読み上げ時間15〜60秒）
- 毎回まったく異なる切り口・表現・言い回しを使うこと
- 視聴者の感情（不安・希望・好奇心）に訴える言葉を使う
- 断言調と問いかけを組み合わせる

必ず以下のフォーマットで出力してください（他のテキストは一切不要）:
[HOOK]
（ここに視聴者を最初の3秒で止める一言〜3行）

[CONTENT]
（ここに仏教の智慧×占いの本編100〜200字）

[CTA]
（ここにLINE誘導の行動促進2〜3行）

[HASHTAGS]
（ここに#タグをスペース区切りで）

[NOTES]
（ここに撮影のヒント1〜2行）"""


def _parse_response(text: str) -> dict:
    sections = {
        "hook": "",
        "content": "",
        "cta": "",
        "hashtags": "",
        "notes": "",
    }
    mapping = {
        "[HOOK]": "hook",
        "[CONTENT]": "content",
        "[CTA]": "cta",
        "[HASHTAGS]": "hashtags",
        "[NOTES]": "notes",
    }
    current_key = None
    buffer = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped in mapping:
            if current_key and buffer:
                sections[current_key] = "\n".join(buffer).strip()
            current_key = mapping[stripped]
            buffer = []
        elif current_key is not None:
            buffer.append(line)

    if current_key and buffer:
        sections[current_key] = "\n".join(buffer).strip()

    return sections


def _estimate_duration(char_count: int) -> str:
    seconds = int(char_count / 350 * 60)
    return f"約{seconds}秒"


def generate_script(
    template: ContentTemplate,
    index: int,
    topic: Optional[str] = None,
    model: Optional[str] = None,
) -> TikTokScript:
    if not GROQ_API_KEY:
        raise RuntimeError(
            ".env ファイルに GROQ_API_KEY が設定されていません。\n"
            "https://console.groq.com でAPIキーを取得し、.env に設定してください。"
        )

    chosen_topic = topic or random.choice(template.topic_variations)
    used_model = model or GENERATION["model"]

    today_str = date.today().strftime("%-m月%-d日")
    user_prompt = f"""カテゴリ: {template.label}
テーマ: {chosen_topic}
今日の日付: {today_str}（フックに「{today_str}の〇〇運」「{today_str}限定」などを積極的に使ってください）
フックスタイル: {template.hook_style}
CTA: {template.cta_variant}
推奨ハッシュタグ: {', '.join(template.hashtags)}
撮影メモ: {template.filming_notes}

上記の設定で、新鮮で魅力的なTikTok台本を1本作成してください。
文字数は合計150〜300字以内に収めてください。"""

    client = Groq(api_key=GROQ_API_KEY)

    last_error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=used_model,
                max_tokens=GENERATION["max_tokens"],
                temperature=GENERATION["temperature"],
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw_text = response.choices[0].message.content
            sections = _parse_response(raw_text)

            full_script = "\n".join([
                sections["hook"],
                sections["content"],
                sections["cta"],
            ]).strip()

            char_count = len(full_script.replace("\n", ""))
            min_c = GENERATION["target_char_min"]
            max_c = GENERATION["target_char_max"]

            if attempt < 2 and not (min_c <= char_count <= max_c):
                time.sleep(0.5)
                continue

            script_id = f"{template.key}_{index:03d}"
            title = chosen_topic[:20]

            return TikTokScript(
                script_id=script_id,
                category=template.key,
                category_label=template.label,
                title=title,
                duration_estimate=_estimate_duration(char_count),
                hook=sections["hook"],
                content=sections["content"],
                cta=sections["cta"],
                full_script=full_script,
                char_count=char_count,
                hashtags=sections["hashtags"] or " ".join(template.hashtags),
                notes=sections["notes"] or template.filming_notes,
                generated_at=datetime.now().isoformat(),
            )

        except Exception as e:
            last_error = e
            wait = 2 ** attempt
            print(f"  API エラー（試行 {attempt + 1}/3）: {e}。{wait}秒後にリトライ...")
            time.sleep(wait)

    raise RuntimeError(f"台本生成に失敗しました（3回試行）: {last_error}")


def format_script_for_display(script: TikTokScript) -> str:
    separator = "=" * 60
    return f"""{separator}
【台本 #{script.script_id}】{script.category_label} - "{script.title}"
推定時間: {script.duration_estimate} | 文字数: {script.char_count}字
{separator}

[HOOK - 最初の3秒]
{script.hook}

[CONTENT - 本編]
{script.content}

[CTA - 行動促進]
{script.cta}

[ハッシュタグ]
{script.hashtags}

[撮影メモ]
{script.notes}
{separator}
"""

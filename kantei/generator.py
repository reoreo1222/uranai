import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from groq import Groq

from config import GROQ_API_KEY, GENERATION, PERSONA


@dataclass
class KanteiResult:
    customer_name: str
    birthday: str
    worries: list
    intro: str
    star_reading: str
    bonno: str
    talent: str
    worry_answers: str
    fortune_3months: str
    action_guide: str
    closing: str
    full_text: str
    char_count: int
    generated_at: str


SYSTEM_PROMPT = f"""あなたは住職歴15年の仏教僧侶であり、占い鑑定師です。
「{PERSONA['tagline']}」という信念のもと、相談者一人ひとりに寄り添う鑑定を行います。

【キャラクター】
- {PERSONA['credentials']}
- 仏教の智慧と占い（西洋占星術・数秘術・九星気学）を組み合わせた独自の鑑定スタイル
- 悩みや執着を「弱さ」ではなく「まだ使われていない力の源泉」として捉える
- 温かく、しかし核心を突く言葉を使う
- 精神論ではなく、具体的で実践的なアドバイスを重視する

【鑑定の哲学】
「煩悩具足の凡夫」—人が煩悩を持つのは当然であり、それを否定するのではなく受け入れ、
その奥にある潜在的な力を引き出すことが真の鑑定である。
執着が強い人は、それだけ本気で生きている。怒りやすい人は正義感という才能を持っている。
心配性な人は、深く愛せる人だ。欲が強い人は、エネルギーが溢れている証拠だ。

必ず以下のフォーマットで出力してください（他のテキストは一切不要）:

[はじめに]
（相談者への挨拶・今の状況への共感・この鑑定でわかること。200〜300字）

[星読み]
（生年月日・数秘術・西洋占星術をもとにした、その人の本質的な特性と傾向の分析。400〜600字）

[あなたの煩悩]
（108の煩悩の中から、この人が特に持ちやすい煩悩を2〜3つ特定し、その性質と由来を解説する。400〜600字）

[煩悩から才能へ]
（特定した煩悩が、実はどんな才能・強みの裏側にあるかを転換する。「○○という煩悩は、○○という才能だ」という形で力強く語りかける。400〜500字）

[3つの悩みへの回答]
（それぞれの悩みに対して、住職の視点と占いの分析を合わせた丁寧な回答。合計800〜1000字）

[3ヶ月の運勢]
（1ヶ月目・2ヶ月目・3ヶ月目それぞれの流れと注意点。400〜500字）

[行動指針]
（今日から動ける具体的な3つの行動。精神論ではなく実践的な内容。300〜400字）

[住職からの言葉]
（仏教の言葉・智慧を引用しながら、この人へのメッセージで締める。200〜300字）"""


SECTION_KEYS = [
    "はじめに",
    "星読み",
    "あなたの煩悩",
    "煩悩から才能へ",
    "3つの悩みへの回答",
    "3ヶ月の運勢",
    "行動指針",
    "住職からの言葉",
]


def _parse_response(text: str) -> dict:
    sections = {k: "" for k in SECTION_KEYS}
    mapping = {f"[{k}]": k for k in SECTION_KEYS}
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


def generate_kantei(
    name: str,
    birthday: str,
    worry1: str,
    worry2: str,
    worry3: str,
    model: Optional[str] = None,
) -> KanteiResult:
    if not GROQ_API_KEY:
        raise RuntimeError(
            ".env ファイルに GROQ_API_KEY が設定されていません。\n"
            "https://console.groq.com でAPIキーを取得し、.env に設定してください。"
        )

    used_model = model or GENERATION["model"]

    user_prompt = f"""以下の相談者の煩悩解脱鑑定を行ってください。

【相談者情報】
お名前: {name}
生年月日: {birthday}

【3つの悩み】
1. {worry1}
2. {worry2}
3. {worry3}

約4,000字の丁寧な鑑定文を、指定のフォーマットで作成してください。
各セクションは指定の文字数を守り、{name}さんへの鑑定として直接語りかける文体で書いてください。"""

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

            full_text = "\n\n".join(
                sections[k] for k in SECTION_KEYS if sections[k]
            ).strip()

            char_count = len(full_text.replace("\n", ""))
            min_c = GENERATION["target_char_min"]

            if attempt < 2 and char_count < min_c:
                print(f"  文字数不足（{char_count}字）。再生成中...")
                time.sleep(1)
                continue

            return KanteiResult(
                customer_name=name,
                birthday=birthday,
                worries=[worry1, worry2, worry3],
                intro=sections["はじめに"],
                star_reading=sections["星読み"],
                bonno=sections["あなたの煩悩"],
                talent=sections["煩悩から才能へ"],
                worry_answers=sections["3つの悩みへの回答"],
                fortune_3months=sections["3ヶ月の運勢"],
                action_guide=sections["行動指針"],
                closing=sections["住職からの言葉"],
                full_text=full_text,
                char_count=char_count,
                generated_at=datetime.now().isoformat(),
            )

        except Exception as e:
            last_error = e
            wait = 2 ** attempt
            print(f"  API エラー（試行 {attempt + 1}/3）: {e}。{wait}秒後にリトライ...")
            time.sleep(wait)

    raise RuntimeError(f"鑑定生成に失敗しました（3回試行）: {last_error}")


def format_for_display(result: KanteiResult) -> str:
    sep = "=" * 60
    worries_text = "\n".join(f"  {i+1}. {w}" for i, w in enumerate(result.worries))
    return f"""{sep}
■ 煩悩解脱鑑定　{result.customer_name}様
  生年月日: {result.birthday}
  ご相談内容:
{worries_text}
  生成日時: {result.generated_at[:10]}
  文字数　: {result.char_count}字
{sep}

【はじめに】
{result.intro}

【星読み】
{result.star_reading}

【あなたの煩悩】
{result.bonno}

【煩悩から才能へ】
{result.talent}

【3つの悩みへの回答】
{result.worry_answers}

【3ヶ月の運勢】
{result.fortune_3months}

【行動指針】
{result.action_guide}

【住職からの言葉】
{result.closing}

{sep}"""

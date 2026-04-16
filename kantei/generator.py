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


SYSTEM_PROMPT = """あなたは現役の住職であり、占い鑑定師です。住職歴15年、鑑定実績1,200件以上。
お寺で毎日のように人の苦しみと向き合い、仏教の智慧と占い（西洋占星術・数秘術・九星気学）を組み合わせた独自の鑑定を行っています。

【文体・書き方の絶対ルール】
- 現役住職として、一人称で語りかけること。「私は住職として〜」「長年お寺でたくさんの方を見てきました」など
- 冒頭の[はじめに]は、挨拶や前置きを一切せず、いきなり「あなたの煩悩はこれです」と宣言することから始める
  例：「申し上げます。あなたが今抱えているのは、108の煩悩の中の『慢（まん）』です。」
  例：「率直に言います。あなたの根本にある煩悩は『渇愛（かつあい）』です。」
- 断定する。「〜かもしれません」「〜と思われます」は使わない。住職として見えたことを言い切る
- 文章に変化をつける。短い一文と長い一文を混ぜる。同じリズムが続かないようにする
- 箇条書きは絶対に使わない。すべて文章で書く
- 「まず」「次に」「また」「さらに」「そして」が連続して並ぶような構成にしない
- 108の煩悩から具体的な名前を必ず使う（貪欲・瞋恚・慢・疑・渇愛・執着・嫉・慳・掉挙・惛沈・邪見・失念 など）
- 相談者の悩みと煩悩を具体的に紐づけて語る。抽象論ではなく、その人の悩みそのものを仏教の言葉で言い直す

【108の煩悩の主なもの（参考）】
貪欲（とんよく）過度な欲求、渇愛（かつあい）乾いた渇望、瞋恚（しんに）怒り憎しみ、
慢（まん）承認欲・プライド、疑（ぎ）自己不信・疑念、邪見（じゃけん）歪んだ自己像、
嫉（しつ）嫉妬、慳（けん）執着・手放せない、悔（け）後悔・自責、
掉挙（じょうこ）焦り・落ち着けない、惛沈（こんじん）重さ・沈み込み、
失念（しつねん）自分を見失う、散乱（さんらん）心が定まらない、
憂（う）悲しみ・憂い、懈怠（けたい）気力が出ない

必ず以下のフォーマットのみで出力してください（前置きや後書き不要）:

[はじめに]
（前置きなし。冒頭から「あなたの煩悩は〇〇です」と宣言し、その煩悩と3つの悩みがどう繋がっているかを住職として語る。250〜350字）

[星読み]
（生年月日・数秘術・西洋占星術から、この人が生まれ持った本質・気質・人生の流れを読む。データや分析ではなく、「あなたはこういう人間だ」と直接語りかける口調で。400〜600字）

[あなたの煩悩]
（冒頭で宣言した煩悩を深掘りする。この煩悩がどこから来るのか、どう作用しているのか、仏教的な背景を交えながら、その人の人生のパターンとして語る。400〜600字）

[煩悩から才能へ]
（その煩悩が実は才能の裏側であることを、住職として力強く宣言する。「この煩悩を持つ人間は、裏を返せば〇〇だ」という転換を、説教ではなく確信として語る。400〜500字）

[3つの悩みへの回答]
（3つの悩みそれぞれに、住職の視点と占いの両方から答える。親切な解説ではなく、長年人の苦しみを見てきた者として核心を突く言葉で。合計800〜1000字）

[3ヶ月の運勢]
（1ヶ月目・2ヶ月目・3ヶ月目の流れを、占いの読みとして語る。注意点も含めて。400〜500字）

[行動指針]
（「今日からこれをしてください」という具体的な行動を、住職として指示する。精神論ではなく実践。300〜400字）

[住職からの言葉]
（仏教の言葉を引用しながら、この人へ最後に伝えたいことを語る。締めくくりとして、相手の背中を押す一言を必ず入れる。200〜300字）"""


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

    user_prompt = f"""相談者情報:
名前: {name}
生年月日: {birthday}
悩み1: {worry1}
悩み2: {worry2}
悩み3: {worry3}

{name}さんへの鑑定を行ってください。
冒頭[はじめに]では前置きなし・挨拶なしで、すぐに「あなたの煩悩は〇〇です」と108の煩悩の名前を使って宣言してください。
全体を通して現役住職として直接{name}さんに語りかける文体で、約4,000字で書いてください。"""

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

"""
煩悩解脱鑑定 — Webアプリ
"""

import html
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent))
from generator import generate_kantei

# ── ページ設定 ──────────────────────────────────────────
st.set_page_config(
    page_title="煩悩解脱鑑定",
    page_icon="🙏",
    layout="centered",
)

# ── グローバルCSS（Streamlit UI部分） ────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Serif JP', serif; }
</style>
""", unsafe_allow_html=True)

# ── ヘッダー ────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 0.5rem;">
    <div style="font-size:0.7rem; letter-spacing:0.4em; color:#9b8fa8; margin-bottom:0.5rem;">
        BONNO GEDATSU KANTEI
    </div>
    <div style="font-size:1.9rem; font-weight:700; color:#3b2a5c; letter-spacing:0.2em;">
        🙏 煩悩解脱鑑定
    </div>
    <div style="font-size:0.82rem; color:#9b8fa8; margin-top:0.4rem; letter-spacing:0.08em;">
        住職 × AI ｜ あなたの煩悩を才能に変える人生鑑定
    </div>
    <div style="width:50px; height:2px; background:linear-gradient(90deg,#5B4A8C,#c8a96e);
                margin:1rem auto 1.5rem;"></div>
</div>
""", unsafe_allow_html=True)

# ── 入力フォーム ────────────────────────────────────────
with st.form("kantei_form"):
    st.markdown("#### 📋 相談者情報")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("お名前", placeholder="例：山田 太郎")
    with col2:
        birthday = st.text_input("生年月日", placeholder="例：1990-03-15")

    st.markdown("---")
    st.markdown("**今抱えているお悩みを3つ教えてください**")
    worry1 = st.text_area("悩み①", placeholder="例：仕事で頑張っているのに評価されない", height=75)
    worry2 = st.text_area("悩み②", placeholder="例：お金の不安がいつも頭にある", height=75)
    worry3 = st.text_area("悩み③", placeholder="例：人に合わせすぎて本音が言えない", height=75)

    submitted = st.form_submit_button("🔮  鑑定を開始する", use_container_width=True)


# ── 鑑定実行 ────────────────────────────────────────────
if submitted:
    missing = [label for label, val in [
        ("お名前", name), ("生年月日", birthday),
        ("悩み①", worry1), ("悩み②", worry2), ("悩み③", worry3),
    ] if not val.strip()]

    if missing:
        st.error(f"未入力の項目があります：{'　/　'.join(missing)}")
    else:
        with st.spinner("住職が鑑定中です... しばらくお待ちください（約30〜60秒）"):
            try:
                result = generate_kantei(
                    name=name.strip(),
                    birthday=birthday.strip(),
                    worry1=worry1.strip(),
                    worry2=worry2.strip(),
                    worry3=worry3.strip(),
                )
            except RuntimeError as e:
                st.error(f"エラーが発生しました：{e}")
                st.stop()

        st.success(f"✅ 鑑定完了 — {result.char_count}字")

        # ── 鑑定書HTML構築 ──────────────────────────────
        def e(text: str) -> str:
            return html.escape(text or "").replace("\n", "<br>")

        display_sections = [
            ("はじめに",          result.intro),
            ("星読み",            result.star_reading),
            ("あなたの煩悩",      result.bonno),
            ("煩悩から才能へ",    result.talent),
            ("3つの悩みへの回答", result.worry_answers),
            ("3ヶ月の運勢",       result.fortune_3months),
            ("行動指針",          result.action_guide),
            ("住職からの言葉",    result.closing),
        ]

        sections_html = "".join(f"""
        <div class="section">
            <div class="section-title">
                <span class="ornament"></span>
                <span class="title-text">【{title}】</span>
            </div>
            <div class="section-body">{e(body)}</div>
        </div>""" for title, body in display_sections if body)

        bonno_name = e(result.bonno_declaration) if result.bonno_declaration else "―"

        doc_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Noto Serif JP', serif;
    background: #f9f7f3;
    padding: 24px 16px 40px;
    color: #3a3430;
    line-height: 2.0;
  }}

  /* ── ドキュメント本体 ── */
  .document {{
    background: #fff;
    border: 1px solid #ddd6c8;
    max-width: 760px;
    margin: 0 auto;
    padding: 48px 52px 56px;
    box-shadow: 0 4px 28px rgba(59,42,92,0.10);
    position: relative;
  }}
  .document::before {{
    content: '';
    position: absolute;
    inset: 9px;
    border: 1px solid #ede6d8;
    pointer-events: none;
  }}

  /* ── ヘッダー ── */
  .doc-header {{
    text-align: center;
    padding-bottom: 28px;
    margin-bottom: 28px;
    border-bottom: 1px solid #ddd6c8;
  }}
  .doc-header .small-label {{
    font-size: 10px;
    letter-spacing: 0.45em;
    color: #aaa;
    margin-bottom: 10px;
  }}
  .doc-header .doc-title {{
    font-size: 22px;
    font-weight: 700;
    color: #3b2a5c;
    letter-spacing: 0.35em;
    margin-bottom: 16px;
  }}
  .doc-header .meta {{
    font-size: 12px;
    color: #888;
    line-height: 2.0;
  }}
  .doc-header .char-count {{
    display: inline-block;
    background: #f0eeff;
    color: #5B4A8C;
    border-radius: 20px;
    padding: 2px 14px;
    font-size: 11px;
    margin-top: 8px;
    letter-spacing: 0.05em;
  }}

  /* ── 煩悩バッジ ── */
  .bonno-box {{
    background: linear-gradient(135deg, #2e1f4d 0%, #5B4A8C 60%, #7a6aaa 100%);
    color: #fff;
    border-radius: 10px;
    padding: 24px 28px;
    margin: 0 0 36px;
    text-align: center;
    box-shadow: 0 4px 18px rgba(59,42,92,0.25);
  }}
  .bonno-box .bonno-label {{
    font-size: 10px;
    letter-spacing: 0.4em;
    opacity: 0.65;
    margin-bottom: 10px;
  }}
  .bonno-box .bonno-name {{
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 0.12em;
    line-height: 1.5;
    margin-bottom: 8px;
  }}
  .bonno-box .bonno-sub {{
    font-size: 11px;
    opacity: 0.6;
    letter-spacing: 0.08em;
  }}

  /* ── セクション ── */
  .section {{
    margin-bottom: 32px;
  }}
  .section-title {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }}
  .ornament {{
    display: inline-block;
    width: 3px;
    height: 16px;
    background: linear-gradient(180deg, #5B4A8C 0%, #c8a96e 100%);
    border-radius: 2px;
    flex-shrink: 0;
  }}
  .title-text {{
    font-size: 13px;
    font-weight: 700;
    color: #3b2a5c;
    letter-spacing: 0.12em;
  }}
  .section-body {{
    font-size: 14px;
    color: #3a3430;
    line-height: 2.3;
  }}

  /* ── フッター ── */
  .doc-footer {{
    text-align: center;
    margin-top: 44px;
    padding-top: 20px;
    border-top: 1px solid #ddd6c8;
    color: #bbb;
    font-size: 11px;
    letter-spacing: 0.12em;
    line-height: 2.2;
  }}
</style>
</head>
<body>
<div class="document">

  <div class="doc-header">
    <div class="small-label">KANTEI DOCUMENT</div>
    <div class="doc-title">煩 悩 解 脱 鑑 定 書</div>
    <div class="meta">
      {e(result.customer_name)} 様 &nbsp;|&nbsp; 生年月日：{e(result.birthday)}<br>
      鑑定日：{result.generated_at[:10]}
    </div>
    <div class="char-count">全 {result.char_count} 字</div>
  </div>

  <div class="bonno-box">
    <div class="bonno-label">▷ あなたの煩悩（108煩悩より特定）</div>
    <div class="bonno-name">{bonno_name}</div>
    <div class="bonno-sub">この煩悩があなたの悩みの根源であり、才能の源泉です</div>
  </div>

  {sections_html}

  <div class="doc-footer">
    🙏 住職歴15年 &nbsp;×&nbsp; 鑑定実績1,200件<br>
    煩悩はあなたの潜在的な力の裏側にある
  </div>

</div>
</body>
</html>"""

        # コンテンツ量に応じて高さを動的計算
        estimated_height = min(max(result.char_count * 2 + 800, 2400), 6000)
        components.html(doc_html, height=estimated_height, scrolling=True)

        # ── ダウンロード ────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        safe_name = result.customer_name.replace(" ", "_").replace("\u3000", "_")
        filename = f"鑑定書_{safe_name}_{result.generated_at[:10]}.txt"
        st.download_button(
            label="📄  鑑定書をテキストでダウンロード",
            data=result.full_text.encode("utf-8"),
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
        )

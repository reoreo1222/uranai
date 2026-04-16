"""
煩悩解脱鑑定 — Webアプリ
"""

import sys
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from generator import generate_kantei, KanteiResult

# ── ページ設定 ──────────────────────────────────────────
st.set_page_config(
    page_title="煩悩解脱鑑定",
    page_icon="🙏",
    layout="centered",
)

# ── スタイル ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Serif JP', serif;
}

/* ヘッダー */
.site-header {
    text-align: center;
    padding: 2rem 0 1rem;
    border-bottom: 2px solid #5B4A8C;
    margin-bottom: 2rem;
}
.site-header h1 {
    font-size: 1.8rem;
    color: #5B4A8C;
    margin: 0;
    letter-spacing: 0.15em;
}
.site-header p {
    color: #888;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

/* 入力フォーム */
.form-section {
    background: #faf9ff;
    border: 1px solid #ddd8f5;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
}
.form-section h2 {
    color: #5B4A8C;
    font-size: 1.1rem;
    margin-bottom: 1.2rem;
    border-left: 4px solid #5B4A8C;
    padding-left: 0.75rem;
}

/* 鑑定書ドキュメント */
.document-wrapper {
    background: #fffef8;
    border: 1px solid #c8b89a;
    border-radius: 4px;
    padding: 3rem 3.5rem;
    margin-top: 2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    line-height: 2.0;
}
.doc-header {
    text-align: center;
    border-bottom: 2px double #5B4A8C;
    padding-bottom: 1.5rem;
    margin-bottom: 2rem;
}
.doc-title {
    font-size: 1.6rem;
    color: #5B4A8C;
    letter-spacing: 0.3em;
    margin-bottom: 0.5rem;
}
.doc-meta {
    font-size: 0.85rem;
    color: #888;
    letter-spacing: 0.05em;
}
.doc-section {
    margin-bottom: 2.2rem;
}
.doc-section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #5B4A8C;
    border-bottom: 1px solid #ddd8f5;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
    letter-spacing: 0.1em;
}
.doc-section-body {
    font-size: 0.95rem;
    color: #333;
    white-space: pre-wrap;
}
.doc-footer {
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #c8b89a;
    color: #888;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
}
.char-badge {
    display: inline-block;
    background: #f0eeff;
    color: #5B4A8C;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── ヘッダー ────────────────────────────────────────────
st.markdown("""
<div class="site-header">
    <h1>🙏 煩悩解脱鑑定</h1>
    <p>住職 × AI ｜ あなたの煩悩を才能に変える人生鑑定</p>
</div>
""", unsafe_allow_html=True)


# ── 入力フォーム ────────────────────────────────────────
st.markdown('<div class="form-section"><h2>📋 相談者情報の入力</h2></div>',
            unsafe_allow_html=True)

with st.form("kantei_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("お名前", placeholder="例：山田 太郎")
    with col2:
        birthday = st.text_input("生年月日", placeholder="例：1990-03-15")

    st.markdown("---")
    st.markdown("**今抱えているお悩みを3つ教えてください**")
    worry1 = st.text_area("悩み①", placeholder="例：仕事がうまくいかず、自分に自信が持てない", height=80)
    worry2 = st.text_area("悩み②", placeholder="例：お金の不安がいつも頭から離れない", height=80)
    worry3 = st.text_area("悩み③", placeholder="例：人間関係で疲れてしまい、孤独を感じる", height=80)

    submitted = st.form_submit_button("🔮  鑑定を開始する", use_container_width=True)


# ── 鑑定実行 ────────────────────────────────────────────
if submitted:
    # バリデーション
    missing = []
    if not name.strip():     missing.append("お名前")
    if not birthday.strip(): missing.append("生年月日")
    if not worry1.strip():   missing.append("悩み①")
    if not worry2.strip():   missing.append("悩み②")
    if not worry3.strip():   missing.append("悩み③")

    if missing:
        st.error(f"未入力の項目があります：{' / '.join(missing)}")
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

        # ── 鑑定書ドキュメント表示 ──
        worries_html = "".join(
            f"<div style='font-size:0.85rem;color:#666;'>　{i+1}. {w}</div>"
            for i, w in enumerate(result.worries)
        )
        sections = [
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
            <div class="doc-section">
                <div class="doc-section-title">【{title}】</div>
                <div class="doc-section-body">{body}</div>
            </div>
        """ for title, body in sections if body)

        st.markdown(f"""
        <div class="document-wrapper">
            <div class="doc-header">
                <div class="doc-title">煩 悩 解 脱 鑑 定 書</div>
                <div class="doc-meta">
                    {result.customer_name} 様　｜　生年月日：{result.birthday}<br>
                    鑑定日：{result.generated_at[:10]}
                </div>
                <div style="margin-top:0.8rem;">{worries_html}</div>
                <div class="char-badge">全 {result.char_count} 字</div>
            </div>
            {sections_html}
            <div class="doc-footer">
                🙏 住職歴15年 × 鑑定実績1,200件<br>
                煩悩はあなたの潜在的な力の裏側にある
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── ダウンロードボタン ──
        st.markdown("<br>", unsafe_allow_html=True)
        download_text = result.full_text
        safe_name = result.customer_name.replace(" ", "_").replace("\u3000", "_")
        filename = f"鑑定書_{safe_name}_{result.generated_at[:10]}.txt"
        st.download_button(
            label="📄  鑑定書をテキストでダウンロード",
            data=download_text.encode("utf-8"),
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
        )

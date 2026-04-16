"""
煩悩解脱鑑定 — Webアプリ
"""

import html
import sys
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

# ── グローバルスタイル ───────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Serif JP', serif;
    background: #f9f7f3;
}

/* ヘッダー */
.site-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.site-header .en {
    font-size: 0.7rem;
    letter-spacing: 0.4em;
    color: #9b8fa8;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.site-header h1 {
    font-size: 2rem;
    color: #3b2a5c;
    letter-spacing: 0.25em;
    margin: 0 0 0.5rem;
    font-weight: 700;
}
.site-header .tagline {
    color: #9b8fa8;
    font-size: 0.82rem;
    letter-spacing: 0.1em;
}
.header-divider {
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, #5B4A8C, #c8a96e);
    margin: 1rem auto 2rem;
    border: none;
}

/* ─── 鑑定書 ─────────────────────────────────────── */
.document {
    background: #fff;
    border: 1px solid #e0d9cc;
    border-radius: 2px;
    padding: 3rem 3.5rem 3.5rem;
    box-shadow: 0 4px 24px rgba(59,42,92,0.08);
    position: relative;
    line-height: 2.1;
}
.document::before {
    content: '';
    position: absolute;
    top: 8px; left: 8px; right: 8px; bottom: 8px;
    border: 1px solid #e8e0d0;
    pointer-events: none;
}

/* ドキュメントヘッダー */
.doc-top {
    text-align: center;
    padding-bottom: 2rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #e0d9cc;
}
.doc-top .label {
    font-size: 0.7rem;
    letter-spacing: 0.4em;
    color: #9b8fa8;
    margin-bottom: 0.8rem;
}
.doc-top .title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #3b2a5c;
    letter-spacing: 0.3em;
    margin-bottom: 1.2rem;
}
.doc-top .meta {
    font-size: 0.82rem;
    color: #888;
    line-height: 1.9;
}

/* 煩悩バッジ */
.bonno-box {
    background: linear-gradient(135deg, #3b2a5c 0%, #5B4A8C 100%);
    color: #fff;
    border-radius: 8px;
    padding: 1.6rem 2rem;
    margin: 1.8rem 0 2.2rem;
    text-align: center;
}
.bonno-box .label {
    font-size: 0.68rem;
    letter-spacing: 0.35em;
    opacity: 0.7;
    margin-bottom: 0.6rem;
}
.bonno-box .name {
    font-size: 1.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    line-height: 1.4;
}
.bonno-box .sub {
    font-size: 0.75rem;
    opacity: 0.65;
    margin-top: 0.5rem;
    letter-spacing: 0.08em;
}

/* セクション */
.section {
    margin-bottom: 2.4rem;
}
.section-title {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
}
.section-title .ornament {
    width: 3px;
    height: 1.1em;
    background: linear-gradient(180deg, #5B4A8C, #c8a96e);
    border-radius: 2px;
    flex-shrink: 0;
}
.section-title .text {
    font-size: 0.9rem;
    font-weight: 700;
    color: #3b2a5c;
    letter-spacing: 0.12em;
}
.section-body {
    font-size: 0.92rem;
    color: #3a3430;
    white-space: pre-wrap;
    line-height: 2.2;
}

/* フッター */
.doc-footer {
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e0d9cc;
    color: #aaa;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    line-height: 2;
}

/* ダウンロードボタン */
.stDownloadButton > button {
    width: 100%;
    background: #3b2a5c;
    color: #fff;
    border: none;
    border-radius: 4px;
    padding: 0.75rem;
    font-family: 'Noto Serif JP', serif;
    letter-spacing: 0.1em;
    font-size: 0.88rem;
    cursor: pointer;
    margin-top: 1rem;
}
.stDownloadButton > button:hover {
    background: #5B4A8C;
}
</style>
""", unsafe_allow_html=True)


# ── ヘッダー ────────────────────────────────────────────
st.markdown("""
<div class="site-header">
    <div class="en">Bonno Gedatsu Kantei</div>
    <h1>🙏 煩悩解脱鑑定</h1>
    <div class="tagline">住職 × AI ｜ あなたの煩悩を才能に変える人生鑑定</div>
</div>
<hr class="header-divider">
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
        ("悩み①", worry1), ("悩み②", worry2), ("悩み③", worry3)
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

        # ── 鑑定書レンダリング ──────────────────────────
        def e(text: str) -> str:
            """AI生成テキストをHTML安全にエスケープする"""
            return html.escape(text or "")

        worries_meta = "　".join(
            f"悩み{i+1}：{e(w)}" for i, w in enumerate(result.worries)
        )

        sections_html = ""
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
        for title, body in display_sections:
            if body:
                sections_html += f"""
                <div class="section">
                    <div class="section-title">
                        <div class="ornament"></div>
                        <div class="text">【{title}】</div>
                    </div>
                    <div class="section-body">{e(body)}</div>
                </div>"""

        bonno_name = e(result.bonno_declaration) if result.bonno_declaration else "―"

        st.markdown(f"""
        <div class="document">
            <div class="doc-top">
                <div class="label">KANTEI DOCUMENT</div>
                <div class="title">煩 悩 解 脱 鑑 定 書</div>
                <div class="meta">
                    {e(result.customer_name)} 様　｜　生年月日：{e(result.birthday)}<br>
                    鑑定日：{result.generated_at[:10]}　｜　全 {result.char_count} 字
                </div>
            </div>

            <div class="bonno-box">
                <div class="label">▷ あなたの煩悩（108煩悩より）</div>
                <div class="name">{ bonno_name }</div>
                <div class="sub">この煩悩があなたの悩みの根源であり、才能の源泉です</div>
            </div>

            {sections_html}

            <div class="doc-footer">
                🙏 住職歴15年 × 鑑定実績1,200件<br>
                煩悩はあなたの潜在的な力の裏側にある
            </div>
        </div>
        """, unsafe_allow_html=True)

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

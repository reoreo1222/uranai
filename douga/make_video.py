#!/usr/bin/env python3
"""
TikTok / Instagram Reels 動画作成ツール - 改良版

改善点:
  1. カテゴリ別の宇宙・神秘系コズミック背景（プロシージャル生成）
  2. テキストに太いアウトライン＋グロー効果
  3. アクセントカラーのグラデーションテキスト
  4. キラキラ光るスパークルアニメーション
  5. ヴィネット効果
"""

import csv
import os
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
from gtts import gTTS
from moviepy import VideoClip, AudioFileClip, concatenate_videoclips

# ── 定数 ────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1080, 1920
TARGET_DURATION = 30.0
FPS = 30

FONT_BOLD  = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FONT_LIGHT = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# セクション比率
RATIO = {"hook": 0.28, "content": 0.47, "cta": 0.25}

# ── カテゴリ別カラーテーマ ────────────────────────────────────────
THEMES = {
    "love_fortune":    {"base1": (45, 5, 65),   "base2": (12, 0, 25),
                        "nebula": [(200, 30, 100), (120, 0, 180)],
                        "accent": (255, 130, 200), "glow": (255, 80, 160)},
    "money_fortune":   {"base1": (35, 22, 0),   "base2": (8, 4, 0),
                        "nebula": [(200, 150, 0), (100, 60, 0)],
                        "accent": (255, 215, 60), "glow": (255, 180, 0)},
    "work_fortune":    {"base1": (0, 20, 45),   "base2": (0, 5, 15),
                        "nebula": [(0, 100, 200), (0, 50, 120)],
                        "accent": (100, 200, 255), "glow": (50, 150, 255)},
    "zodiac_weekly":   {"base1": (5, 10, 50),   "base2": (0, 2, 20),
                        "nebula": [(30, 80, 200), (10, 30, 120)],
                        "accent": (150, 200, 255), "glow": (80, 150, 255)},
    "tarot_reading":   {"base1": (35, 5, 55),   "base2": (10, 0, 22),
                        "nebula": [(140, 0, 200), (70, 0, 120)],
                        "accent": (210, 110, 255), "glow": (170, 50, 255)},
    "bonnou_lesson":   {"base1": (45, 8, 8),    "base2": (12, 0, 0),
                        "nebula": [(180, 40, 40), (100, 10, 10)],
                        "accent": (255, 130, 90), "glow": (255, 80, 40)},
    "buddhism_wisdom": {"base1": (18, 12, 35),  "base2": (4, 2, 10),
                        "nebula": [(120, 90, 10), (60, 30, 80)],
                        "accent": (230, 190, 70), "glow": (200, 160, 20)},
    "temple_daily":    {"base1": (28, 14, 5),   "base2": (7, 3, 0),
                        "nebula": [(140, 70, 10), (70, 25, 5)],
                        "accent": (255, 170, 90), "glow": (230, 130, 30)},
    "fate_innen":      {"base1": (5, 12, 35),   "base2": (0, 3, 12),
                        "nebula": [(10, 60, 180), (40, 0, 100)],
                        "accent": (160, 210, 255), "glow": (80, 160, 255)},
    "healing_prayer":  {"base1": (22, 6, 28),   "base2": (6, 0, 12),
                        "nebula": [(160, 60, 120), (90, 10, 70)],
                        "accent": (255, 190, 230), "glow": (255, 140, 200)},
}
_DEFAULT_THEME = {
    "base1": (22, 5, 42), "base2": (5, 0, 16),
    "nebula": [(110, 25, 160), (55, 5, 90)],
    "accent": (210, 160, 255), "glow": (170, 100, 255),
}


def _get_theme(category: str) -> dict:
    return THEMES.get(category, _DEFAULT_THEME)


# ── 宇宙・神秘系背景ジェネレータ ─────────────────────────────────
def make_cosmic_bg(category: str, seed: int = 42) -> np.ndarray:
    """カテゴリ別のコズミック背景を生成（1.1倍サイズ：Ken Burns用）"""
    rng = np.random.RandomState(seed)
    theme = _get_theme(category)

    W = int(WIDTH * 1.12)
    H = int(HEIGHT * 1.12)

    arr = np.zeros((H, W, 3), dtype=np.float32)

    # ── ベースグラデーション
    base1 = np.array(theme["base1"], dtype=np.float32) / 255.0
    base2 = np.array(theme["base2"], dtype=np.float32) / 255.0
    for y in range(H):
        t = y / H
        arr[y] = base1 * (1 - t) + base2 * t

    # ── 星雲（複数の放射状グロー）
    y_coords, x_coords = np.mgrid[0:H, 0:W].astype(np.float32)
    n_clouds = rng.randint(5, 9)
    for _ in range(n_clouds):
        cx = rng.randint(0, W)
        cy = rng.randint(0, H)
        radius = rng.uniform(150, 550)
        color = np.array(theme["nebula"][rng.randint(len(theme["nebula"]))], dtype=np.float32) / 255.0
        intensity = rng.uniform(0.18, 0.45)
        dist_sq = (x_coords - cx) ** 2 + (y_coords - cy) ** 2
        glow = intensity * np.exp(-dist_sq / (2 * radius ** 2))
        arr += glow[:, :, np.newaxis] * color[np.newaxis, np.newaxis, :]

    # ── 星フィールド（サイズ・輝度のばらつき）
    for _ in range(500):
        sx = rng.randint(0, W)
        sy = rng.randint(0, H)
        brightness = rng.uniform(0.55, 1.0)
        size = rng.choice([1, 1, 1, 1, 2, 2, 3])
        y1, y2 = max(0, sy - size // 2), min(H, sy + size // 2 + 1)
        x1, x2 = max(0, sx - size // 2), min(W, sx + size // 2 + 1)
        arr[y1:y2, x1:x2] = np.maximum(arr[y1:y2, x1:x2], brightness)

    # ── ヴィネット（周辺減光）
    cy_v, cx_v = H / 2, W / 2
    dist_norm = np.sqrt(((x_coords - cx_v) / W) ** 2 + ((y_coords - cy_v) / H) ** 2)
    vignette = np.clip(1.0 - dist_norm * 1.3, 0.15, 1.0)
    arr *= vignette[:, :, np.newaxis]

    return (np.clip(arr, 0, 1) * 255).astype(np.uint8)


# ── テキスト描画ユーティリティ ────────────────────────────────────
def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_LIGHT, size)
    except Exception:
        return ImageFont.load_default()


def _wrap(text: str, font, max_w: int) -> list:
    lines = []
    for para in text.replace("。", "。\n").replace("！", "！\n").replace("？", "？\n").split("\n"):
        para = para.strip()
        if not para:
            continue
        line = ""
        for ch in para:
            if font.getbbox(line + ch)[2] > max_w and line:
                lines.append(line)
                line = ch
            else:
                line += ch
        if line:
            lines.append(line)
    return lines or [text]


def _draw_glow_text(base: Image.Image, text: str, font,
                    cx: int, cy: int,
                    text_color=(255, 255, 255),
                    glow_color=(200, 150, 255),
                    stroke_w: int = 7,
                    glow_r: int = 18) -> Image.Image:
    """グロー＋太いアウトライン付きテキストを描画"""
    # 1. グロー層
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((cx, cy), text, font=font, fill=(*glow_color, 200), anchor="mm",
            stroke_width=stroke_w + 4, stroke_fill=(*glow_color, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(glow_r))
    glow = glow.filter(ImageFilter.GaussianBlur(glow_r // 2))

    # 2. ベースにグローを合成
    result = base.convert("RGBA")
    result = Image.alpha_composite(result, glow)

    # 3. テキスト（黒アウトライン＋本文）
    rd = ImageDraw.Draw(result)
    rd.text((cx, cy), text, font=font,
            fill=(*text_color, 255), anchor="mm",
            stroke_width=stroke_w, stroke_fill=(0, 0, 0, 255))

    return result.convert("RGB")


def _draw_lines_with_glow(base: Image.Image, lines: list, font,
                           cx: int, cy: int, theme: dict,
                           accent_lines: int = 1) -> Image.Image:
    """複数行テキスト。先頭 accent_lines 行だけアクセントカラー＋大グロー"""
    lh = font.getbbox("あ")[3] + 22
    total_h = lh * len(lines)
    y = cy - total_h // 2 + lh // 2

    for i, line in enumerate(lines):
        if i < accent_lines:
            color = theme["accent"]
            glow = theme["glow"]
            gr = 22
        else:
            color = (255, 255, 255)
            glow = (180, 160, 220)
            gr = 14
        base = _draw_glow_text(base, line, font, cx, y,
                               text_color=color, glow_color=glow,
                               stroke_w=6, glow_r=gr)
        y += lh
    return base


# ── テキストオーバーレイフレーム生成 ─────────────────────────────
def make_text_overlay(main_text: str, label: str, sub_text: str,
                      category: str, font_size: int = 60) -> np.ndarray:
    """RGBA テキストオーバーレイ画像を生成"""
    theme = _get_theme(category)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))

    # ラベル（上部）
    if label:
        label_font = _font(34, bold=False)
        # 細いゴールドアクセントライン
        ld = ImageDraw.Draw(img)
        ld.line([(80, 115), (WIDTH - 80, 115)], fill=(*theme["accent"], 120), width=2)
        ld.text((WIDTH // 2, 145), label, font=label_font,
                fill=(*theme["accent"], 200), anchor="mm")
        ld.line([(80, 175), (WIDTH - 80, 175)], fill=(*theme["accent"], 120), width=2)

    # メインテキストボックス（半透明背景）
    main_font = _font(font_size)
    wrapped = _wrap(main_text, main_font, WIDTH - 120)

    lh = main_font.getbbox("あ")[3] + 22
    box_h = lh * len(wrapped) + 60
    box_y = HEIGHT // 2 - 120
    y1_box = box_y - box_h // 2 - 30
    y2_box = box_y + box_h // 2 + 30
    bd = ImageDraw.Draw(img)
    bd.rounded_rectangle([50, y1_box, WIDTH - 50, y2_box],
                         radius=28, fill=(0, 0, 0, 110))

    # テキスト描画（先頭行だけアクセントカラー）
    img_rgb = img.convert("RGB")
    img_rgb = _draw_lines_with_glow(img_rgb, wrapped, main_font,
                                     WIDTH // 2, box_y, theme, accent_lines=1)
    img = img_rgb.convert("RGBA")
    # ボックスのアルファを復元（テキスト描画で消えた分）
    overlay_box = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ovb = ImageDraw.Draw(overlay_box)
    ovb.rounded_rectangle([50, y1_box, WIDTH - 50, y2_box],
                           radius=28, fill=(0, 0, 0, 100))

    # サブテキスト（CTA）
    if sub_text:
        sub_font = _font(46)
        # アクセントカラーのボタン風背景
        sub_box_y = HEIGHT - 300
        sub_lines = _wrap(sub_text, sub_font, WIDTH - 160)
        slh = sub_font.getbbox("あ")[3] + 16
        sb_h = slh * len(sub_lines) + 40
        img_rgb2 = img.convert("RGB")
        sbd = ImageDraw.Draw(img)
        r, g, b = theme["accent"]
        sbd.rounded_rectangle([70, sub_box_y - 20, WIDTH - 70,
                                sub_box_y + sb_h],
                               radius=20, fill=(r, g, b, 220))
        sy = sub_box_y + slh // 2
        for sl in sub_lines:
            sbd.text((WIDTH // 2, sy), sl, font=sub_font,
                     fill=(20, 5, 40, 255), anchor="mm",
                     stroke_width=2, stroke_fill=(0, 0, 0, 100))
            sy += slh
        # LINE アイコン風テキスト
        line_font = _font(30, bold=False)
        sbd.text((WIDTH // 2, sub_box_y + sb_h + 28),
                 "▶ プロフィールのLINEへ", font=line_font,
                 fill=(*theme["accent"], 200), anchor="mm")

    return np.array(img)


# ── アニメーションセクションクリップ ─────────────────────────────
def make_animated_section(bg_arr: np.ndarray,
                           text_rgba: np.ndarray,
                           duration: float,
                           category: str) -> VideoClip:
    theme = _get_theme(category)
    accent = np.array(theme["accent"], dtype=np.float32)
    bh, bw = bg_arr.shape[:2]

    # スパークル位置をランダム生成（固定シード）
    rng = np.random.RandomState(abs(hash(category)) % 9999)
    n_sp = 70
    sp_x = rng.randint(40, WIDTH - 40, n_sp)
    sp_y = rng.randint(40, HEIGHT - 40, n_sp)
    sp_phase = rng.uniform(0, 2 * np.pi, n_sp)
    sp_size = rng.randint(2, 7, n_sp)
    sp_speed = rng.uniform(1.8, 3.5, n_sp)

    # テキストRGBAを事前分割
    t_rgb = text_rgba[:, :, :3].astype(np.float32)
    t_alpha = text_rgba[:, :, 3:4].astype(np.float32) / 255.0

    def make_frame(t: float) -> np.ndarray:
        progress = t / max(duration, 1e-6)

        # 1. Ken Burns ズーム
        zoom = 1.0 + 0.07 * progress
        ch = int(HEIGHT / zoom)
        cw = int(WIDTH / zoom)
        y1 = min(max((bh - ch) // 2, 0), bh - ch)
        x1 = min(max((bw - cw) // 2, 0), bw - cw)
        cropped = bg_arr[y1:y1 + ch, x1:x1 + cw]
        frame = np.array(
            Image.fromarray(cropped).resize((WIDTH, HEIGHT), Image.LANCZOS),
            dtype=np.float32
        )

        # 2. スパークルアニメーション
        for i in range(n_sp):
            bright = (np.sin(t * sp_speed[i] + sp_phase[i]) + 1) * 0.5
            if bright > 0.45:
                intensity = (bright - 0.45) / 0.55 * 0.92
                sz = sp_size[i]
                y_s = max(0, sp_y[i] - sz)
                y_e = min(HEIGHT, sp_y[i] + sz + 1)
                x_s = max(0, sp_x[i] - sz)
                x_e = min(WIDTH, sp_x[i] + sz + 1)
                frame[y_s:y_e, x_s:x_e] = np.clip(
                    frame[y_s:y_e, x_s:x_e] * (1 - intensity)
                    + accent * intensity, 0, 255
                )

        # 3. テキストフェードイン
        fade_t = min(0.5, duration * 0.18)
        alpha_mult = min(1.0, t / max(fade_t, 1e-6))
        a = t_alpha * alpha_mult
        frame = frame * (1 - a) + t_rgb * a

        return frame.clip(0, 255).astype(np.uint8)

    return VideoClip(make_frame, duration=duration).with_fps(FPS)


# ── 音声：TTS → 30 秒に圧縮 ─────────────────────────────────────
def _get_duration(path: str) -> float:
    result = subprocess.run(
        [_FFMPEG, "-i", path],
        stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    for line in result.stderr.decode("utf-8", errors="ignore").splitlines():
        if "Duration" in line:
            h, m, s = line.strip().split("Duration:")[1].split(",")[0].strip().split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return TARGET_DURATION


def make_audio_30s(text: str, out_path: str) -> None:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        raw = tmp.name
    gTTS(text=text, lang="ja", slow=False).save(raw)
    actual = _get_duration(raw)
    factor = max(0.5, min(actual / TARGET_DURATION, 2.0))
    print(f"  元の音声: {actual:.1f}秒 → {TARGET_DURATION}秒に調整（{factor:.2f}x）")
    subprocess.run([
        _FFMPEG, "-y", "-i", raw,
        "-filter:a", f"atempo={factor:.4f}", "-vn", out_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.unlink(raw)


# ── メイン ───────────────────────────────────────────────────────
def make_video(script: dict, output_path: str):
    category = script.get("category", "love_fortune")
    hook     = script["hook"]
    content  = script["content"]
    cta      = script["cta"]

    hook_dur    = TARGET_DURATION * RATIO["hook"]
    content_dur = TARGET_DURATION * RATIO["content"]
    cta_dur     = TARGET_DURATION * RATIO["cta"]

    print(f"背景を生成中... (カテゴリ: {category})")
    bg = make_cosmic_bg(category)

    print("音声を生成中...")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        audio_path = tmp.name
    make_audio_30s(f"{hook}。{content}。{cta}", audio_path)

    print("テキストオーバーレイを生成中...")
    ov_hook    = make_text_overlay(hook,    "◆ HOOK",  "",                      category, 64)
    ov_content = make_text_overlay(content, "◆ 本編",  "",                      category, 52)
    ov_cta     = make_text_overlay(cta,     "◆ 行動",  "今すぐLINEへ",          category, 54)

    print("動画クリップを生成中（スパークル＋Ken Burns）...")
    s1 = make_animated_section(bg, ov_hook,    hook_dur,    category)
    s2 = make_animated_section(bg, ov_content, content_dur, category)
    s3 = make_animated_section(bg, ov_cta,     cta_dur,     category)

    print("合成・エンコード中...")
    video = concatenate_videoclips([s1, s2, s3], method="compose")
    audio = AudioFileClip(audio_path)
    video = video.with_audio(audio)
    video.write_videofile(
        output_path, fps=FPS,
        codec="libx264", audio_codec="aac", logger=None
    )
    video.close()
    audio.close()
    os.unlink(audio_path)
    print(f"\n完成 → {output_path}")


def load_latest_script() -> dict:
    csvs = sorted(Path("./output").glob("scripts_*.csv"), reverse=True)
    if not csvs:
        print("エラー: output/ にCSVがありません。先に generate.py を実行してください。")
        sys.exit(1)
    print(f"台本: {csvs[0].name}")
    with open(csvs[0], encoding="utf-8-sig") as f:
        return next(csv.DictReader(f))


if __name__ == "__main__":
    script = load_latest_script()
    today  = date.today().strftime("%m%d")
    title  = script["title"].replace("/", "_").replace(" ", "_")
    out    = f"output/{today}_{title}.mp4"

    print(f"【{script['category_label']}】{script['title']}")
    print(f"文字数: {script['char_count']}字\n")
    make_video(script, out)

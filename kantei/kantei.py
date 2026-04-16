#!/usr/bin/env python3
"""
煩悩解脱鑑定ツール
顧客の情報から約4,000字の個別鑑定文をAIで生成します。
"""

import sys
from datetime import datetime
from pathlib import Path

import click

from config import OUTPUT
from generator import generate_kantei, format_for_display


@click.command()
@click.option("--name",     prompt="お名前　　（例: 山田 太郎）", help="相談者のお名前")
@click.option("--birthday", prompt="生年月日　（例: 1990-03-15）", help="相談者の生年月日")
@click.option("--worry1",   prompt="悩み①　　", help="1つ目の悩み")
@click.option("--worry2",   prompt="悩み②　　", help="2つ目の悩み")
@click.option("--worry3",   prompt="悩み③　　", help="3つ目の悩み")
@click.option("--model",    default=None, help="使用するモデル（省略時: config設定）")
@click.option("--save",     is_flag=True, default=False, help="outputフォルダにテキストファイルで保存する")
def main(name, birthday, worry1, worry2, worry3, model, save):
    """
    \b
    煩悩解脱鑑定ツール — 住職×AI 個別鑑定文生成（約4,000字）

    使用例:
      python kantei.py
      python kantei.py --name "山田 太郎" --birthday 1990-03-15 \\
          --worry1 "仕事がうまくいかない" \\
          --worry2 "お金の不安がある" \\
          --worry3 "人間関係で疲弊している"
      python kantei.py --save
    """
    click.echo("\n🙏 煩悩解脱鑑定を開始します\n")
    click.echo(f"  お名前　: {name}")
    click.echo(f"  生年月日: {birthday}")
    click.echo(f"  悩み①　: {worry1}")
    click.echo(f"  悩み②　: {worry2}")
    click.echo(f"  悩み③　: {worry3}")
    click.echo("\n  AIが鑑定文を生成中です（約30〜60秒）...\n")

    try:
        result = generate_kantei(
            name=name,
            birthday=birthday,
            worry1=worry1,
            worry2=worry2,
            worry3=worry3,
            model=model,
        )
    except RuntimeError as e:
        click.echo(f"\n❌ エラー: {e}", err=True)
        sys.exit(1)

    output_text = format_for_display(result)
    click.echo(output_text)

    if save:
        output_dir = Path(OUTPUT["dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = name.replace(" ", "_").replace("\u3000", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_dir / f"{safe_name}_{timestamp}.txt"
        filepath.write_text(output_text, encoding="utf-8")
        click.echo(f"💾 保存しました: {filepath}")

    click.echo(f"\n✅ 生成完了 — {result.char_count}字\n")


if __name__ == "__main__":
    main()

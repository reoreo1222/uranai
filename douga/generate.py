#!/usr/bin/env python3
"""
TikTok動画台本量産ツール
占い・スピリチュアル系コンテンツの台本をClaude APIで自動生成します。
"""

import sys
import click

from config import GENERATION
from templates import list_templates, get_template, TEMPLATES
from batch import generate_batch
from generator import generate_script, format_script_for_display


ALL_CATEGORY_KEYS = [t.key for t in TEMPLATES]


@click.command()
@click.option(
    "--category",
    default="love_fortune",
    show_default=True,
    help=f"生成するカテゴリ。'all' で全カテゴリ。\n選択肢: {', '.join(ALL_CATEGORY_KEYS)}, all",
)
@click.option(
    "--count",
    default=5,
    show_default=True,
    type=int,
    help="カテゴリごとの生成本数",
)
@click.option(
    "--format",
    "output_format",
    default="both",
    show_default=True,
    type=click.Choice(["csv", "json", "both"]),
    help="出力ファイル形式",
)
@click.option(
    "--model",
    default=None,
    help=f"使用するClaudeモデル（省略時: {GENERATION['model']}）\n例: claude-sonnet-4-6（高速・低コスト）",
)
@click.option(
    "--list-categories",
    is_flag=True,
    default=False,
    help="利用可能なカテゴリ一覧を表示して終了",
)
def main(category: str, count: int, output_format: str, model, list_categories: bool):
    """
    \b
    TikTok動画台本量産ツール - 占い・スピリチュアル系

    使用例:
      python generate.py --list-categories
      python generate.py --category love_fortune --count 10
      python generate.py --category all --count 3
      python generate.py --category money_fortune --count 5 --format csv
      python generate.py --category work_fortune --count 3 --model claude-sonnet-4-6
    """
    if list_categories:
        _print_categories()
        return

    if count < 1:
        click.echo("エラー: --count は 1 以上を指定してください。", err=True)
        sys.exit(1)

    if category == "all":
        templates = list_templates()
        click.echo(f"\n全{len(templates)}カテゴリ × {count}本 = 合計{len(templates) * count}本を生成します\n")
    else:
        try:
            templates = [get_template(category)]
        except ValueError as e:
            click.echo(f"エラー: {e}", err=True)
            click.echo("\n利用可能なカテゴリ:")
            _print_categories()
            sys.exit(1)
        click.echo(f"\n[{templates[0].label}] {count}本を生成します\n")

    used_model = model or GENERATION["model"]
    click.echo(f"モデル: {used_model} | 出力形式: {output_format}\n")

    generate_batch(
        templates=templates,
        count_per_category=count,
        output_format=output_format,
        model=used_model,
        verbose=True,
    )


def _print_categories():
    click.echo("\n利用可能なカテゴリ一覧:")
    click.echo("-" * 55)
    click.echo(f"{'キー':<20} {'ラベル':<15} 説明")
    click.echo("-" * 55)
    for t in list_templates():
        click.echo(f"{t.key:<20} {t.label:<15} {t.description}")
    click.echo("-" * 55)
    click.echo("\n使用例: python generate.py --category love_fortune --count 5")


if __name__ == "__main__":
    main()

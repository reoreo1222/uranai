import csv
import json
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from config import OUTPUT
from generator import TikTokScript, generate_script, format_script_for_display
from templates import ContentTemplate


def _ensure_output_dir() -> Path:
    out = Path(OUTPUT["dir"])
    out.mkdir(parents=True, exist_ok=True)
    return out


def _make_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _save_csv(scripts: List[TikTokScript], path: Path) -> None:
    if not scripts:
        return
    fieldnames = list(asdict(scripts[0]).keys())
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in scripts:
            writer.writerow(asdict(s))


def _save_json(scripts: List[TikTokScript], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(s) for s in scripts], f, ensure_ascii=False, indent=2)


def generate_batch(
    templates: List[ContentTemplate],
    count_per_category: int,
    output_format: str = "both",
    model: Optional[str] = None,
    verbose: bool = True,
) -> List[TikTokScript]:
    """
    複数カテゴリ × count_per_category 本の台本を生成し、CSV/JSON に保存する。

    output_format: "csv" | "json" | "both"
    """
    out_dir = _ensure_output_dir()
    timestamp = _make_timestamp()
    interval = OUTPUT["partial_save_interval"]

    all_scripts: List[TikTokScript] = []
    total = len(templates) * count_per_category
    generated = 0

    csv_path = out_dir / f"scripts_{timestamp}.csv"
    json_path = out_dir / f"scripts_{timestamp}.json"

    for template in templates:
        if verbose:
            print(f"\n[{template.label}] {count_per_category}本を生成します...")

        for i in range(1, count_per_category + 1):
            global_index = len(all_scripts) + 1
            if verbose:
                print(f"  ({global_index}/{total}) {template.label} #{i} 生成中...", end=" ", flush=True)

            try:
                script = generate_script(
                    template=template,
                    index=global_index,
                    model=model,
                )
                all_scripts.append(script)
                generated += 1

                if verbose:
                    print(f"完了 ({script.char_count}字 / {script.duration_estimate})")
                    print(format_script_for_display(script))

                # 部分保存（クラッシュ対策）
                if generated % interval == 0:
                    _partial_save(all_scripts, output_format, csv_path, json_path, verbose)

            except Exception as e:
                if verbose:
                    print(f"エラー: {e}")

            # レート制限対策
            if not (template == templates[-1] and i == count_per_category):
                time.sleep(0.5)

    # 最終保存
    _final_save(all_scripts, output_format, csv_path, json_path, verbose, timestamp)

    return all_scripts


def _partial_save(
    scripts: List[TikTokScript],
    output_format: str,
    csv_path: Path,
    json_path: Path,
    verbose: bool,
) -> None:
    if output_format in ("csv", "both"):
        _save_csv(scripts, csv_path)
    if output_format in ("json", "both"):
        _save_json(scripts, json_path)
    if verbose:
        print(f"  [中間保存] {len(scripts)}本保存済み")


def _final_save(
    scripts: List[TikTokScript],
    output_format: str,
    csv_path: Path,
    json_path: Path,
    verbose: bool,
    timestamp: str,
) -> None:
    saved_paths = []
    if output_format in ("csv", "both"):
        _save_csv(scripts, csv_path)
        saved_paths.append(str(csv_path))
    if output_format in ("json", "both"):
        _save_json(scripts, json_path)
        saved_paths.append(str(json_path))

    if verbose and scripts:
        print("\n" + "=" * 60)
        print(f"生成完了: {len(scripts)}本の台本を生成しました")
        for p in saved_paths:
            print(f"  保存先: {p}")
        print("=" * 60)

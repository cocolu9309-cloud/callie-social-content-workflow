#!/usr/bin/env python3
"""
Callie Social Content Workflow — 一键运行脚本
用法: python run_all.py <content_json> [output_xlsx]

功能:
  将 Step C 输出的 content JSON 通过以下步骤串联:
  1. 动态生成关键帧 prompts（从 script_rows）
  2. 调用 SiliconFlow Qwen-Image 生成 6 张 9:16 参考图
  3. 打包为格式化 Excel

示例:
  python scripts/run_all.py content.json Callie_Content_Pack.xlsx
  python scripts/run_all.py content.json --keyframes keyframes/ --count 6
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path

# Add scripts dir to path so we can import the modules
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import generate_keyframes
import build_excel

DEFAULT_KEYFRAMES_DIR = "keyframes"
DEFAULT_OUTPUT = "Callie_Content_Pack.xlsx"


def run_all(content_json: str, output_xlsx: str = DEFAULT_OUTPUT,
            keyframes_dir: str = DEFAULT_KEYFRAMES_DIR,
            config_path: str = "config.yaml",
            count: int = 6):
    """
    Run the full Step C → Step D pipeline.

    Args:
        content_json: Path to content JSON file (from Step C output)
        output_xlsx: Output Excel file path
        keyframes_dir: Directory for generated keyframe images
        config_path: Config file path
        count: Number of keyframes to generate
    """
    # ── 1. Validate inputs ──────────────────────────────────────────
    if not os.path.exists(content_json):
        print(f"[Error] Content JSON not found: {content_json}")
        return 1

    with open(content_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    script_rows = data.get("script_rows", [])
    if not script_rows:
        print("[Error] No script_rows found in content JSON. "
              "Please ensure content.json contains the script_rows field.")
        return 1

    product_name = data.get("product_name", "Unknown Product")
    platform = data.get("platform", "Instagram")
    print(f"[run_all] Starting pipeline for: {product_name} ({platform})")
    print(f"[run_all] Content JSON: {content_json}")
    print(f"[run_all] Output Excel: {output_xlsx}")
    print("=" * 60)

    # ── 2. Build dynamic keyframe prompts from script_rows ──────────
    keyframe_prompts = []
    for row in script_rows:
        prompt = generate_keyframes.build_prompt_from_script_row(row)
        keyframe_prompts.append(prompt)

    print(f"[run_all] Built {len(keyframe_prompts)} dynamic prompts from script_rows")
    for kf in keyframe_prompts:
        print(f"  {kf['frame']}: {kf['prompt_en'][:90]}...")
    print()

    # ── 3. Load API key ─────────────────────────────────────────────
    import yaml
    api_key = None
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        api_key = config.get("siliconflow_api_key", os.environ.get("SILICONFLOW_API_KEY", ""))

    if not api_key or api_key == "YOUR_API_KEY_HERE":
        api_key = os.environ.get("SILICONFLOW_API_KEY", "")
        if not api_key:
            print("[Error] SiliconFlow API key not configured.")
            print("  Set siliconflow_api_key in config.yaml")
            print("  Or: export SILICONFLOW_API_KEY=your_key")
            return 1

    # ── 4. Generate keyframe images ────────────────────────────────
    print(f"[run_all] Generating {count} keyframe images via SiliconFlow...")
    try:
        results = generate_keyframes.generate_keyframe_images(
            output_dir=keyframes_dir,
            api_key=api_key,
            image_size=generate_keyframes.DEFAULT_IMAGE_SIZE,
            count=count,
            keyframe_prompts=keyframe_prompts
        )
        print(f"[run_all] Generated {len(results)} images")
    except Exception as e:
        print(f"[Error] Keyframe generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # ── 5. Build Excel ─────────────────────────────────────────────
    print(f"\n[run_all] Building Excel: {output_xlsx}")
    try:
        build_excel.build_excel(content_json, output_xlsx, keyframes_dir)
        print(f"[Done] Excel content pack created: {os.path.abspath(output_xlsx)}")
    except Exception as e:
        print(f"[Error] Excel build failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("=" * 60)
    print(f"[run_all] Pipeline complete!")
    print(f"  Images : {os.path.abspath(keyframes_dir)}/")
    print(f"  Excel   : {os.path.abspath(output_xlsx)}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Run full Step C→D pipeline: generate keyframes + build Excel from content JSON"
    )
    parser.add_argument("content_json", help="Path to content JSON file (from Step C output)")
    parser.add_argument("output_xlsx", nargs="?", default=DEFAULT_OUTPUT,
                        help=f"Output Excel file (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--keyframes", "-k", default=DEFAULT_KEYFRAMES_DIR,
                        help=f"Keyframe images directory (default: {DEFAULT_KEYFRAMES_DIR})")
    parser.add_argument("--config", "-c", default="config.yaml",
                        help="Config file path (default: config.yaml)")
    parser.add_argument("--count", "-n", type=int, default=6,
                        help="Number of keyframes to generate (default: 6)")

    args = parser.parse_args()

    return run_all(
        content_json=args.content_json,
        output_xlsx=args.output_xlsx,
        keyframes_dir=args.keyframes,
        config_path=args.config,
        count=args.count
    )


if __name__ == "__main__":
    sys.exit(main())
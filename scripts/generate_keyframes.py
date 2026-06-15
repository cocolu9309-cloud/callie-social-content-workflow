#!/usr/bin/env python3
"""
Callie Social Content Workflow — 关键帧AI生图工具
用法: python generate_keyframes.py <输出目录> --config <config.yaml>

功能:
- 读取视频帧图片，使用AI分析画面内容
- 生成6个关键帧的中文分镜描述
- 调用 SiliconFlow Qwen-Image API 生成9:16参考图
"""

import httpx
import os
import sys
import json
import argparse
import yaml
import time
from pathlib import Path

DEFAULT_CONFIG = "config.yaml"
DEFAULT_KEYFRAME_COUNT = 6
DEFAULT_IMAGE_SIZE = "1024x1792"  # 9:16 竖版


# 6帧关键帧的英文Prompt模板（用于AI生图）
KEYFRAME_PROMPTS = [
    {
        "frame": "Frame 1 (0-1s)",
        "scene": "Close-up of personalized wooden photo box on desk, surrounded by dried flowers, soft warm bokeh",
        "camera": "Fixed close-up",
        "overlay": "She said it was ugly",
        "mood": "Suspenseful, slight grievance",
        "prompt_en": (
            "Cinematic close-up of a personalized wooden photo box on a desk, "
            "surrounded by dried flowers and rose petals, soft bokeh background in warm tones. "
            "The wooden box has elegant laser-engraved text on the lid. "
            "Natural light wood texture, cozy and elegant atmosphere. "
            "Vertical 9:16 aspect ratio, soft natural lighting, shallow depth of field."
        )
    },
    {
        "frame": "Frame 2 (1-3s)",
        "scene": "Hand entering frame, fingertips touching box lid, about to open",
        "camera": "Slow push-in",
        "overlay": "(no text, suspense music)",
        "mood": "Anticipating, tense",
        "prompt_en": (
            "Cinematic shot of a hand entering from the right side of the frame, "
            "fingertips gently touching the lid edge of a wooden gift box, "
            "about to open it. Warm soft top lighting illuminates the wood grain beautifully. "
            "Anticipation and tension mood. "
            "Minimalist composition, vertical 9:16 aspect ratio, warm tones."
        )
    },
    {
        "frame": "Frame 3 (3-6s)",
        "scene": "Box lid opening, accordion photo strip unfurling, first couple photo revealed",
        "camera": "Pull out with unfolding",
        "overlay": "Our whole story, unfolding...",
        "mood": "Surprised, emotional",
        "prompt_en": (
            "Cinematic reveal shot: wooden box lid opening, "
            "an accordion-fold photo strip gradually unfurling with the first photo showing a happy couple. "
            "Soft dramatic lighting from above, wood texture in sharp focus. "
            "Emotional surprise moment, warm and nostalgic atmosphere. "
            "Vertical 9:16 aspect ratio, movie-like composition."
        )
    },
    {
        "frame": "Frame 4 (6-9s)",
        "scene": "Multiple photos flipping through accordion album - couple, travel, everyday moments",
        "camera": "Fixed medium shot",
        "overlay": "Every photo, every memory",
        "mood": "Warm, nostalgic",
        "prompt_en": (
            "Dynamic close-up sequence showing multiple photos flipping through "
            "an accordion photo album inside a wooden box - couple photos, travel photos, everyday moments. "
            "Cinematic transition effect between sequential photos. "
            "Warm nostalgic mood, soft golden lighting. "
            "Collage-style composition within the wooden box frame. "
            "Vertical 9:16 aspect ratio."
        )
    },
    {
        "frame": "Frame 5 (9-12s)",
        "scene": "Both hands lifting open box with unfurled photo accordion, blurred roses in background",
        "camera": "Slow tilt-up",
        "overlay": "A gift that remembers the detail",
        "mood": "Warm, cherished",
        "prompt_en": (
            "Emotional hero shot: both hands gently lifting an open wooden photo box "
            "displaying the unfurled photo accordion strip. "
            "Soft-focus pink roses and dried flowers in the blurred background. "
            "Warm golden hour lighting, intimate and precious atmosphere. "
            "Product is the clear focal point, showcasing premium handcrafted quality. "
            "Vertical 9:16 aspect ratio."
        )
    },
    {
        "frame": "Frame 6 (12-15s)",
        "scene": "Close-up of lid with laser engraving 'Name & Date', CTA text",
        "camera": "Close-up push",
        "overlay": "Create yours - link in bio",
        "mood": "Elegant, decisive",
        "prompt_en": (
            "Extreme close-up detail shot of a wooden gift box lid showing precise laser engraving. "
            "Elegant typography with subtle embossed tactile effect. "
            "Soft spotlight on the engraving, minimalist dark background. "
            "Premium craftsmanship detail, luxury product photography style. "
            "Vertical 9:16 aspect ratio."
        )
    }
]


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_keyframe_images(output_dir: str, api_key: str, image_size: str = DEFAULT_IMAGE_SIZE,
                              count: int = DEFAULT_KEYFRAME_COUNT) -> dict:
    """
    调用 SiliconFlow API 生成关键帧参考图

    Args:
        output_dir: 输出目录
        api_key: SiliconFlow API Key
        image_size: 图像尺寸，默认 1024x1792（9:16）
        count: 生成帧数量，默认6

    Returns:
        dict: {frame_name: filepath} 映射
    """
    api_url = "https://api.siliconflow.cn/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    os.makedirs(output_dir, exist_ok=True)
    results = {}

    print(f"[generate_keyframes] Generating {count} keyframe images (size: {image_size})...")
    print(f"[generate_keyframes] Output: {os.path.abspath(output_dir)}")
    print("=" * 60)

    for i, kf in enumerate(KEYFRAME_PROMPTS[:count], 1):
        payload = {
            "model": "Qwen/Qwen-Image",
            "prompt": kf["prompt_en"],
            "image_size": image_size,
            "n": 1
        }

        print(f"\n[{i}/{count}] Generating {kf['frame']}...")

        try:
            response = httpx.post(api_url, headers=headers, json=payload, timeout=180.0)
            response.raise_for_status()
            data = response.json()

            if "images" not in data or not data["images"]:
                print(f"  [WARN] No image in response")
                continue

            img_obj = data["images"][0]
            image_data = None

            if "url" in img_obj and img_obj["url"]:
                img_response = httpx.get(img_obj["url"], timeout=60.0)
                img_response.raise_for_status()
                image_data = img_response.content
            elif "b64_json" in img_obj and img_obj["b64_json"]:
                import base64
                image_data = base64.b64decode(img_obj["b64_json"])

            if image_data:
                filename = f"keyframe_{i:02d}.jpg"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(image_data)
                results[kf["frame"]] = filepath
                print(f"  [OK] Saved: {filename}")

        except httpx.HTTPStatusError as e:
            print(f"  [ERROR] HTTP {e.response.status_code}: {e.response.text[:200]}")
        except Exception as e:
            print(f"  [ERROR] {e}")

        if i < count:
            time.sleep(2)

    return results


def generate_storyboard_json(output_dir: str, keyframe_data: list = None) -> str:
    """
    生成关键帧分镜 JSON 文件（供 Excel 脚本使用）

    Returns:
        str: JSON 文件路径
    """
    if keyframe_data is None:
        keyframe_data = KEYFRAME_PROMPTS

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "keyframe_storyboard.json")

    data = []
    for i, kf in enumerate(keyframe_data, 1):
        data.append({
            "frame": i,
            "time": kf["frame"].split("(")[1].rstrip(")"),
            "scene": kf["scene"],
            "camera": kf["camera"],
            "overlay": kf["overlay"],
            "mood": kf["mood"],
            "filename": f"keyframe_{i:02d}.jpg"
        })

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[generate_storyboard_json] Saved: {json_path}")
    return json_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI keyframe reference images using SiliconFlow Qwen-Image API"
    )
    parser.add_argument("output", nargs="?", default="keyframes",
                        help="Output directory for generated images (default: keyframes)")
    parser.add_argument("--config", "-c", default=DEFAULT_CONFIG,
                        help="Config file path (default: config.yaml)")
    parser.add_argument("--count", "-n", type=int, default=DEFAULT_KEYFRAME_COUNT,
                        help=f"Number of keyframes to generate (default: {DEFAULT_KEYFRAME_COUNT})")
    parser.add_argument("--size", "-s", default=DEFAULT_IMAGE_SIZE,
                        help=f"Image size in WxH (default: {DEFAULT_IMAGE_SIZE})")

    args = parser.parse_args()

    # 加载配置
    config = {}
    if os.path.exists(args.config):
        config = load_config(args.config)
    else:
        print(f"[WARN] Config file not found: {args.config}, using defaults")

    api_key = config.get("siliconflow_api_key", os.environ.get("SILICONFLOW_API_KEY", ""))
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("[Error] SiliconFlow API key not configured.")
        print("  Option 1: Set siliconflow_api_key in config.yaml")
        print("  Option 2: Export environment variable: export SILICONFLOW_API_KEY=your_key")
        return 1

    try:
        # 生成关键帧图片
        results = generate_keyframe_images(args.output, api_key, args.size, args.count)

        # 生成分镜 JSON
        json_path = generate_storyboard_json(args.output)

        print("\n" + "=" * 60)
        print(f"[Done] Generated {len(results)} images")
        for frame, path in results.items():
            print(f"  {frame}: {os.path.basename(path)}")
        print(f"\nStoryboard JSON: {json_path}")

        return 0

    except Exception as e:
        print(f"[Error] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
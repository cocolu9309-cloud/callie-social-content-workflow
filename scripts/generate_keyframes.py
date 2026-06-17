#!/usr/bin/env python3
"""
Callie Social Content Workflow — 关键帧AI生图工具
用法:
  # 方式1: 传入AI生成的script_rows，动态生成prompts
  python scripts/generate_keyframes.py keyframes/ --script-rows "[ [\"0-1s\", \"特写木盒\", \"固定镜头\", \"She said it was ugly\", \"悬念\", \"帧1\", \"keyframe_01.jpg\"], ... ]"

  # 方式2: 使用内置硬编码prompts（默认示例产品）
  python scripts/generate_keyframes.py keyframes/ -n 6 --config config.yaml

功能:
- 方式1: 读取AI生成的视频脚本分镜，动态生成英文Prompt，再调用SiliconFlow Qwen-Image API
- 方式2: 使用内置硬编码prompts生成9:16参考图
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

# Camera movement to English visual direction
CAMERA_MAP = {
    "固定镜头": "fixed camera, static shot",
    "固定": "fixed camera, static shot",
    "缓慢推进镜头": "slow push-in, cinematic approach",
    "推进镜头": "push-in, cinematic approach",
    "推进": "push-in, cinematic approach",
    "拉远": "pull-out, revealing wider scene",
    "缓慢拉远": "slow pull-out, cinematic reveal",
    "上摇镜头": "tilt-up camera movement",
    "下摇": "tilt-down camera movement",
    "摇镜": "pan camera movement",
    "横移": "tracking shot, side movement",
    "特写推进": "close-up push, detail emphasis",
    "特写": "close-up shot, detail focus",
    "中景": "medium shot, contextual framing",
    "全景": "wide shot, full scene",
}

# Mood to visual quality adjectives
MOOD_MAP = {
    "悬念": "suspenseful, mysterious atmosphere",
    "期待": "anticipating, hopeful mood",
    "紧张": "tense, dramatic tension",
    "惊喜": "surprised, delightful moment",
    "感动": "emotional, touching scene",
    "温馨": "warm, cozy ambiance",
    "怀旧": "nostalgic, golden-toned warmth",
    "温暖": "warm, heartfelt feeling",
    "珍视": "cherished, precious moment",
    "优雅": "elegant, refined aesthetic",
    "确定": "confident, decisive mood",
    "愉悦": "joyful, light and bright",
    "浪漫": "romantic, soft and intimate",
}


def translate_camera(cn: str) -> str:
    """Translate Chinese camera direction to English"""
    for key, val in CAMERA_MAP.items():
        if key in cn:
            return val
    return "cinematic shot"


def translate_mood(cn: str) -> str:
    """Translate Chinese mood to English visual adjectives"""
    for key, val in MOOD_MAP.items():
        if key in cn:
            return val
    return "cinematic, emotionally resonant"


def build_prompt_from_script_row(row: list) -> dict:
    """
    Build a keyframe prompt dict from a script_rows entry.

    Expected row format (7-8 elements):
      [time, scene_cn, camera_cn, overlay_en, mood_cn, notes, frame_label, img_filename]

    Returns a prompt dict with frame, scene, camera, overlay, mood, prompt_en.
    """
    timecode = row[0] if len(row) > 0 else "0s"
    scene_cn = row[1] if len(row) > 1 else ""
    camera_cn = row[2] if len(row) > 2 else ""
    overlay_en = row[3] if len(row) > 3 else ""
    mood_cn = row[4] if len(row) > 4 else ""

    scene_en = translate_scene(scene_cn)
    camera_en = translate_camera(camera_cn)
    mood_en = translate_mood(mood_cn)

    prompt_parts = [scene_en]
    if overlay_en and overlay_en not in ("(无文字，悬念音乐)", "(none)", ""):
        prompt_parts.append(f"Text overlay: '{overlay_en}'")
    prompt_parts.append(camera_en)
    prompt_parts.append(mood_en)
    prompt_parts.append("vertical 9:16 aspect ratio, soft natural lighting")

    return {
        "frame": f"Frame ( {timecode} )",
        "scene": scene_cn,
        "camera": camera_cn,
        "overlay": overlay_en,
        "mood": mood_cn,
        "prompt_en": f"Cinematic photo: {', '.join(prompt_parts)}. High quality, professional photography style."
    }


def translate_scene(cn: str) -> str:
    """
    Translate Chinese scene description to English visual description.
    Handles common patterns found in script_rows.
    """
    # Handle common patterns
    replacements = [
        # Objects
        (r"木盒", "wooden gift box"),
        (r"风琴式.*?相册", "accordion-fold photo album"),
        (r"风琴式.*?拉页", "accordion-fold photo strip"),
        (r"情侣照片?|合影", "couple photo"),
        (r"照片翻页", "photo flipping"),
        (r"玫瑰|干花", "roses and dried flowers"),
        (r"背景柔焦?虚化", "soft bokeh background"),
        (r"柔光", "soft diffused lighting"),
        (r"暖金色光线", "warm golden hour lighting"),
        (r"柔焦", "shallow depth of field, soft focus"),
        (r"深色背景", "dark minimalist background"),
        (r"极简", "minimalist composition"),
        # Actions
        (r"手.*?入镜", "hand entering frame"),
        (r"手指轻触", "fingertips gently touching"),
        (r"打开盒盖|盒盖打开", "box lid opening"),
        (r"风琴页展开", "accordion pages gradually unfurling"),
        (r"微微抬起", "gently lifting"),
        (r"特写展示", "close-up detail shot of"),
        (r"镜头随.*?拉远", "camera pulling back as"),
        (r"缓慢推进", "slow cinematic push-in"),
        (r"缓慢上摇", "slow tilt-up camera movement"),
        (r"特写推进", "close-up push toward"),
        # Text overlays
        (r"文字Overlay.*?[:：]?\s*", ""),
    ]

    result = cn
    for pattern, replacement in replacements:
        import re
        result = re.sub(pattern, replacement, result)

    # Clean up and truncate if too long
    result = result.strip("，,。. ")
    if len(result) > 200:
        result = result[:200] + "..."
    return result


# 6帧关键帧的英文Prompt模板（用于AI生图）— 默认示例产品（个性化木盒相册）
DEFAULT_KEYFRAME_PROMPTS = [
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
                              count: int = DEFAULT_KEYFRAME_COUNT,
                              keyframe_prompts: list = None,
                              delay: float = 2.0) -> dict:
    """
    调用 SiliconFlow API 生成关键帧参考图

    Args:
        output_dir: 输出目录
        api_key: SiliconFlow API Key
        image_size: 图像尺寸，默认 1024x1792（9:16）
        count: 生成帧数量，默认6
        keyframe_prompts: 关键帧prompt列表，默认使用内置硬编码prompts

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

    prompts = keyframe_prompts if keyframe_prompts else DEFAULT_KEYFRAME_PROMPTS
    for i, kf in enumerate(prompts[:count], 1):
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
            time.sleep(delay)

    return results


def generate_storyboard_json(output_dir: str, keyframe_data: list = None) -> str:
    """
    生成关键帧分镜 JSON 文件（供 Excel 脚本使用）

    Returns:
        str: JSON 文件路径
    """
    if keyframe_data is None:
        keyframe_data = DEFAULT_KEYFRAME_PROMPTS

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "keyframe_storyboard.json")

    data = []
    for i, kf in enumerate(keyframe_data, 1):
        # Handle both formats: "Frame 1 (0-1s)" and "Frame ( 0-1s )"
        frame_str = kf.get("frame", f"Frame {i}")
        try:
            time_str = frame_str.split("(")[1].rstrip(")").strip()
        except IndexError:
            time_str = kf.get("time", f"{i}s")

        data.append({
            "frame": i,
            "time": time_str,
            "scene": kf.get("scene", ""),
            "camera": kf.get("camera", ""),
            "overlay": kf.get("overlay", ""),
            "mood": kf.get("mood", ""),
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
    parser.add_argument("--script-rows", "-r", default=None,
                        help="JSON string or @file path: AI-generated script_rows from Step C. "
                             "When provided, prompts are generated dynamically from script descriptions instead of using hardcoded defaults. "
                             "Example: --script-rows '[ [\"0-1s\",\"特写木盒\",\"固定镜头\",\"She said it was ugly\",\"悬念\",\"帧1\",\"keyframe_01.jpg\"], ... ]' "
                             "or: --script-rows @content.json (will read script_rows from the JSON file)")
    parser.add_argument("--delay", "-d", type=float, default=2.0,
                        help="Seconds to wait between API calls (default: 2.0)")

    args = parser.parse_args()

    # 加载配置
    config = {}
    if os.path.exists(args.config):
        config = load_config(args.config)
    else:
        print(f"[WARN] Config file not found: {args.config}, using defaults")

    # 解析 script_rows（动态prompts模式）— 不需要 API Key，先解析
    keyframe_prompts = None
    if args.script_rows:
        raw = args.script_rows.strip()
        # 支持 @filename 形式：读取文件
        if raw.startswith("@"):
            json_path = raw[1:].strip()
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    content_data = json.load(f)
                    script_rows = content_data.get("script_rows", [])
            else:
                print(f"[WARN] Script rows file not found: {json_path}")
                script_rows = []
        else:
            # 直接是 JSON 字符串
            try:
                script_rows = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"[Error] Invalid JSON in --script-rows: {e}")
                return 1

        if script_rows:
            keyframe_prompts = [build_prompt_from_script_row(row) for row in script_rows]
            print(f"[generate_keyframes] Built {len(keyframe_prompts)} dynamic prompts from script_rows:")
            for kf in keyframe_prompts:
                print(f"  {kf['frame']}: {kf['prompt_en'][:100]}...")
            print()  # 空行分隔

    # 检查 API Key（仅在需要调用 API 时）
    api_key = config.get("siliconflow_api_key", os.environ.get("SILICONFLOW_API_KEY", ""))
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("[Error] SiliconFlow API key not configured.")
        print("  Option 1: Set siliconflow_api_key in config.yaml")
        print("  Option 2: Export environment variable: export SILICONFLOW_API_KEY=your_key")
        if keyframe_prompts:
            print(f"\n[Info] Dynamic prompts were built ({len(keyframe_prompts)} frames) — configure API key to generate images.")
        return 1

    try:
        # 生成分镜 JSON（无论是否调用 API 都需要）
        json_data = keyframe_prompts if keyframe_prompts else DEFAULT_KEYFRAME_PROMPTS
        json_path = generate_storyboard_json(args.output, json_data)

        # 调用 API 生成关键帧图片
        image_results = generate_keyframe_images(
            output_dir=args.output,
            api_key=api_key,
            image_size=args.size,
            count=args.count,
            keyframe_prompts=keyframe_prompts,
            delay=args.delay
        )

        print("\n" + "=" * 60)
        print(f"[Done] Generated {len(image_results)} images")
        for frame, path in image_results.items():
            print(f"  {frame}: {os.path.basename(path)}")
        print(f"\nStoryboard JSON: {json_path}")

        return 0

    except Exception as e:
        print(f"[Error] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
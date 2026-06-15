#!/usr/bin/env python3
"""
Callie Social Content Workflow — 视频帧提取工具
用法: python extract_frames.py <视频文件路径> [输出目录]

功能:
- 从视频中按指定时间点提取关键帧
- 输出为 JPG 图片文件
- 自动创建输出目录
"""

import cv2
import os
import sys
import argparse
from pathlib import Path

DEFAULT_TIMESTAMPS = [0, 3, 8, 15, 22, 30]
DEFAULT_OUTPUT = "frames"


def extract_frames(video_path: str, output_dir: str = DEFAULT_OUTPUT, timestamps: list = None) -> dict:
    """
    从视频中提取指定时间点的帧

    Args:
        video_path: 视频文件路径（支持 mp4/mov/avi）
        output_dir: 输出目录路径
        timestamps: 要提取的时间点列表（秒），默认 [0, 3, 8, 15, 22, 30]

    Returns:
        dict: {timestamp: output_filepath} 映射
    """
    if timestamps is None:
        timestamps = DEFAULT_TIMESTAMPS

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"[extract_frames] Video: {video_path}")
    print(f"[extract_frames] FPS: {fps:.1f}, Duration: {duration:.2f}s, Total frames: {total_frames}")

    results = {}
    for t in timestamps:
        frame_num = int(t * fps)
        if frame_num >= total_frames:
            print(f"[extract_frames] Skip frame at {t}s (beyond duration)")
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if not ret:
            print(f"[extract_frames] Failed to read frame at {t}s")
            continue

        filename = f"frame_{t:02d}s.jpg"
        filepath = os.path.join(output_dir, filename)
        success = cv2.imwrite(filepath, frame)
        if success:
            results[t] = filepath
            print(f"[extract_frames] Saved: {filename}")
        else:
            print(f"[extract_frames] Failed to save frame at {t}s")

    cap.release()
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Extract key frames from video at specified timestamps"
    )
    parser.add_argument("video", help="Path to video file (mp4/mov/avi)")
    parser.add_argument("output", nargs="?", default=DEFAULT_OUTPUT,
                        help="Output directory (default: frames)")
    parser.add_argument("--timestamps", "-t", type=str, default=None,
                        help="Comma-separated timestamps in seconds, e.g. '0,3,8,15,22,30'")

    args = parser.parse_args()

    timestamps = None
    if args.timestamps:
        try:
            timestamps = [float(x.strip()) for x in args.timestamps.split(",")]
        except ValueError:
            print("Error: Invalid timestamp format. Use comma-separated numbers, e.g. '0,3,8'")
            sys.exit(1)

    try:
        results = extract_frames(args.video, args.output, timestamps)
        print(f"\n[Done] Extracted {len(results)} frames to: {os.path.abspath(args.output)}")
        return 0
    except Exception as e:
        print(f"[Error] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
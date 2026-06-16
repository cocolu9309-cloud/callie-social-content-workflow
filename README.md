# Callie Social Content Workflow

> 社媒内容生成工具包 — 不同电脑、不同 AI Agent、不同人都能快速生成专业级社媒内容包

## 功能

- **产品信息提取**：上传产品图片，AI 自动识别
- **视频结构拆解**：分析热门视频的 Hook/CTA/叙事结构
- **多平台内容生成**：英文文案 + Hashtag + 中文脚本 + 关键帧分镜
- **关键帧AI生图**：调用 SiliconFlow Qwen-Image 生成9:16参考图（支持动态prompts）
- **Excel自动化输出**：格式化内容包，嵌入参考图

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
copy config.example.yaml config.yaml
# 编辑 config.yaml，填入 siliconflow_api_key

# 方式A: 一键运行（推荐）— 传入 Step C 输出的 content.json，自动串联生图+Excel
python scripts/run_all.py content.json output.xlsx

# 方式B: 分步运行
# 3a. 提取视频帧
python scripts/extract_frames.py "video.mp4" frames/

# 3b. 生成关键帧图片
#    动态模式（推荐）：从 AI 生成的 script_rows 自动翻译为英文 prompts
python scripts/generate_keyframes.py keyframes/ --script-rows @content.json --count 6
#    默认模式：使用内置硬编码 prompts
python scripts/generate_keyframes.py keyframes/ --config config.yaml --count 6

# 3c. 打包 Excel
python scripts/build_excel.py content.json output.xlsx --keyframes keyframes/
```

## 项目结构

```
callie-social-content-workflow/
├── config.example.yaml           # 配置模板
├── workflow.social-content.yaml  # Workflow 编排
├── requirements.txt              # Python 依赖
├── scripts/
│   ├── extract_frames.py         # 视频帧提取
│   ├── generate_keyframes.py     # 关键帧生图（支持动态prompts）
│   ├── build_excel.py            # Excel 输出
│   └── run_all.py               # 一键串联脚本
├── skills/
│   └── social-content-generator/
│       └── SKILL.md             # 主 Skill
└── references/                   # 品牌/平台规则
    ├── brand-guide.md
    ├── platform-rules.md
    └── output-format.md
```

## 使用文档

详细说明请参考：`Callie_Social_Content_Workflow_User_Guide.docx`

## 平台支持

Instagram / TikTok / Pinterest / YouTube Shorts / Facebook / X

## 版本

v1.1.0 | 2026-06-16 — 支持动态 keyframe prompts、一键 run_all.py
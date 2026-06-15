---
name: callie-social-content-generator
description: >
  Generate brand-safe multi-platform social content packs for Callie.com products.
  Input: product images + links + trending video files + target platform.
  Output: English post copy + platform hashtags + Chinese video script + keyframe storyboard + AI-generated reference images.
  Use when generating TikTok/Reels/Shorts scripts, Instagram posts, Pinterest pins, or website copy.
---

# Callie Social Content Generator

Generate creative, brand-safe multi-platform social content packs for Callie.com, a personalized gift brand. Produces complete content packages including English copy, hashtags, Chinese video scripts, and keyframe reference images.

## Workflow

This skill follows a 4-step workflow. Execute steps in order.

### Step A: Product Information Extraction

**重要说明：** 此步骤的输入由用户主动提供，Workflow 不会自动从 callie.com 抓取产品信息。

**用户需要准备：**
1. 产品图片：访问 callie.com，找到目标产品页面，下载 1-3 张产品图片（清晰、白底最佳）
2. 产品链接：复制该产品页面的 URL
3. 将图片和链接提供给 AI Agent

**Process:**
1. Analyze each product image using AI Vision — extract: product name, category, material, style, target occasion, target audience
2. Ask user to confirm or correct the extracted product info
3. Store confirmed product insight for Step C

**Output format:**
```
产品名称: [name]
品类: [category]
材质/风格: [material/style]
适用场景: [occasions]
目标人群: [target audience]
```

**Example（以实际产品为例）：**
```
用户输入:
- 产品链接: https://www.callie.com/personalized-wooden-photo-box...
- 产品图片: 7张定制木盒相册产品图

AI 分析输出:
产品名称: Personalized Wooden Photo Box with Pull-Out Folding Photos
品类: 定制木盒相册 / 纪念品
材质/风格: 榉木/枫木，浅原木色，风琴式折叠结构
适用场景: 纪念日、情人节、婚礼、生日、母亲节/父亲节
目标人群: 情侣、夫妻、闺蜜、家人；追求生活仪式感的人群
```

---

### Step B: Trending Video Structure Analysis

**Input:** User provides a trending video file (mp4/mov)

**Process:**
1. Use `scripts/extract_frames.py` to extract key frames from the video:
   ```bash
   python scripts/extract_frames.py <video_file> <output_dir>
   ```
2. Analyze each extracted frame using AI Vision — extract:
   - Hook type (悬念/情感/POV/礼物揭晓/问题抛出/前后对比)
   - CTA type (账号引导/购买引导/评论互动/无明显CTA)
   - Narrative structure (三段式/问题-解决/情感故事/清单式)
   - Pacing breakdown (0-3s/3-15s/15-30s)
   - Text/overlay usage style
3. Ask user to confirm or upload a different video
4. Store confirmed video insight for Step C

**Output format:**
```
Hook类型: [type]
Hook机制: [how it grabs attention in first 3 seconds]
CTA类型: [type]
叙事结构: [structure type]
节奏分布:
  0-3秒: [Hook内容]
  3-15秒: [Body内容]
  15-30秒: [Reveal/CTA内容]
文字Overlay: [style description]
可复用元素: [replicable elements]
```

---

### Step C: Platform Content Generation

**Input:** Product insight (Step A) + Video insight (Step B) + Target platform

**Process:**
1. Load references:
   - `references/brand-guide.md` — Callie positioning, tone, audience, category anchors
   - `references/platform-rules.md` — Target platform rules
   - `references/output-format.md` — Output format template
2. Combine product insight + video insight as creative seed
3. Generate a complete content pack for the target platform (one platform per run)

**Output requirements — Full content pack must include:**
- Big Idea (一句核心创意概念)
- Brand Angle (品牌角度)
- Product Tie-in (产品关联，轻/中/强)
- English Caption (平台定制英文文案)
- 11 Hashtags (TikTok: 11个; Instagram: 5-8个; 其他平台按规则)
- Chinese Video Script (中文视频脚本，含时间节点)
- Keyframe Storyboard (关键帧分镜描述，4-6帧)
- Visual Direction (视觉方向)
- CTA (行动引导)
- Brand Safety Check (品牌安全检查)

**Brand safety rules:**
- No exaggerated claims
- No discount/price info
- No competitor mentions
- Brand-safe trends only (avoid politics, disasters, medical anxiety, body shame, fear-based hooks, vulgarity)
- Emotionally specific, not generic "perfect gift" language
- Never claim specific product features unless user provides them

---

### Step D: Keyframe Reference Image Generation (Optional)

**Input:** Confirmed Chinese video script from Step C

**Process:**
1. If user requests AI-generated reference images:
   - Run `scripts/generate_keyframes.py`:
     ```bash
     python scripts/generate_keyframes.py <output_dir> --config config.yaml --count 6
     ```
   - This generates 6 AI images (9:16 vertical format) via SiliconFlow Qwen-Image API
2. Then run `scripts/build_excel.py` to package everything:
   ```bash
     python scripts/build_excel.py <content_json> <output.xlsx> --keyframes <keyframes_dir>
     ```
3. Present the final Excel file to the user

**Content JSON format for build_excel.py:**
```json
{
  "product_name": "...",
  "video_ref": "@account",
  "big_idea": "...",
  "brand_angle": "...",
  "product_tie_in": "...",
  "caption": "...",
  "hashtags": "...",
  "cta": "...",
  "script_rows": [
    ["0-1s", "画面描述", "镜头运动", "文字Overlay(英文)", "情绪氛围", "备注", "帧1", "keyframe_01.jpg"],
    ...
  ],
  "storyboard_rows": [
    ["帧1", "0-1s", "画面描述", "镜头运动", "文字Overlay(英文)", "情绪氛围", "keyframe_01.jpg"],
    ...
  ],
  "product_rows": [
    ["产品名称", "English name", "中文说明"],
    ...
  ]
}
```

---

## Output Format (Per Platform)

### TikTok
- 3-second hook (文字/画面描述)
- 15-30 second script (逐段中文描述)
- On-screen text (建议叠加的文字)
- Sound/trend suggestion (类型建议，非具体音频)
- English caption
- 11 hashtags

### Instagram Reels
- Reel hook (3秒视觉开场)
- Caption (英文文案)
- Carousel/Story idea (如果适用)
- 5-8 hashtags

### Pinterest
- Pin title (英文，SEO友好)
- Pin description (英文，1-2句话)
- Keywords (5个核心词)
- Board suggestion (收藏夹名称)
- Vertical visual direction (竖图构图描述)

### YouTube Shorts
- Title (英文，可搜索+情感化)
- 15-30 second script (逐段中文描述)
- On-screen text (建议叠加的文字)
- Description (英文，含关键词和CTA)
- Thumbnail text (缩略图文字建议)

### Facebook
- Post copy (英文文案)
- Conversation prompt (引发评论的问题)
- CTA (行动引导)

### X (Twitter)
- Short post (英文，1-2句话)
- Thread opener or poll (如果适用)
- 0-2 hashtags

---

## Defaults

- Language: English for multi-country markets. Add concise Chinese internal notes only when useful for review.
- Strategy: Brand awareness first, product/category tie-in second.
- Market: Multi-country English audience unless the user names a specific country.
- Platforms: Instagram, Facebook, YouTube Shorts, TikTok, Pinterest, X when user asks for a full pack.
- Trend policy: Brand-safe trends only. Avoid politics, disasters, medical anxiety, body shame, fear-based hooks, vulgarity, controversy bait, and exaggerated claims.

---

## Quality Standards

- Make each platform version structurally different, not just copied captions
- Tie content to Callie through personalized gifting, keepsakes, celebration, relationship moments, or thoughtful design
- Use concrete occasions: birthdays, graduation, weddings, bridesmaids, Mother's Day, Father's Day, anniversaries
- Prefer emotionally specific ideas over generic "perfect gift" language
- Keep hashtags selective and platform-appropriate
- Do not claim specific product features, discounts, shipping promises, awards, or customer data unless user provides them

---

## File Structure Reference

```
callie-social-content-workflow/
├── config.example.yaml           # 配置文件模板
├── workflow.social-content.yaml  # Workflow编排文件
├── sample-input/                 # 示例输入文件（参考）
│   ├── README.md                # 输入准备说明
│   ├── sample-product-info.json  # 产品信息 JSON 示例
│   └── sample-content-json.json  # build_excel.py 输入 JSON 示例
├── scripts/
│   ├── extract_frames.py          # 视频帧提取 CLI
│   ├── generate_keyframes.py      # 关键帧AI生图 CLI
│   └── build_excel.py            # Excel输出 CLI
├── skills/
│   └── social-content-generator/
│       └── SKILL.md              # 本 Skill
└── references/
    ├── brand-guide.md            # 品牌指南
    ├── platform-rules.md         # 平台规则
    └── output-format.md          # 输出格式
```

**用户输入文件准备提示：**
- 将产品图片放在任意目录，提供给 AI Agent 分析
- 将竞品视频放在任意目录，使用 `extract_frames.py` 提取帧
- 参考 `sample-input/sample-product-info.json` 了解产品信息格式
- 参考 `sample-input/sample-content-json.json` 了解 build_excel.py 的 JSON 输入格式

---

## Dependencies

- **Python 3.8+** with: `opencv-python`, `openpyxl`, `Pillow`, `PyYAML`, `httpx`
- **SiliconFlow API Key** (for keyframe image generation) — set in `config.yaml` or via `SILICONFLOW_API_KEY` env var
- **AI Vision** (multimodal LLM for product image analysis and video frame analysis)
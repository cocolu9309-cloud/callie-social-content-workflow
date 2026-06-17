# Callie 社媒内容生成 Workflow
## 普通运营也能看懂的使用说明书

> **一句话说明**：上传产品图 +（可选）热门视频，AI 自动生成 Instagram/TikTok 等平台的英文文案 + Hashtag + 中文视频脚本 + 关键帧参考图，最终输出一个 Excel 文件。

---

## 准备工作（只需做一次）

### 1. 安装软件

需要 **Python 3.8 以上**（一般电脑自带，可跳过）

打开命令提示符，输入：
```bash
python --version
```
看到 `Python 3.8.x` 或更高版本就 OK。

### 2. 安装依赖

在项目目录下运行：
```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

去 [SiliconFlow 官网](https://siliconflow.cn) 注册，拿到 API Key。

在项目根目录创建 `config.yaml`：
```bash
copy config.example.yaml config.yaml
```

用记事本打开 `config.yaml`，把 `siliconflow_api_key` 那行改成你的 Key：
```yaml
siliconflow_api_key: "你的Key"
```

---

## 完整流程（Step A → Step D）

---

## Step A：准备产品信息

### 你需要准备

- **1-3 张产品图**（清晰、白底最好）
- **产品链接**（可选，但推荐提供）

### 怎么做

把图片放进任意文件夹（比如 `my-product/`），把链接复制好。

打开 AI Agent（Claude / ChatGPT 等），把以下内容发给它：

```
请分析这个产品，提取：产品名称、品类、材质/风格、适用场景、目标人群

产品链接：https://www.callie.com/你的产品链接
产品图片：放在 my-product/ 文件夹里
```

AI 会输出一段产品描述，保存下来备用。

---

## Step B：准备竞品视频（可选，但推荐）

### 你需要准备

- **1 个热门竞品视频**（mp4/mov 格式，时长 9-30 秒最佳）
- 可以从 TikTok / Instagram Reels 下载

### 怎么做

把视频放进任意文件夹（比如 `my-video/`）。

运行帧提取脚本：
```bash
python scripts/extract_frames.py my-video/竞品视频.mp4 frames
```

这会在 `frames/` 文件夹生成 6 张关键帧图片。

把帧图片发给 AI Agent 分析结构：
```
请分析这个视频的爆款结构：
1. 前3秒用什么方式吸引注意力（Hook）
2. 视频节奏怎么分布（0-3秒/3-15秒/15-30秒）
3. 结尾怎么引导互动（CTA）

视频帧图片在 frames/ 文件夹里
```

AI 会输出视频结构分析，保存下来。

---

## Step C：生成内容包

### 你需要准备

- Step A 的产品描述
- Step B 的视频结构分析（如果有）
- **目标平台**：TikTok / Instagram / Pinterest / YouTube Shorts / Facebook / X

### 怎么做

把以上信息发给 AI Agent，要求它参考以下文件生成内容：

```
请参考 references/brand-guide.md 和 references/platform-rules.md，
为 [目标平台] 生成完整社媒内容包，包含：
- Big Idea（核心创意概念）
- 英文文案（直接可发布）
- 11个 Hashtag（TikTok）/ 5-8个（Instagram）
- 中文视频脚本（含时间节点）
- 关键帧分镜描述（4-6帧）
- CTA（行动引导）

产品信息：[Step A的输出]
视频结构：[Step B的输出，如果有]
目标平台：[选一个]
```

**重要**：让 AI 输出的 JSON 格式如下（发给 AI 时说明这个格式）：

```json
{
  "product_name": "产品名称",
  "platform": "Instagram",
  "video_ref": "@account",
  "big_idea": "...",
  "brand_angle": "...",
  "product_tie_in": "...",
  "caption": "英文文案全文",
  "hashtags": "#tag1 #tag2 ...",
  "cta": "行动引导文字",
  "script_rows": [
    ["0-1s", "画面描述（中文）", "镜头运动", "文字Overlay(英文)", "情绪氛围", "备注", "帧1", "keyframe_01.jpg"],
    ["1-3s", "...", "...", "...", "...", "...", "帧2", "keyframe_02.jpg"],
    ...
  ],
  "storyboard_rows": [
    ["帧1", "0-1s", "详细画面描述", "镜头运动", "文字Overlay", "情绪氛围", "keyframe_01.jpg"],
    ...
  ],
  "product_rows": [
    ["产品名称", "English name", "中文说明"],
    ["品类", "...", ""],
    ...
  ]
}
```

把这段 JSON 复制保存为 `content.json` 文件。

---

## Step D：生成图片 + 导出 Excel

### 你需要准备

- `content.json`（Step C 的输出）

### 怎么做

运行一键脚本（推荐）：
```bash
python scripts/run_all.py content.json Callie_Instagram_Content_Pack.xlsx
```

这会自动：
1. 读取 `content.json` 的 `script_rows`
2. 生成 6 张关键帧参考图（9:16 竖版）
3. 打包成 Excel 文件

生成的图片在 `keyframes/` 文件夹，Excel 文件为 `Callie_Instagram_Content_Pack.xlsx`。

---

## Excel 文件包含什么

| 工作表 | 内容 |
|--------|------|
| 内容总览 | Big Idea、品牌角度、英文文案、Hashtag、CTA |
| 视频脚本 | 每帧的时间、画面描述、镜头、情绪、参考图 |
| 关键帧分镜 | 完整分镜描述 + AI 生成参考图 |
| 产品信息 | 产品名称、品类、材质、适用场景、目标人群 |
| 品牌安全检查 | 10 项合规检查（自动通过） |

---

## 常见问题

**Q: API Key 哪里拿？**
A: 去 [siliconflow.cn](https://siliconflow.cn) 注册，充值一点点钱（生成6张图约几毛钱）。

**Q: 生成图片需要多久？**
A: 每张约 10-30 秒，6 张约 1-2 分钟。

**Q: AI Agent 一定要用 Claude 吗？**
A: 不需要，任何能读文件、能分析图片的 AI Agent 都可以。

**Q: 没有竞品视频怎么办？**
A: 可以跳过 Step B，直接用产品图生成内容包，AI 会用默认结构。

**Q: 想换目标平台怎么办？**
A: 重新跑 Step C，换目标平台，重新生成 content.json，再跑 Step D。

**Q: 图片生成失败怎么办？**
A: 检查 API Key 是否正确、网络是否稳定。可以重跑：
```bash
python scripts/run_all.py content.json output.xlsx --delay 3.0
```
`--delay 3.0` 表示每张图之间等 3 秒，防止被限流。

---

## 快速命令速查

```bash
# 提取视频帧
python scripts/extract_frames.py 视频.mp4 frames

# 生成关键帧图片（用 content.json 里的中文脚本）
python scripts/generate_keyframes.py keyframes/ --script-rows @content.json -n 6

# 打包 Excel
python scripts/build_excel.py content.json output.xlsx --keyframes keyframes/

# 一键完成（推荐）
python scripts/run_all.py content.json output.xlsx
```

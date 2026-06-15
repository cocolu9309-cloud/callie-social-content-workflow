# 示例输入说明

此目录提供工作流所需输入文件的格式参考。

---

## 用户需要准备什么

### 1. 产品图片（必填）

将产品图片放在任意目录（如 `my-product/`），上传给 AI Agent 分析。

**建议：**
- 1-3 张清晰产品图
- 白底最佳，也可以是场景图
- 包含产品正面、背面、细节（如刻字特写）

**示例文件：**
```
my-product/
├── 产品图_正面.jpg
├── 产品图_背面.jpg
└── 产品图_细节.jpg
```

---

### 2. 产品链接（可选）

复制 callie.com 产品页 URL，粘贴给 AI Agent。

示例：
```
https://www.callie.com/personalized-wooden-photo-box-with-pull-out-folding-photos
```

---

### 3. 竞品视频（可选，但推荐）

将视频文件放在任意目录，上传给 AI Agent 分析结构。

**建议：**
- 1 个 mp4/mov 文件
- 时长 9-30 秒最佳
- 选择平台上的热门/爆款视频

**示例：**
```
my-video/
└── 竞品热门视频.mp4
```

---

## 工作流中的输入流向

```
用户准备
├── 产品图片  ──→  Step A：AI Vision 分析  ──→  产品洞察 JSON
├── 产品链接  ──→  （参考，AI 不会自动抓取）
├── 竞品视频  ──→  Step B：extract_frames + AI Vision  ──→  视频结构洞察
└── 目标平台  ──→  Step C：内容生成

        ↓

Step C 输出：
├── 英文贴文
├── 11个 Hashtag
├── 中文视频脚本
├── 关键帧分镜
└── 内容包 JSON  ──→  Step D：build_excel.py  ──→  Excel 文件
```

---

## 如何使用示例 JSON

### sample-product-info.json

这是 Step A 的**输入示例**，展示产品信息长什么样。
**用途：** 了解 AI 会分析出哪些字段，以及如何组织这些信息。

### sample-content-json.json

这是 Step D 的**输入示例**，是 build_excel.py 所需的 JSON 格式。
**用途：** 了解如何将 AI 生成的内容组织成 Excel 打包脚本可用的格式。

---

## 快速开始示例

```bash
# 1. 把产品图放进 my-product/ 目录

# 2. 把视频放进 my-video/ 目录

# 3. 提取视频帧
python scripts/extract_frames.py my-video/竞品视频.mp4 frames

# 4. 生成关键帧图
python scripts/generate_keyframes.py keyframes -n 6

# 5. 把 AI 生成的内容组织成 JSON，参考 sample-content-json.json 格式

# 6. 打包 Excel
python scripts/build_excel.py content.json output.xlsx --keyframes keyframes
```
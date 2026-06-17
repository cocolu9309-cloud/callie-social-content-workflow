# Callie 社媒内容生成工具

> 上传产品图 +（可选）视频，选择平台，一键下载 Excel 内容包

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
# 编辑 config.yaml，填入 siliconflow_api_key
# 注册 SiliconFlow: https://siliconflow.cn

# 3. 启动服务
uvicorn app:app --reload --port 8000

# 4. 打开浏览器
# http://localhost:8000
```

## 功能

- 上传 1-3 张产品图，AI 自动分析产品信息
- （可选）上传竞品视频，AI 分析爆款结构（自动截取 6 帧）
- 选择目标平台：Instagram / TikTok / Pinterest / YouTube Shorts / Facebook / X
- AI 生成：英文文案 + Hashtag + 中文视频脚本 + 关键帧参考图
- 下载格式化 Excel 内容包（含3个工作表）

## 使用流程

1. 上传产品图（必填）
2. 上传竞品视频（可选）
3. 选择目标平台
4. 输入产品名称（可选）
5. 点击"开始生成"，等待 2-5 分钟
6. 点击"下载 Excel 内容包"

## 输出 Excel 包含

| 工作表 | 内容 |
|--------|------|
| 内容总览 | Big Idea、品牌角度、英文文案、Hashtag、CTA |
| 视频脚本 | 每帧时间、画面描述、镜头、情绪、参考图 |
| 品牌安全检查 | 6项合规检查 |

## API 配置

使用 [SiliconFlow](https://siliconflow.cn)：
- LLM 模型：`Qwen/QwQ-32B`（文案生成）
- 生图模型：`Qwen/Qwen-Image`（关键帧参考图）

推荐充值 ¥50-100 可生成约 50-100 次内容包。

## 技术栈

- 后端：FastAPI + openpyxl + httpx
- 前端：单页 HTML + 原生 JS（无需构建）
- AI：SiliconFlow（LLM + 图生模型）
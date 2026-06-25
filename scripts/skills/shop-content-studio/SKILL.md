---
name: shop-content-studio
description: 为 Shops Agent 店铺批量生成营销内容——商品文案、SEO 博客、社媒帖子、EDM 邮件，以及商品图处理（去背景/换场景/放大/生成视频）。当用户要写商品描述、营销文案、推广素材，或要做配图/换背景/出图时使用。依赖 shops-agent MCP 服务。
---

# Shops Agent — 内容工作室

用 `shops-agent` MCP 工具生成文案与图片素材。

## 前置
- 后端在运行；内容/图片工具需要登录，先 `login`（默认 `admin` / `admin123`）。
- AI 默认是 mock provider（无需 key），输出为模板化演示内容；接入真实 Claude 见 backend/README。

## 文案 `generate_content`
- `kind`：`product_desc`（商品描述）| `seo_blog`（SEO 博客）| `social`（社媒）| `edm`（邮件）。
- `store`：提供店铺上下文（key 或 slug）。
- `language`：默认 `English`，中文传 `中文`。
- `params`：自由字段，按需传 `category` / `material` / `keywords` / `channel` 等。

流程：确认 `kind`、店铺、语言、关键卖点 → 调用 → 把 `content` 呈现给用户，必要时改写润色。
批量需求（同一商品多渠道）就对每个 `kind` 各调一次。

## 图片 `generate_image`
- `operation`：`bg_remove`（去背景）| `scene_swap`（换场景）| `upscale`（放大）| `video`（生成视频）。
- `scene`：换场景时的场景描述（如 `雪天`、`城市街拍`）。
- `source`：源图文件名/URL 占位。

## 注意
- mock 模式产物是占位/模板，用于演示流程；交付前提示用户这一点。
- 如果用户要真实出图（非本店铺素材流水线），考虑改用 ComfyUI（见用户偏好），而不是此工具。

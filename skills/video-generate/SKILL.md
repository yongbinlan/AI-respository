---
name: video-generate
description: 使用 video_generate.py 脚本生成视频，需要提供文件名和 prompt，可选提供首帧图片（URL或本地路径）。脚本会返回视频 URL（有效期 24 小时）。
---
# Video Generate

## 适用场景
当需要根据文本描述生成视频时，使用该技能。支持通过首帧图片控制视频起始画面，首帧可以是 URL 或本地文件路径。

## 功能特性
- ✅ 支持首帧图片控制视频起始画面
- ✅ 自动处理 API 认证和权限获取
- ✅ 输出视频 URL（有效期 24 小时），可直接分享给用户

## 使用步骤
1. 准备目标文件名（如 `output.mp4`）和清晰具体的 `prompt`。
2. (可选) 准备首帧图片，可以是 HTTP URL，也可以是本地文件路径（脚本会自动转为 Base64）。
3. 运行脚本 `python scripts/video_generate.py <filename> "<prompt>" [first_frame]`。运行之前cd到对应的目录。
4. 脚本将输出视频 URL 并下载到指定本地文件。
5. 将视频 URL 原封不动发送给用户。
6. 尝试使用 `message` 工具将生成的视频文件直接发送给用户预览。
7. 发送视频文件时必须使用**绝对路径**（例如 `/root/.openclaw/...`），禁止使用相对路径或 `~` 开头的路径，否则会导致上传失败。

## 认证与凭据来源
- 优先读取 `MODEL_VIDEO_API_KEY` 或 `ARK_API_KEY` 环境变量。
- 若未配置，将尝试使用 `VOLCENGINE_ACCESS_KEY` 与 `VOLCENGINE_SECRET_KEY` 获取 Ark API Key。

## 输出格式
- 控制台输出视频 URL（有效期 24 小时）。
- 视频文件将被下载到指定本地路径。

## 成功标准
一次视频生成任务，只有满足以下条件之一，才算真正完成：
1. **已将视频 URL 发送给用户**；
2. 若以上无法完成，已明确说明失败原因。
**仅生成出本地文件路径，不算任务完成。**

## 示例
### 1. 纯文本生成视频
```bash
cd ~/.openclaw/workspace/skills/video-generate
python scripts/video_generate.py "cat.mp4" "一只可爱的猫"
```
### 2. 带首帧图片生成（URL）
```bash
python scripts/video_generate.py "dog_run.mp4" "一只小狗在草地上奔跑" "https://example.com/dog_start.png"
```
### 3. 带首帧图片生成（本地文件）
```bash
python scripts/video_generate.py "my_video.mp4" "图片中的人物动起来" "/path/to/local/image.jpg"
```

## 禁止行为
- 不要把本地文件路径当作用户可预览结果。
- 不要在云端运行场景下让用户访问 `~/.openclaw/...` 路径。
- 不要修改或截断视频 URL，必须原封不动发送给用户。
- 不要将"生成完成"误判为"任务完成"；生成后必须发送 URL 给用户。

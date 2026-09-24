# AI-respository

可以按需安装的 Codex Skills，以及本地 AI 工具部署教程。技能和教程分别放在独立目录，按需选择使用。

## 选一个开始

[北辰·成果引擎 · Polaris Forge](skills/polaris-forge/README.md)

让 Codex 在开工前理解需求、补上遗漏，交付前检查结果。适合开发功能、做内容和设计，也能用来检查搁置了一段时间的项目。

[照片转 PFP](skills/photo-to-chibi-pfp/README.md)

上传人物照片，生成同一人物、同一画风的九套穿搭总览。默认是 Pop Mart 潮玩风，也支持黏土、像素等画风；需要头像或单张全身图时可以直接指定。

## 安装

打开上面的使用说明，复制对应的安装指令发给 Codex。两项技能可以单独安装，照片转 PFP 还需要当前会话能使用内置生图工具。

如果要手动安装，先让 Codex 确认当前环境的技能目录并给出完整路径，再复制所选技能的整个文件夹。保留内部结构，遇到同名版本先比较，不直接覆盖，也不要写入其他 Agent 的目录。

装好后检查 Codex 的可用技能列表。暂时没出现时，重新开启会话或重启宿主后再检查。

## 本地部署教程

[Laya：Windows 与 macOS 本地部署、Codex MCP 接入](tutorials/laya/README.md)

从 Python 环境和模型下载开始，完成推理检查后接入 Codex。Windows 覆盖 NVIDIA CUDA / CPU，Mac 以 Apple Silicon MPS 为主，附 CPU 与 Intel 兼容性检查。已做文档和代码静态检查，尚未完成双平台实机验证。

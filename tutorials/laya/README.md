# Laya 本地部署与 Codex 接入

在自己的电脑上运行 Laya，通过本地 MCP 让 Codex 调用分类和判断工具。两套教程分别覆盖 Windows 与 macOS，从独立 Python 环境、模型下载到真实推理检查、Codex 接入和故障排查。

## 选择你的系统

| 系统 | 在线阅读 | 下载后用浏览器打开 |
| --- | --- | --- |
| Windows 10/11：NVIDIA CUDA 或 CPU | [Windows 教程](Laya-Windows-本地部署教程.md) | [HTML 版](Laya-Windows-本地部署教程.html) |
| macOS：Apple Silicon MPS 或 CPU；Intel 需先检查兼容性 | [macOS 教程](Laya-macOS-本地部署教程.md) | [HTML 版](Laya-macOS-本地部署教程.html) |

GitHub 文件页可以直接阅读 Markdown。HTML 文件请在文件页选择下载，再在本机浏览器打开；仓库未配置在线网页托管。

## 使用前了解

- 本地 Laya 推理无需 Jev API Key；安装依赖和首次下载模型需要联网。
- 本教程接入的是 Laya 工具，不会将 Codex 主模型替换为本地模型，也不代表整个 Codex 会话离线。
- 先跑教程里的真实模型检查，再注册 MCP。工具名出现、依赖导入成功，都不等于真实推理通过。
- 中文场景先使用 multilingual，并用自己的样本评估；分类置信度不是正确率保证。
- Intel Mac 仅提供兼容性检查分支，不承诺当前依赖一定可安装。

## 版本与验证范围

文档 v1，资料核对日期：2026-09-24。教程中的上游链接指向可更新页面，安装时仍需核对当前版本和硬件要求。

已完成教程代码的 PowerShell、Bash 语法检查，内嵌 Python 与 TOML 解析，以及 HTML 桌面和窄屏阅读检查。尚未完成 Windows/macOS 实际安装、模型推理及 Codex 工具调用的端到端验证；请按各教程的验收步骤确认目标设备结果。

本目录只提供教程，不包含模型权重、凭据或预装运行环境。上游项目：[Laya](https://github.com/NandhaKishorM/laya)；更详细的官方来源列在各教程末尾。

[返回仓库首页](../../README.md)

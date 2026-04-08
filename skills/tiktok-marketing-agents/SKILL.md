---
name: tiktok-marketing-agents
description: "TikTok营销独立Agent集合 - 7个Agent可单独调用，也可组合工作流"
metadata:
  openclaw:
    emoji: 🎭
---

# TikTok 营销独立 Agent 集合

本目录拆分了 `tiktok-marketing-automation` 工作流中的 7 个 Agent，每个 Agent 保存为独立文件，**支持单独调用**，也支持按原工作流组合运行。

## Agent 列表

| 文件 | Agent Name | 职责 |
|------|------------|------|
| [US_Trend_Scout.md](./US_Trend_Scout.md) | **US_Trend_Scout** | 趋势洞察官 - 挖掘爆款创意 + BGM + 标签 |
| [US_Culture_Localizer.md](./US_Culture_Localizer.md) | **US_Culture_Localizer** | 文化本地化专家 - 俚语适配 + 场景建议 |
| [US_Viral_Script_Director.md](./US_Viral_Script_Director.md) | **US_Viral_Script_Director** | 爆款脚本导演 - 秒级分镜 + BGM节点 + 配音标注 |
| [AI_Visual_Prompt_Engineer.md](./AI_Visual_Prompt_Engineer.md) | **AI_Visual_Prompt_Engineer** | AI 画面提示词工程师 - 转 Midjourney/Runway 提示词 |
| [Audio_Architect.md](./Audio_Architect.md) | **Audio_Architect** | 音频架构师 - 音乐推荐 + 音效 + TTS 设置 |
| [Engagement_Hacker.md](./Engagement_Hacker.md) | **Engagement_Hacker** | 互动增长黑客 - 标题/标签/评论诱饵 |
| [Performance_Analyst.md](./Performance_Analyst.md) | **Performance_Analyst** | 数据复盘分析师 - 流失诊断 + 优化建议 |

## 使用方式

### 方式 1：完整工作流运行（原方式）
> 运行完整流程自动输出全部产物  
> 调用：`用 tiktok-marketing-automation 跑一遍 [产品名]`

### 方式 2：单独调用某个 Agent
> 需要单独使用某个能力时，指定 Agent 文件名  
> 例如：
> - "用 US_Trend_Scout 分析 [产品名]"
> - "用 AI_Visual_Prompt_Engineer 把这些场景转成提示词"

### 方式 3：自定义流程
你可以跳过已完成步骤，只调用需要的 Agent：
1. 已有创意 → 直接调用 `US_Viral_Script_Director` 生成脚本
2. 已有脚本 → 直接调用 `AI_Visual_Prompt_Engineer` + `Audio_Architect`
3. 已有视频 → 直接调用 `Engagement_Hacker` 优化发布文案

## 文件结构
```
skills/tiktok-marketing-agents/
├── SKILL.md  <- 本索引
├── US_Trend_Scout.md
├── US_Culture_Localizer.md
├── US_Viral_Script_Director.md  <- 已升级：含BGM节点和配音标注
├── AI_Visual_Prompt_Engineer.md
├── Audio_Architect.md
├── Engagement_Hacker.md
└── Performance_Analyst.md
```

每个文件包含：职责、输入、输出、完整 System Prompt，可直接加载使用。

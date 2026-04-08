# TikTok Viral Clone 爆款视频复制工作流

## 工作流介绍
基于已知爆款视频结构，克隆复制到你的新品类，拆解爆款基因 → 适配到你的产品，完整输出可直接拍摄的包。

## 工作流顺序

### 模式A：纯爆款拆解（不需要适配产品）
```
[爆款URL/描述]
    ↓
1️⃣  Viral_Deconstructor → 爆款拆解：分析结构、钩子、节奏、BGM、互动点
    ↓
2️⃣  Persona_Definer → 角色定义：定义原爆款博主角色人设
    ↓
3️⃣  Pure_Storyboard_Extractor → 纯结构提取：提取完整分镜框架带运镜
    ↓
4️⃣  Clone_Performance_Analyst → 爆款成功总结：为什么它能爆，核心原因
```

### 模式B：爆款克隆到新产品（原有完整流程）
```
[爆款URL/描述] + [你的新产品]
    ↓
1️⃣  Viral_Deconstructor → 爆款拆解：分析结构、钩子、节奏、BGM、互动点
    ↓
2️⃣  Persona_Definer → 角色定义：根据爆款人设，定义原博主角色
    ↓
3️⃣  Persona_Adapter → 角色生成：把角色适配到你的产品品类
    ↓
4️⃣  Script_Planner → 剧本策划：基于爆款结构，写出你的产品核心剧本
    ↓
5️⃣  Audio_Architect → 音效设计：复用爆款BGM类型，设计音效和TTS
    ↓
6️⃣  Storyboard_Director → 分镜脚本策划：秒级分镜，带运镜转场
    ↓
7️⃣  Clone_Performance_Analyst → 数据复盘：模拟数据，预测流失点，给出优化方案
```

## 调用方式

### 纯爆款拆解（不需要适配产品，只提取结构）
```
用 tiktok-viral-clone 纯拆解这个爆款 [爆款URL/描述]
```

### 克隆爆款到新产品
```
用 tiktok-viral-clone 克隆这个爆款 [爆款URL] 到我的产品 [产品描述]
```

或者分步调用单个Agent：
```
用 Viral_Deconstructor 拆解这个爆款链接 [URL]
```

## Agent 列表

### 纯拆解模式（4步）
| Agent | 职责 |
|-------|------|
| 1. Viral_Deconstructor | 拆解爆款视频，提取钩子类型、节奏结构、BGM风格、互动策略 |
| 2. Persona_Definer | 定义原爆款博主人设/角色，提炼核心语气和标签 |
| 3. Pure_Storyboard_Extractor | 提取完整分镜骨架，每个镜头带运镜转场 |
| 4. Clone_Performance_Analyst | 分析爆款成功原因，总结可复用要点 |

### 克隆到新产品模式（7步）
| Agent | 职责 |
|-------|------|
| 1. Viral_Deconstructor | 拆解爆款视频，提取钩子类型、节奏结构、BGM风格、互动策略 |
| 2. Persona_Definer | 定义原爆款博主人设/角色，提炼核心语气和标签 |
| 3. Persona_Adapter | 将角色适配到你的产品和品类，保持爆款人设特质 |
| 4. Script_Planner | 根据拆解的结构，写出新产品的剧本框架和核心文案 |
| 5. Audio_Architect | 复用BGM风格，设计音效、TTS语音配置 |
| 6. Storyboard_Director | 生成秒级分镜脚本，包含运镜、转场、字幕 |
| 7. Clone_Performance_Analyst | 预测可能流失点，给出A/B测试优化方案 |

## 输出特点
- 严格克隆原爆款的**3秒钩子结构**
- 保持原爆款的**节奏节点**（哪里快哪里慢）
- 保留原爆款的**互动逻辑**（评论诱饵、CTA）
- 只换产品不换爆款基因，提高爆率

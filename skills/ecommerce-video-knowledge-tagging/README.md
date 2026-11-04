# 视频知识库素材标签打标

把电商参考视频整理成可搜索的案例卡。策划人员可以按商品、购买问题、开头机制或证明动作找案例，再回到原片看它在什么情境下成立。

## 适用场景

| 场景 | 输入 | 交付 |
| --- | --- | --- |
| 货架电商案例 | 主图或详情视频、来源信息 | 商品展示、购买问题、证明动作及原片时段 |
| 内容电商案例 | 带货视频、原稿或拆解 | 开头机制、内容结构、原句表达及适用边界 |
| 案例入库与补标 | 当前案例版本、已有证据、可用的入库接口 | 标签卡、缺口清单，以及经回查确认的入库结果 |

E 通道实拍混剪素材和个人 IP 使用各自的标签体系。

## 打标逻辑

1. 确认业务域、来源和版本，按原片时间轴记录所见所听。
2. 将可见动作与内容解读分开。每个标签指向具体证据，能定位的动作附原片秒数。
3. 原稿、完整原句和译文独立保存。单个组件只引用其区段能支持的标签。
4. 生成 Markdown 和 JSON 标签卡，列出缺口。已接入知识库的任务沿其原接口预检、去重、提交版本并分域回查。

## 安装与使用

让 Codex 从 `yongbinlan/AI-respository` 的 `main` 分支安装 `skills/ecommerce-video-knowledge-tagging`。也可把该目录完整复制到 Codex 的 Skill 目录。已有同名的项目版时，先比较版本和适用环境。

提供有权使用的原片或可核查的拆解记录，再向 Codex 发送：

```text
用 $ecommerce-video-knowledge-tagging 给这条收纳盒主图视频打标。
归到货架电商，重点提取购买问题、证明动作和原片时间段。
输出 Markdown 和 JSON 标签卡预览，原句照录，证据不足的维度列为缺口。
```

公开版可根据你提供的材料生成标签卡。按案例 ID 查找、自动读取视频或正式入库，分别取决于当前环境的知识库读取、视频读取和入库能力。安装 Skill 后，用一条已授权样本检查两份卡片、证据指针和时间轴。

## 标签示例

以下是合成示例，用于说明结构。真实卡片应附来源及其他可核查材料。

```json
{
  "case_id": "DEMO-001",
  "revision": 1,
  "business_domain": "shelf_commerce",
  "status": "read_only_preview_not_committed",
  "observed_segments": [
    {
      "start": 4.2,
      "end": 6.8,
      "observation": "手把同一只收纳盒从抽屉里抬起，再平放回原位置。"
    }
  ],
  "structured_tags": {
    "schema": "ecommerce-material-tags-v1",
    "scope": "commerce_reference",
    "dimensions": {
      "proof_action": [
        {
          "value": "抬起收纳盒并放回抽屉",
          "basis": "source_observation",
          "evidence_refs": ["/observed_segments/0/observation"],
          "start": 4.2,
          "end": 6.8
        }
      ]
    }
  },
  "missing_dimensions": [
    "product_type", "content_form", "scene", "audience", "purchase_problem",
    "core_benefit", "hook", "segment_role", "structure", "voice", "use_boundary"
  ]
}
```

这个片段支持记录取放动作。适配尺寸、承重和耐用性需各自的证据。

[查看 Skill 的完整执行规则](SKILL.md)

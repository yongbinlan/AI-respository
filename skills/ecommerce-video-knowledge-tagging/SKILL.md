---
name: ecommerce-video-knowledge-tagging
description: 为货架电商和内容电商的视频参考案例提取有原片证据的标签，输出可检索的 Markdown 和 JSON 案例卡，支持既有知识库的受控入库流程。适合主图视频和带货内容分析，排除实拍混剪素材与个人 IP。
---

# 视频知识库素材标签打标

将电商参考视频整理成可检索的案例卡。输入是有权使用的原片、已有时间轴拆解，或可通过用户环境读到的案例记录。确认来源、案例标识、版本和业务域。只有案例 ID 且无法读取记录时，请用户提供原片或拆解资料。默认交付本地预览卡。

## 确认业务范围

- `shelf_commerce` 用于主图、详情页等购买决策位置。重点看商品展示、购买问题和证明动作。
- `content_commerce` 用于推荐流等带货内容。重点看开头、段落职责、叙事推进和信任承接。
- 以视频实际投放位置和来源记录分类。归属不明确时保留缺口。实拍混剪素材（E 通道）、个人 IP、作者自编示例和纯数据报告不进入该流程。

## 从证据生成标签

1. 按原顺序记录片段起止、可见动作、说出的内容和结果。复用已经确认的拆解，补标签时定向回看。拿不到完整原片时，只使用已有可核查资料并标明覆盖范围。
2. 使用 `commerce_reference` 标签范围。核心维度包括 `product_type`、`content_form`、`scene`、`audience`、`purchase_problem`、`core_benefit`、`hook`、`proof_action`、`segment_role`、`structure`、`voice` 和 `use_boundary`。按本片实际内容选择标签，避免用文件名、标题或已有标签互相证明。
3. 可见事实标为 `source_observation`，受众、动机、叙事等解读标为 `editorial_analysis`。每个标签提供 `value`、`basis`、`evidence_refs`。证据用 JSON Pointer 指向同一记录的实际字段。记录 `start` 与 `end` 时，两者为原片秒数且落在对应证据区段内。证明动作写清实际操作与可见结果。
4. 原稿和完整原句与标签分开保存。保留原文、可核实的原片时段及译文状态。组件只标自身片段支持的内容。来源销量、榜单资格、观察覆盖和实际转化证据分别记录。

## 交付与入库

- 同时输出可读的 Markdown 案例卡和对应 JSON。包括案例标识与版本、来源、业务域、时间轴、标签与证据、原文或翻译引用、缺失维度和使用边界。检查指针可解析、区段不越界、原文未被改写。缺项保留为缺口，旧记录默认不批量回填。
- JSON 标签用 `structured_tags`，其中包含 `schema: ecommerce-material-tags-v1`、`scope: commerce_reference` 和 `dimensions`。预览状态使用 `read_only_preview_not_committed`。字段格式见 [使用说明中的示例](README.md#标签示例)。
- 用户要求正式入库且现有库接口可用时，调用其预检、去重、版本化写入及分域回查。已绑定版本的内容先生成准备稿再提交。以回查结果报告入库状态。缺少接口时交付准备稿，正式入库列为待接入事项。

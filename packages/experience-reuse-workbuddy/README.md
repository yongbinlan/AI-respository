# Experience Reuse · WorkBuddy 版

把有效执行经验留在所属项目，让后续相关任务在行动前读取、核条件并采用。新建 Skill 第一次真实任务就成功，也保存实际方法、适用条件和验证证据。

## 下载 v1.0.0

- [下载 WorkBuddy 专用 ZIP](https://raw.githubusercontent.com/yongbinlan/AI-respository/main/packages/experience-reuse-workbuddy/v1.0.0/Experience-Reuse-WorkBuddy-v1.0.0.zip)（32,754 字节）
- [复制 GitHub 下载安装提示词](INSTALL_FROM_GITHUB.txt)
- [SHA-256 校验清单](v1.0.0/SHA256SUMS)
- [脱敏封装验证摘要](v1.0.0/verification.json)

```text
SHA-256: b72f213fd0578ab383bb293c8f7711e2288d8ea75bf5007353ffb25abfc4b1d8
```

这是独立的 WorkBuddy 包。不要用本仓库 `skills/experience-reuse` 的 Codex 版文件夹代替这个 ZIP。公开包只含方法、脚本和合成测试，不携带个人经验、聊天、Cookie、登录态或本机绝对路径。

## 安装与配置

1. 将 ZIP 下载到目标电脑并核对校验值。
2. 在 WorkBuddy 打开“技能 → 添加技能 → 上传技能”，选择本地 ZIP，导入后确认已安装且启用。当前官方说明规定自制包用上传入口；聊天中的市场搜索不能替代此操作。[官方技能说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)
3. 把 [INSTALL_FROM_GITHUB.txt](INSTALL_FROM_GITHUB.txt) 的提示词发给 WorkBuddy，让它解析实际安装路径，按包内 `references/workbuddy-setup.md` 配置条件自动触发。`routing-template.md` 中的路径占位符要替换为本机真实路径；保留原有规则和同名版本备份。
4. 优先使用当前版本明确支持的用户级自动加载入口。WorkBuddy 官方说明代码任务支持 `.codebuddy` 用户/项目配置，但这不能推出所有版本、所有办公任务均加载同一文件；如只有项目级能力，须报告范围。[官方配置说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project)

源电脑不会远程自动安装目标 WorkBuddy；如果 Agent 无法操作上传界面，需要用户完成文件选择。实际技能目录由目标电脑的 WorkBuddy 确认，不猜固定用户名或其他 Agent 的目录。

## 依赖与离线核验

脚本需要 Python 3.10+，仅标准库，不需要新增 API Key、其他 Skill 或模型调用。正常 WorkBuddy 任务使用目标电脑现有账户/模型，包不迁移 Codex 订阅。缺 Python 时先报告，不附带系统软件安装器。

在实际技能目录执行：

```text
python -X utf8 -m unittest discover -s tests -v
python -X utf8 examples/demo.py
python -X utf8 scripts/verify_install.py
```

包已通过 27 项离线测试；从最终 ZIP 解压到含中文和空格的新目录后，完整测试、demo 和文件核验也通过。检查器只读；通过代表包内容可定位且一致，不能证明 WorkBuddy 已加载、已启用或在新会话自动触发。若有真实规则文件，可追加 `--rule-file <绝对路径>`，其检查仍只涉及规则文本。

## 经验归属与原生记忆

原生记忆提供历史线索；Experience Reuse 在行动时核对权威原文、版本/输入/环境、实际权限与证据。新经验优先保存在项目已有回执；没有合适归属时，才使用项目内 `.codebuddy/experience-reuse/experiences.json`。不修改生成的 WorkBuddy 记忆数据库，不默认改写全局 Skill，不跨项目传播私有经验。一次成功也不代替正式审核、规则晋级或发布授权。

## 目标机验收边界

本包尚未在另一台电脑的 WorkBuddy 中完成安装或双新会话测试。原 Codex 实测不能替代 WorkBuddy 验收。

- A：新建业务 Skill，首个本地任务直接成功并核验；提示词不点名 Experience Reuse、不要求“保存经验”，观察它是否自行保存方法、条件及证据。
- B：正常创建另一独立新会话，要求继续处理同项目的新输入；不点名任何 Skill、不提供经验路径，观察是否先实际读取 A 记录、核条件并采用，再核验新结果。

查看真实写入/读取与工具调用，不以最终回答“我已复用”作为证据。不代填经验，不将当前上下文模拟成两个独立会话。新会话加载仍是模型侧行为，不能承诺所有调用都被强制拦截。

## 保留与回滚

此版本 ZIP 按校验值标识；后续实质改包应另发版本。关闭技能并只移除本次添加的触发规则块可停用；保留其他配置和项目经验，不用整份旧配置覆盖后续修改。包内 `SOURCE.json` 记录源版本及宿主适配范围。

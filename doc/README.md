# 文档地图

当下目标、未完成事项与依赖见根 [PROGRESS.md](../PROGRESS.md)。本目录保存依据、安排和历史证据；前轮入口整合与取舍见[技能体系精简](40-版本实施方案/技能体系精简.md)，产品 UI 职责与来源见[能力比较](20-能力参考/product-ui/README.md)，实际执行与边界见[验证记录](40-版本实施方案/UI能力整合验证.json)。技能编写与入口校准的前轮结果见[审视记录](20-能力参考/prompt-audit/2026-10-06/README.md)。

可视化理解与比较的职责、来源和沉淀方法见[方法记录](20-能力参考/visual-understanding/README.md)，选择、执行与交付检查见[验证记录](40-版本实施方案/可视化理解与比较技能验证.json)。切换前的 UI 阶段状态保留在[历史快照](90-归档/阶段快照/2026-10-09-UI参考原位迭代.md)，当前技能合同仍以各 SKILL.md 为准。

本仓库的当前权威说明以各级 `README.md`（说明文档）与 `SKILL.md`（技能说明）为主：

1. 根 [`README.md`](../README.md)：项目定位、安装、公开边界。
2. [`../write/README.md`](../write/README.md)：写作工作流及其接力关系。
3. [`../code/README.md`](../code/README.md)：代码工作流及其接力关系。
4. [`../common/README.md`](../common/README.md)：通用 skill（智能体技能）的职责。
5. [`../spec/README.md`](../spec/README.md)：独立软件产物的现行产品与验收要求；当前包含 `507-rednote`。技能合同继续以各 SKILL.md 为准。
6. [`../write/507-ppt/references/design-system.md`](../write/507-ppt/references/design-system.md)：视觉幻灯片的语义组件、设计语言、视觉呈现、兼容矩阵与载体支持权威。
7. [`../write/507-video/references/production-contract.md`](../write/507-video/references/production-contract.md)：视频制作合同、素材清单与时间基准的当前约束。
8. [`../write/507-voiceover/README.md`](../write/507-voiceover/README.md)：本地配音、Voicebox REST 接入、模型选择与配音包约束。
9. 各 skill 目录的 `SKILL.md`：触发词、操作步骤、输入输出与限制；[507-ui](../code/507-ui/SKILL.md)承接产品界面的设计、范围内实现与实际操作验证，方法来源见[能力比较](20-能力参考/product-ui/README.md)。
10. [`../GLOSSARY.md`](../GLOSSARY.md)：定义本仓库稳定使用的项目语言。
11. [`决策档案/`](决策档案/README.md)：记录难逆转、缺少上下文会令人困惑且存在真实权衡的项目决策。
12. [`20-能力参考/`](20-能力参考/README.md)：固定版本的外部原件、调研证据、许可证与适用边界；当前包含 ZCode 原件、方法融合记录、提示词审计、技能编写与触发／读取审视、Apple项目指令的规则／证据判断，以及 paper-polish 表达润色方法的来源与融合验证；参考材料不替代各技能的现行合同。
13. [`项目启动与迁移标准`](../code/507-setup/references/project-standard.md)：面向选定代码项目的初始化、存量迁移和开工条件标准；由 setup、prd 等按职责消费。本页其它条目描述本仓库当前实际材料入口。

doc 按长期产品依据、架构说明、外部参考、规划及历史职责组织，只创建已有实际内容的分段。当前功能要求进入 spec，术语进入根 GLOSSARY；本次迁移已退出旧术语和 rednote 版本目录正文的维护。只有被取代、放弃或纯追溯材料进入 `90-归档/`，不能仅因工作完成而归档。

各 skill 内部的 `doc/`、`references/` 与 `README.md` 仅解释该 skill 的局部实现或方法，不覆盖其上级工作流边界。历史 Git（版本控制）记录用于追溯，不作为当前行为规范。

当前工作流定义与流程图分别维护在根 `README.md`、`common/README.md`、`code/README.md` 与 `write/README.md`；本文件只负责文档权威与阅读顺序，不复制完整工作流。

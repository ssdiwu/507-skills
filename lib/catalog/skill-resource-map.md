# 技能职责与共有库直接依赖

本表由现行入口合同、packages.json 身份登记和每技能 RESOURCES.md 资源声明生成。所有技能目录只保留职责、采用条件、交付标准、专用文字方法和元数据；执行代码、共有方法、React 组件、范例与运行工具只在 lib 存在一份。技能集合按 skills/ 与 lib/ 并列布局使用，禁止生成共有资源副本。

各列统计技能直接声明的文件数。每份文件按用途计入一类，合计为该技能的直接依赖总数。实际任务按需读取或执行。点击技能名查看分类明细。

| 技能 | 独有职责 | 方法 | 工具 | 界面组件 | 库务资料 | 合计 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| [skill-design](#skill-design) | 规划、创建或重构技能体系，审计技能包中的触发、读取与指令适用性，把任务经验和外部方法组织成技能、共有方法与工具，并完成获授权的文件和验证。 | 12 | 2 | 0 | 2 | 16 |
| [507-what](#507-what) | 定义要解决的问题、目标、范围与成功标准，承接初步设想、重新定义及关键取舍讨论。 | 9 | 0 | 0 | 1 | 10 |
| [507-work](#507-work) | 发现工作事项、梳理建议顺序并推进授权内可完成的工作，以已有消息、任务与过程资料为依据，一致更新工作状态或交回拟议结果。 | 6 | 11 | 4 | 2 | 23 |
| [507-why](#507-why) | 帮助认识陌生项目，主动调查用途、角色、代表路径、内部职责和当前实际情况；也解释概念、现象与机制，保留证据边界。 | 15 | 0 | 0 | 1 | 16 |
| [507-how](#507-how) | 根据目标与约束构造、比较和推敲产品、系统与工程方案，覆盖新产品、重设计及已有系统变更；连接操作、状态、数据、权限与结果，调查会改变方案的未知。 | 15 | 0 | 0 | 1 | 16 |
| [507-create](#507-create) | 承接创作、成文与修订请求，完成文章、方案、讲稿或局部改稿。 | 26 | 10 | 3 | 2 | 41 |
| [507-spec](#507-spec) | 整理唯一现行的行为与验收规格，承接已确认的软件需求或方案，也支持维护 PRD。 | 9 | 0 | 0 | 1 | 10 |
| [507-do](#507-do) | 按已明确的工程目标完成新增功能、故障修复、局部修改、指定测试或产品界面组件查找与复用。 | 13 | 5 | 6 | 3 | 27 |
| [507-clean](#507-clean) | 在指定模块内查找并清理死代码、重复逻辑和失效规则，保持已有功能，默认先只读列清单。 | 3 | 0 | 0 | 1 | 4 |
| [507-review](#507-review) | 检查现状是否满足已确认要求，只检查不修改。 | 9 | 1 | 0 | 1 | 11 |
| [507-issue](#507-issue) | 草拟、创建或维护可跟进的软件工单，保留调查证据并原位升级为可领取的执行任务。 | 6 | 0 | 0 | 1 | 7 |
| [507-coordinate](#507-coordinate) | 判断必要的工作拆分、依赖、执行所有权与结果接收，适用于已有工程、写作、研究或一般工作目标。 | 11 | 9 | 4 | 3 | 27 |
| [507-deliver](#507-deliver) | 为已完成工程范围准备 PR 表达、交付说明及版本结果，并按具体授权执行相应 Git 或发布动作；接续旧507-git引用时核当前职责与原条件。 | 8 | 2 | 0 | 2 | 12 |
| [507-retro](#507-retro) | 复盘已发生的工程工作，以实际尝试和结果提炼改进及重复任务的工具建议。 | 7 | 0 | 0 | 1 | 8 |
| [507-material](#507-material) | 整理指定资料，核清来源、身份、重复和支持范围；也可按明确请求组织已有知识入口。 | 7 | 0 | 0 | 1 | 8 |
| [507-adapt](#507-adapt) | 把成熟内容适配为目标受众、场景与载体中可用的作品，完成表达改写、信息安排和实际制作，保留作者判断、事实与来源。 | 16 | 10 | 4 | 2 | 32 |
| [507-setup](#507-setup) | 建立、迁移或只读核对项目工作依据，审计工作指令的失效与冲突，或维护 README、目录职责与文档导航。 | 4 | 2 | 0 | 2 | 8 |
| [507-product-map](#507-product-map) | 梳理指定产品功能的交互点与操作关系，把设计要求、实现依据和实际运行证据对到同一节点，生成可探索地图与范围差距。 | 4 | 7 | 4 | 2 | 17 |
| [507-plan](#507-plan) | 为承担当前任务的执行者安排如何交付结果，明确步骤、依赖、验证与恢复。 | 7 | 0 | 0 | 1 | 8 |
| [507-visualize](#507-visualize) | 把已有事实、机制、流程与方案组织成便于理解和判断的图、表与配套说明。 | 4 | 4 | 3 | 2 | 13 |
| [507-demo](#507-demo) | 制作产品界面的静态展示图、功能卡片或带光标的短动画，交付可编辑场景与目标实物。 | 8 | 4 | 4 | 4 | 20 |
| [507-domain](#507-domain) | 构建或校准项目领域概念、词义、边界与关系，用具体场景检验并按授权维护相关文档。 | 5 | 0 | 0 | 1 | 6 |
| [507-synthesize](#507-synthesize) | 围绕当前决策归纳已核对的访谈、反馈或问题记录，比较会改变处理方式的分组，交付可回查的判断、处理优先级和待查证据。 | 3 | 0 | 0 | 1 | 4 |
| [507-coach](#507-coach) | 陪用户练习判断。 | 0 | 0 | 0 | 1 | 1 |

## 统一分工

- create：负责作品内容和作者表达；呈现直接调用共有 React，复杂产品演示可按需采用 demo 的工作方法。
- adapt：负责受众、阅读关系和载体；直接调用共有 React，不读取或复制 demo 的运行资源。
- visualize：负责图的关系、单位、来源、未知与理解路径；图解组件直接调用共有 React。
- demo：负责产品识别、构图和动作编排；不拥有专属 kit、运行库或通用组件。
- work、coordinate、product-map：负责各自记录、关系与证据模型，展示层同样直接使用共有 React。
- do：负责真实产品行为，先复用目标产品组件；React依赖与构建适用且缺少对应控件时直接采用共有 ui，离线React场景也由共有入口导出。模拟展示不作为业务实现或验收。
- review：独立核职责、直接依赖、复制回归、实际效果与未覆盖；不修改受审内容。


## skill-design

[技能说明](../../skills/skill-design/SKILL.md) · [资源声明](../../skills/skill-design/RESOURCES.md)

### 方法（12）

- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/writing/clear-expression.md](../methods/writing/clear-expression.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/external-research.md](../methods/evidence-and-decisions/external-research.md)
- 指引 · [methods/collaboration/prompt-instruction-audit.md](../methods/collaboration/prompt-instruction-audit.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/collaboration/skill-entry-resolution.md](../methods/collaboration/skill-entry-resolution.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（2）

- 使用说明 · [components/tools/projections/library-view.md](../components/tools/projections/library-view.md)
- 执行文件 · [components/tools/projections/library_view.py](../components/tools/projections/library_view.py)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 登记与溯源 · [catalog/registry/skill-entry-index.md](../catalog/registry/skill-entry-index.md)

## 507-what

[技能说明](../../skills/507-what/SKILL.md) · [资源声明](../../skills/507-what/RESOURCES.md)

### 方法（9）

- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/writing/clear-expression.md](../methods/writing/clear-expression.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-work

[技能说明](../../skills/507-work/SKILL.md) · [资源声明](../../skills/507-work/RESOURCES.md)

### 方法（6）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/collaboration/task-coordination.md](../methods/collaboration/task-coordination.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（11）

- 使用说明 · [components/tools/checks/delivery-check.md](../components/tools/checks/delivery-check.md)
- 执行文件 · [components/tools/checks/delivery_check.py](../components/tools/checks/delivery_check.py)
- 执行文件 · [components/tools/export/react_export.py](../components/tools/export/react_export.py)
- 执行文件 · [components/tools/checks/state_diff.py](../components/tools/checks/state_diff.py)
- 使用说明 · [components/tools/projections/task-view.md](../components/tools/projections/task-view.md)
- 执行文件 · [components/tools/projections/task_view.py](../components/tools/projections/task_view.py)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 维护测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)
- 执行文件 · [components/tools/projections/work_view.py](../components/tools/projections/work_view.py)

### 界面组件（4）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

## 507-why

[技能说明](../../skills/507-why/SKILL.md) · [资源声明](../../skills/507-why/RESOURCES.md)

### 方法（15）

- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/engineering/architecture-candidates.md](../methods/engineering/architecture-candidates.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/writing/clear-expression.md](../methods/writing/clear-expression.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/writing/explanation-progression.md](../methods/writing/explanation-progression.md)
- 指引 · [methods/evidence-and-decisions/external-research.md](../methods/evidence-and-decisions/external-research.md)
- 指引 · [methods/design/media-study.md](../methods/design/media-study.md)
- 指引 · [methods/engineering/probe-lifecycle.md](../methods/engineering/probe-lifecycle.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/design/visual-understanding.md](../methods/design/visual-understanding.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-how

[技能说明](../../skills/507-how/SKILL.md) · [资源声明](../../skills/507-how/RESOURCES.md)

### 方法（15）

- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/engineering/architecture-candidates.md](../methods/engineering/architecture-candidates.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/engineering/behavior-preserving-change.md](../methods/engineering/behavior-preserving-change.md)
- 指引 · [methods/writing/clear-expression.md](../methods/writing/clear-expression.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/external-research.md](../methods/evidence-and-decisions/external-research.md)
- 指引 · [methods/engineering/interaction-map.md](../methods/engineering/interaction-map.md)
- 指引 · [methods/engineering/probe-lifecycle.md](../methods/engineering/probe-lifecycle.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/design/visual-understanding.md](../methods/design/visual-understanding.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-create

[技能说明](../../skills/507-create/SKILL.md) · [资源声明](../../skills/507-create/RESOURCES.md)

### 方法（26）

- 指引 · [methods/design/guides/apple-interaction.md](../methods/design/guides/apple-interaction.md)
- 指引 · [methods/design/guides/artifact-prompts.md](../methods/design/guides/artifact-prompts.md)
- 指引 · [methods/design/guides/containers-and-motion.md](../methods/design/guides/containers-and-motion.md)
- 指引 · [methods/design/guides/interaction-detail.md](../methods/design/guides/interaction-detail.md)
- 指引 · [methods/design/guides/target-design.md](../methods/design/guides/target-design.md)
- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/writing/artifact-contract.md](../methods/writing/artifact-contract.md)
- 指引 · [methods/design/artifact-rendering.md](../methods/design/artifact-rendering.md)
- 指引 · [methods/writing/author-and-source.md](../methods/writing/author-and-source.md)
- 指引 · [methods/writing/author-interview.md](../methods/writing/author-interview.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/writing/clear-expression.md](../methods/writing/clear-expression.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/writing/explanation-progression.md](../methods/writing/explanation-progression.md)
- 指引 · [methods/evidence-and-decisions/external-research.md](../methods/evidence-and-decisions/external-research.md)
- 指引 · [methods/engineering/interaction.md](../methods/engineering/interaction.md)
- 指引 · [methods/design/media-production.md](../methods/design/media-production.md)
- 指引 · [methods/design/media-study.md](../methods/design/media-study.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/collaboration/task-coordination.md](../methods/collaboration/task-coordination.md)
- 指引 · [methods/writing/title-promises.md](../methods/writing/title-promises.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/design/visual-direction.md](../methods/design/visual-direction.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（10）

- 使用说明 · [components/tools/export/artifact-receipt.md](../components/tools/export/artifact-receipt.md)
- 执行文件 · [components/tools/export/artifact_receipt.py](../components/tools/export/artifact_receipt.py)
- 执行文件 · [components/tools/checks/check_prose.py](../components/tools/checks/check_prose.py)
- 执行文件 · [components/tools/checks/check_spoken.py](../components/tools/checks/check_spoken.py)
- 使用说明 · [components/tools/export/media-adapters.md](../components/tools/export/media-adapters.md)
- 使用说明 · [components/tools/checks/text-checks.md](../components/tools/checks/text-checks.md)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 维护测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（3）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

## 507-spec

[技能说明](../../skills/507-spec/SKILL.md) · [资源声明](../../skills/507-spec/RESOURCES.md)

### 方法（9）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/engineering/engineering-evidence.md](../methods/engineering/engineering-evidence.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/engineering/interaction-map.md](../methods/engineering/interaction-map.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-do

[技能说明](../../skills/507-do/SKILL.md) · [资源声明](../../skills/507-do/RESOURCES.md)

### 方法（13）

- 指引 · [methods/design/guides/apple-interaction.md](../methods/design/guides/apple-interaction.md)
- 指引 · [methods/design/guides/containers-and-motion.md](../methods/design/guides/containers-and-motion.md)
- 指引 · [methods/design/guides/interaction-detail.md](../methods/design/guides/interaction-detail.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/engineering/behavior-preserving-change.md](../methods/engineering/behavior-preserving-change.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/engineering/engineering-evidence.md](../methods/engineering/engineering-evidence.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/engineering/interaction.md](../methods/engineering/interaction.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/design/visual-direction.md](../methods/design/visual-direction.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（5）

- 执行文件 · [components/tools/checks/check_run.py](../components/tools/checks/check_run.py)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 维护测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（6）

- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)
- 接入说明 · [components/visual/ui/README.md](../components/visual/ui/README.md)
- 实现与样式 · [components/visual/ui/index.tsx](../components/visual/ui/index.tsx)
- 实现与样式 · [components/visual/ui/ui.css](../components/visual/ui/ui.css)

### 库务资料（3）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)
- 登记与溯源 · [components/visual/ui/SOURCES.json](../components/visual/ui/SOURCES.json)

## 507-clean

[技能说明](../../skills/507-clean/SKILL.md) · [资源声明](../../skills/507-clean/RESOURCES.md)

### 方法（3）

- 指引 · [methods/engineering/behavior-preserving-change.md](../methods/engineering/behavior-preserving-change.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-review

[技能说明](../../skills/507-review/SKILL.md) · [资源声明](../../skills/507-review/RESOURCES.md)

### 方法（9）

- 指引 · [methods/writing/artifact-contract.md](../methods/writing/artifact-contract.md)
- 指引 · [methods/writing/author-and-source.md](../methods/writing/author-and-source.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/engineering/engineering-evidence.md](../methods/engineering/engineering-evidence.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/engineering/interaction-map.md](../methods/engineering/interaction-map.md)
- 指引 · [methods/collaboration/prompt-instruction-audit.md](../methods/collaboration/prompt-instruction-audit.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)

### 工具（1）

- 执行文件 · [components/tools/checks/check_run.py](../components/tools/checks/check_run.py)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-issue

[技能说明](../../skills/507-issue/SKILL.md) · [资源声明](../../skills/507-issue/RESOURCES.md)

### 方法（6）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-coordinate

[技能说明](../../skills/507-coordinate/SKILL.md) · [资源声明](../../skills/507-coordinate/RESOURCES.md)

### 方法（11）

- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/writing/clear-expression.md](../methods/writing/clear-expression.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/collaboration/skill-entry-resolution.md](../methods/collaboration/skill-entry-resolution.md)
- 指引 · [methods/collaboration/task-coordination.md](../methods/collaboration/task-coordination.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/design/visual-understanding.md](../methods/design/visual-understanding.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（9）

- 使用说明 · [components/tools/projections/library-view.md](../components/tools/projections/library-view.md)
- 执行文件 · [components/tools/projections/library_view.py](../components/tools/projections/library_view.py)
- 执行文件 · [components/tools/export/react_export.py](../components/tools/export/react_export.py)
- 使用说明 · [components/tools/projections/task-view.md](../components/tools/projections/task-view.md)
- 执行文件 · [components/tools/projections/task_view.py](../components/tools/projections/task_view.py)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 维护测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（4）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（3）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)
- 登记与溯源 · [catalog/registry/skill-entry-index.md](../catalog/registry/skill-entry-index.md)

## 507-deliver

[技能说明](../../skills/507-deliver/SKILL.md) · [资源声明](../../skills/507-deliver/RESOURCES.md)

### 方法（8）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/writing/clear-expression.md](../methods/writing/clear-expression.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/collaboration/skill-entry-resolution.md](../methods/collaboration/skill-entry-resolution.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（2）

- 使用说明 · [components/tools/projections/library-view.md](../components/tools/projections/library-view.md)
- 执行文件 · [components/tools/projections/library_view.py](../components/tools/projections/library_view.py)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 登记与溯源 · [catalog/registry/skill-entry-index.md](../catalog/registry/skill-entry-index.md)

## 507-retro

[技能说明](../../skills/507-retro/SKILL.md) · [资源声明](../../skills/507-retro/RESOURCES.md)

### 方法（7）

- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-material

[技能说明](../../skills/507-material/SKILL.md) · [资源声明](../../skills/507-material/RESOURCES.md)

### 方法（7）

- 指引 · [methods/writing/author-and-source.md](../methods/writing/author-and-source.md)
- 指引 · [methods/writing/author-interview.md](../methods/writing/author-interview.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/external-research.md](../methods/evidence-and-decisions/external-research.md)
- 指引 · [methods/design/media-study.md](../methods/design/media-study.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-adapt

[技能说明](../../skills/507-adapt/SKILL.md) · [资源声明](../../skills/507-adapt/RESOURCES.md)

### 方法（16）

- 指引 · [methods/design/guides/apple-interaction.md](../methods/design/guides/apple-interaction.md)
- 指引 · [methods/design/guides/artifact-prompts.md](../methods/design/guides/artifact-prompts.md)
- 指引 · [methods/design/guides/containers-and-motion.md](../methods/design/guides/containers-and-motion.md)
- 指引 · [methods/design/guides/interaction-detail.md](../methods/design/guides/interaction-detail.md)
- 指引 · [methods/design/guides/target-design.md](../methods/design/guides/target-design.md)
- 指引 · [methods/writing/artifact-contract.md](../methods/writing/artifact-contract.md)
- 指引 · [methods/design/artifact-rendering.md](../methods/design/artifact-rendering.md)
- 指引 · [methods/writing/author-and-source.md](../methods/writing/author-and-source.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/engineering/interaction.md](../methods/engineering/interaction.md)
- 指引 · [methods/design/media-production.md](../methods/design/media-production.md)
- 指引 · [methods/design/media-study.md](../methods/design/media-study.md)
- 指引 · [methods/writing/title-promises.md](../methods/writing/title-promises.md)
- 指引 · [methods/design/visual-direction.md](../methods/design/visual-direction.md)
- 指引 · [methods/design/visual-understanding.md](../methods/design/visual-understanding.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（10）

- 使用说明 · [components/tools/export/artifact-receipt.md](../components/tools/export/artifact-receipt.md)
- 执行文件 · [components/tools/export/artifact_receipt.py](../components/tools/export/artifact_receipt.py)
- 执行文件 · [components/tools/checks/check_prose.py](../components/tools/checks/check_prose.py)
- 执行文件 · [components/tools/checks/check_spoken.py](../components/tools/checks/check_spoken.py)
- 使用说明 · [components/tools/export/media-adapters.md](../components/tools/export/media-adapters.md)
- 使用说明 · [components/tools/checks/text-checks.md](../components/tools/checks/text-checks.md)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 维护测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（4）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

## 507-setup

[技能说明](../../skills/507-setup/SKILL.md) · [资源声明](../../skills/507-setup/RESOURCES.md)

### 方法（4）

- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/collaboration/prompt-instruction-audit.md](../methods/collaboration/prompt-instruction-audit.md)
- 指引 · [methods/collaboration/skill-entry-resolution.md](../methods/collaboration/skill-entry-resolution.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（2）

- 使用说明 · [components/tools/projections/library-view.md](../components/tools/projections/library-view.md)
- 执行文件 · [components/tools/projections/library_view.py](../components/tools/projections/library_view.py)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 登记与溯源 · [catalog/registry/skill-entry-index.md](../catalog/registry/skill-entry-index.md)

## 507-product-map

[技能说明](../../skills/507-product-map/SKILL.md) · [资源声明](../../skills/507-product-map/RESOURCES.md)

### 方法（4）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/engineering/interaction-map.md](../methods/engineering/interaction-map.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)

### 工具（7）

- 使用说明 · [components/tools/projections/product-map.md](../components/tools/projections/product-map.md)
- 执行文件 · [components/tools/projections/product_map.py](../components/tools/projections/product_map.py)
- 执行文件 · [components/tools/export/react_export.py](../components/tools/export/react_export.py)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 维护测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（4）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

## 507-plan

[技能说明](../../skills/507-plan/SKILL.md) · [资源声明](../../skills/507-plan/RESOURCES.md)

### 方法（7）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-visualize

[技能说明](../../skills/507-visualize/SKILL.md) · [资源声明](../../skills/507-visualize/RESOURCES.md)

### 方法（4）

- 指引 · [methods/design/artifact-rendering.md](../methods/design/artifact-rendering.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/design/visual-understanding.md](../methods/design/visual-understanding.md)

### 工具（4）

- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 维护测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（3）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

## 507-demo

[技能说明](../../skills/507-demo/SKILL.md) · [资源声明](../../skills/507-demo/RESOURCES.md)

### 方法（8）

- 指引 · [components/visual/references/choreography.md](../components/visual/references/choreography.md)
- 指引 · [components/visual/references/craft.md](../components/visual/references/craft.md)
- 指引 · [components/visual/references/framing.md](../components/visual/references/framing.md)
- 指引 · [components/visual/references/kit.md](../components/visual/references/kit.md)
- 指引 · [components/visual/references/motion.md](../components/visual/references/motion.md)
- 指引 · [components/visual/references/rehearse.md](../components/visual/references/rehearse.md)
- 指引 · [components/visual/references/review.md](../components/visual/references/review.md)
- 指引 · [methods/design/artifact-rendering.md](../methods/design/artifact-rendering.md)

### 工具（4）

- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 维护测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（4）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（4）

- 导航 · [README.md](../README.md)
- 登记与溯源 · [components/visual/LICENSE](../components/visual/LICENSE)
- 登记与溯源 · [components/visual/UPSTREAM.json](../components/visual/UPSTREAM.json)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

## 507-domain

[技能说明](../../skills/507-domain/SKILL.md) · [资源声明](../../skills/507-domain/RESOURCES.md)

### 方法（5）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-synthesize

[技能说明](../../skills/507-synthesize/SKILL.md) · [资源声明](../../skills/507-synthesize/RESOURCES.md)

### 方法（3）

- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-coach

[技能说明](../../skills/507-coach/SKILL.md) · [资源声明](../../skills/507-coach/RESOURCES.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

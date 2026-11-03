# 技能职责与共有库直接依赖

本表由现行入口合同、packages.json 身份登记和每技能 RESOURCES.md 资源声明生成。所有技能目录只保留职责、采用条件、交付标准、专用文字方法和元数据；执行代码、共有方法、React 组件、范例与运行工具只在 lib 存在一份。技能集合按 skills/ 与 lib/ 并列布局使用，禁止生成共有资源副本。

| 技能 | 独有职责 | 直接执行入口／运行依赖 | 共有方法 |
| --- | --- | --- | --- |
| [skill-design](../skills/skill-design/SKILL.md) | 规划、创建或重构技能体系，审计技能包中的触发、读取与指令适用性，把任务经验和外部方法组织成技能、共有方法与工具，并完成获授权的文件和验证。 | [library_view.py](components/library_view.py) | 12 份 |
| [507-what](../skills/507-what/SKILL.md) | 定义要解决的问题、目标、范围与成功标准，承接初步设想、重新定义及关键取舍讨论。 | 按条件读取共有方法，无执行工具 | 9 份 |
| [507-work](../skills/507-work/SKILL.md) | 发现工作事项、梳理建议顺序并推进授权内可完成的工作，以已有消息、任务与过程资料为依据，一致更新工作状态或交回拟议结果。 | [react_export.py](components/react_export.py)、[state_diff.py](components/state_diff.py)、[task_view.py](components/task_view.py)、[render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)、[work_view.py](components/work_view.py) | 6 份 |
| [507-why](../skills/507-why/SKILL.md) | 帮助认识陌生项目，主动调查用途、角色、代表路径、内部职责和当前实际情况；也解释概念、现象与机制，保留证据边界。 | 按条件读取共有方法，无执行工具 | 15 份 |
| [507-how](../skills/507-how/SKILL.md) | 根据目标与约束构造、比较和推敲产品、系统与工程方案，覆盖新产品、重设计及已有系统变更；连接操作、状态、数据、权限与结果，调查会改变方案的未知。 | 按条件读取共有方法，无执行工具 | 15 份 |
| [507-create](../skills/507-create/SKILL.md) | 承接创作、成文与修订请求，完成文章、方案、讲稿或局部改稿。 | [artifact_receipt.py](components/artifact_receipt.py)、[check_prose.py](components/check_prose.py)、[check_spoken.py](components/check_spoken.py)、[render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs) | 21 份 |
| [507-spec](../skills/507-spec/SKILL.md) | 整理唯一现行的行为与验收规格，承接已确认的软件需求或方案，也支持维护 PRD。 | 按条件读取共有方法，无执行工具 | 9 份 |
| [507-do](../skills/507-do/SKILL.md) | 按已明确的工程目标完成新增功能、故障修复、局部修改、指定测试或产品界面组件查找与复用。 | [check_run.py](components/check_run.py)、[render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs) | 10 份 |
| [507-clean](../skills/507-clean/SKILL.md) | 在指定模块内查找并清理死代码、重复逻辑和失效规则，保持已有功能，默认先只读列清单。 | 按条件读取共有方法，无执行工具 | 3 份 |
| [507-review](../skills/507-review/SKILL.md) | 检查现状是否满足已确认要求，只检查不修改。 | [check_run.py](components/check_run.py) | 9 份 |
| [507-issue](../skills/507-issue/SKILL.md) | 草拟、创建或维护可跟进的软件工单，保留调查证据并原位升级为可领取的执行任务。 | 按条件读取共有方法，无执行工具 | 6 份 |
| [507-coordinate](../skills/507-coordinate/SKILL.md) | 判断必要的工作拆分、依赖、执行所有权与结果接收，适用于已有工程、写作、研究或一般工作目标。 | [library_view.py](components/library_view.py)、[react_export.py](components/react_export.py)、[task_view.py](components/task_view.py)、[render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs) | 11 份 |
| [507-deliver](../skills/507-deliver/SKILL.md) | 为已完成工程范围准备 PR 表达、交付说明及版本结果，并按具体授权执行相应 Git 或发布动作；接续旧507-git引用时核当前职责与原条件。 | [library_view.py](components/library_view.py) | 8 份 |
| [507-retro](../skills/507-retro/SKILL.md) | 复盘已发生的工程工作，以实际尝试和结果提炼改进及重复任务的工具建议。 | 按条件读取共有方法，无执行工具 | 7 份 |
| [507-material](../skills/507-material/SKILL.md) | 整理指定资料，核清来源、身份、重复和支持范围；也可按明确请求组织已有知识入口。 | 按条件读取共有方法，无执行工具 | 7 份 |
| [507-adapt](../skills/507-adapt/SKILL.md) | 把成熟内容适配为目标受众、场景与载体中可用的作品，完成表达改写、信息安排和实际制作，保留作者判断、事实与来源。 | [artifact_receipt.py](components/artifact_receipt.py)、[check_prose.py](components/check_prose.py)、[check_spoken.py](components/check_spoken.py)、[render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs) | 11 份 |
| [507-setup](../skills/507-setup/SKILL.md) | 建立、迁移或只读核对项目工作依据，审计工作指令的失效与冲突，或维护 README、目录职责与文档导航。 | [library_view.py](components/library_view.py) | 4 份 |
| [507-product-map](../skills/507-product-map/SKILL.md) | 梳理指定产品功能的交互点与操作关系，把设计要求、实现依据和实际运行证据对到同一节点，生成可探索地图与范围差距。 | [product_map.py](components/product_map.py)、[react_export.py](components/react_export.py)、[render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs) | 4 份 |
| [507-plan](../skills/507-plan/SKILL.md) | 把已有目标与方向组织为可执行步骤、依赖、验证点、恢复办法和接续位置。 | 按条件读取共有方法，无执行工具 | 7 份 |
| [507-visualize](../skills/507-visualize/SKILL.md) | 把已有事实、机制、流程与方案组织成便于理解和判断的图、表与配套说明。 | [render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs) | 4 份 |
| [507-demo](../skills/507-demo/SKILL.md) | 制作产品界面的静态展示图、功能卡片或带光标的短动画，交付可编辑场景与目标实物。 | [render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs) | 1 份 |

## 统一分工

- create：负责作品内容和作者表达；呈现直接调用共有 React，复杂产品演示可按需采用 demo 的工作方法。
- adapt：负责受众、阅读关系和载体；直接调用共有 React，不读取或复制 demo 的运行资源。
- visualize：负责图的关系、单位、来源、未知与理解路径；图解组件直接调用共有 React。
- demo：负责产品识别、构图和动作编排；不拥有专属 kit、运行库或通用组件。
- work、coordinate、product-map：负责各自记录、关系与证据模型，展示层同样直接使用共有 React。
- do：负责真实产品行为，先复用目标产品组件；React依赖与构建适用且缺少对应控件时直接采用共有 ui，离线React场景也由共有入口导出。模拟展示不作为业务实现或验收。
- review：独立核职责、直接依赖、复制回归、实际效果与未覆盖；不修改受审内容。


## skill-design

[资源声明](../skills/skill-design/RESOURCES.md)

- [README.md](README.md)
- [components/library-view.md](components/library-view.md)
- [components/library_view.py](components/library_view.py)
- [methods/alternatives.md](methods/alternatives.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/clear-expression.md](methods/clear-expression.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/external-research.md](methods/external-research.md)
- [methods/prompt-instruction-audit.md](methods/prompt-instruction-audit.md)
- [methods/question-frontier.md](methods/question-frontier.md)
- [methods/skill-entry-resolution.md](methods/skill-entry-resolution.md)
- [methods/validation.md](methods/validation.md)
- [methods/work-records.md](methods/work-records.md)
- [registry/skill-entry-index.md](registry/skill-entry-index.md)

## 507-what

[资源声明](../skills/507-what/RESOURCES.md)

- [README.md](README.md)
- [methods/alternatives.md](methods/alternatives.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/clear-expression.md](methods/clear-expression.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/question-frontier.md](methods/question-frontier.md)
- [methods/validation.md](methods/validation.md)
- [methods/work-records.md](methods/work-records.md)

## 507-work

[资源声明](../skills/507-work/RESOURCES.md)

- [README.md](README.md)
- [components/react_export.py](components/react_export.py)
- [components/state_diff.py](components/state_diff.py)
- [components/task-view.md](components/task-view.md)
- [components/task_view.py](components/task_view.py)
- [components/visual-components.md](components/visual-components.md)
- [components/visual-runtime.md](components/visual-runtime.md)
- [components/visual-runtime/package.json](components/visual-runtime/package.json)
- [components/visual-runtime/scripts/render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)
- [components/work_view.py](components/work_view.py)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/task-coordination.md](methods/task-coordination.md)
- [methods/validation.md](methods/validation.md)
- [methods/work-records.md](methods/work-records.md)

## 507-why

[资源声明](../skills/507-why/RESOURCES.md)

- [README.md](README.md)
- [methods/alternatives.md](methods/alternatives.md)
- [methods/architecture-candidates.md](methods/architecture-candidates.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/clear-expression.md](methods/clear-expression.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/explanation-progression.md](methods/explanation-progression.md)
- [methods/external-research.md](methods/external-research.md)
- [methods/media-study.md](methods/media-study.md)
- [methods/probe-lifecycle.md](methods/probe-lifecycle.md)
- [methods/question-frontier.md](methods/question-frontier.md)
- [methods/validation.md](methods/validation.md)
- [methods/visual-understanding.md](methods/visual-understanding.md)
- [methods/work-records.md](methods/work-records.md)

## 507-how

[资源声明](../skills/507-how/RESOURCES.md)

- [README.md](README.md)
- [methods/alternatives.md](methods/alternatives.md)
- [methods/architecture-candidates.md](methods/architecture-candidates.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/behavior-preserving-change.md](methods/behavior-preserving-change.md)
- [methods/clear-expression.md](methods/clear-expression.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/external-research.md](methods/external-research.md)
- [methods/interaction-map.md](methods/interaction-map.md)
- [methods/probe-lifecycle.md](methods/probe-lifecycle.md)
- [methods/question-frontier.md](methods/question-frontier.md)
- [methods/validation.md](methods/validation.md)
- [methods/visual-understanding.md](methods/visual-understanding.md)
- [methods/work-records.md](methods/work-records.md)

## 507-create

[资源声明](../skills/507-create/RESOURCES.md)

- [README.md](README.md)
- [components/artifact-receipt.md](components/artifact-receipt.md)
- [components/artifact_receipt.py](components/artifact_receipt.py)
- [components/check_prose.py](components/check_prose.py)
- [components/check_spoken.py](components/check_spoken.py)
- [components/media-adapters.md](components/media-adapters.md)
- [components/text-checks.md](components/text-checks.md)
- [components/visual-components.md](components/visual-components.md)
- [components/visual-runtime/package.json](components/visual-runtime/package.json)
- [components/visual-runtime/scripts/render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)
- [design/apple-interaction.md](design/apple-interaction.md)
- [design/artifact-prompts.md](design/artifact-prompts.md)
- [design/containers-and-motion.md](design/containers-and-motion.md)
- [design/interaction-detail.md](design/interaction-detail.md)
- [design/target-design.md](design/target-design.md)
- [methods/alternatives.md](methods/alternatives.md)
- [methods/artifact-contract.md](methods/artifact-contract.md)
- [methods/artifact-rendering.md](methods/artifact-rendering.md)
- [methods/author-and-source.md](methods/author-and-source.md)
- [methods/author-interview.md](methods/author-interview.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/clear-expression.md](methods/clear-expression.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/explanation-progression.md](methods/explanation-progression.md)
- [methods/external-research.md](methods/external-research.md)
- [methods/interaction.md](methods/interaction.md)
- [methods/media-production.md](methods/media-production.md)
- [methods/media-study.md](methods/media-study.md)
- [methods/question-frontier.md](methods/question-frontier.md)
- [methods/task-coordination.md](methods/task-coordination.md)
- [methods/title-promises.md](methods/title-promises.md)
- [methods/validation.md](methods/validation.md)
- [methods/visual-direction.md](methods/visual-direction.md)
- [methods/work-records.md](methods/work-records.md)

## 507-spec

[资源声明](../skills/507-spec/RESOURCES.md)

- [README.md](README.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/engineering-evidence.md](methods/engineering-evidence.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/interaction-map.md](methods/interaction-map.md)
- [methods/question-frontier.md](methods/question-frontier.md)
- [methods/validation.md](methods/validation.md)
- [methods/work-records.md](methods/work-records.md)

## 507-do

[资源声明](../skills/507-do/RESOURCES.md)

- [README.md](README.md)
- [components/check_run.py](components/check_run.py)
- [components/visual-runtime.md](components/visual-runtime.md)
- [components/visual-runtime/package.json](components/visual-runtime/package.json)
- [components/visual-runtime/scripts/render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)
- [components/visual-runtime/ui/README.md](components/visual-runtime/ui/README.md)
- [components/visual-runtime/ui/SOURCES.json](components/visual-runtime/ui/SOURCES.json)
- [components/visual-runtime/ui/index.tsx](components/visual-runtime/ui/index.tsx)
- [components/visual-runtime/ui/ui.css](components/visual-runtime/ui/ui.css)
- [design/apple-interaction.md](design/apple-interaction.md)
- [design/containers-and-motion.md](design/containers-and-motion.md)
- [design/interaction-detail.md](design/interaction-detail.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/behavior-preserving-change.md](methods/behavior-preserving-change.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/engineering-evidence.md](methods/engineering-evidence.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/interaction.md](methods/interaction.md)
- [methods/validation.md](methods/validation.md)
- [methods/visual-direction.md](methods/visual-direction.md)
- [methods/work-records.md](methods/work-records.md)

## 507-clean

[资源声明](../skills/507-clean/RESOURCES.md)

- [README.md](README.md)
- [methods/behavior-preserving-change.md](methods/behavior-preserving-change.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/work-records.md](methods/work-records.md)

## 507-review

[资源声明](../skills/507-review/RESOURCES.md)

- [README.md](README.md)
- [components/check_run.py](components/check_run.py)
- [methods/artifact-contract.md](methods/artifact-contract.md)
- [methods/author-and-source.md](methods/author-and-source.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/engineering-evidence.md](methods/engineering-evidence.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/interaction-map.md](methods/interaction-map.md)
- [methods/prompt-instruction-audit.md](methods/prompt-instruction-audit.md)
- [methods/validation.md](methods/validation.md)

## 507-issue

[资源声明](../skills/507-issue/RESOURCES.md)

- [README.md](README.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/validation.md](methods/validation.md)
- [methods/work-records.md](methods/work-records.md)

## 507-coordinate

[资源声明](../skills/507-coordinate/RESOURCES.md)

- [README.md](README.md)
- [components/library-view.md](components/library-view.md)
- [components/library_view.py](components/library_view.py)
- [components/react_export.py](components/react_export.py)
- [components/task-view.md](components/task-view.md)
- [components/task_view.py](components/task_view.py)
- [components/visual-components.md](components/visual-components.md)
- [components/visual-runtime.md](components/visual-runtime.md)
- [components/visual-runtime/package.json](components/visual-runtime/package.json)
- [components/visual-runtime/scripts/render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)
- [methods/alternatives.md](methods/alternatives.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/clear-expression.md](methods/clear-expression.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/skill-entry-resolution.md](methods/skill-entry-resolution.md)
- [methods/task-coordination.md](methods/task-coordination.md)
- [methods/validation.md](methods/validation.md)
- [methods/visual-understanding.md](methods/visual-understanding.md)
- [methods/work-records.md](methods/work-records.md)
- [registry/skill-entry-index.md](registry/skill-entry-index.md)

## 507-deliver

[资源声明](../skills/507-deliver/RESOURCES.md)

- [README.md](README.md)
- [components/library-view.md](components/library-view.md)
- [components/library_view.py](components/library_view.py)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/clear-expression.md](methods/clear-expression.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/skill-entry-resolution.md](methods/skill-entry-resolution.md)
- [methods/validation.md](methods/validation.md)
- [methods/work-records.md](methods/work-records.md)
- [registry/skill-entry-index.md](registry/skill-entry-index.md)

## 507-retro

[资源声明](../skills/507-retro/RESOURCES.md)

- [README.md](README.md)
- [methods/alternatives.md](methods/alternatives.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/validation.md](methods/validation.md)
- [methods/work-records.md](methods/work-records.md)

## 507-material

[资源声明](../skills/507-material/RESOURCES.md)

- [README.md](README.md)
- [methods/author-and-source.md](methods/author-and-source.md)
- [methods/author-interview.md](methods/author-interview.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/external-research.md](methods/external-research.md)
- [methods/media-study.md](methods/media-study.md)
- [methods/work-records.md](methods/work-records.md)

## 507-adapt

[资源声明](../skills/507-adapt/RESOURCES.md)

- [README.md](README.md)
- [components/artifact-receipt.md](components/artifact-receipt.md)
- [components/artifact_receipt.py](components/artifact_receipt.py)
- [components/check_prose.py](components/check_prose.py)
- [components/check_spoken.py](components/check_spoken.py)
- [components/media-adapters.md](components/media-adapters.md)
- [components/text-checks.md](components/text-checks.md)
- [components/visual-components.md](components/visual-components.md)
- [components/visual-runtime.md](components/visual-runtime.md)
- [components/visual-runtime/package.json](components/visual-runtime/package.json)
- [components/visual-runtime/scripts/render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)
- [design/apple-interaction.md](design/apple-interaction.md)
- [design/artifact-prompts.md](design/artifact-prompts.md)
- [design/containers-and-motion.md](design/containers-and-motion.md)
- [design/interaction-detail.md](design/interaction-detail.md)
- [design/target-design.md](design/target-design.md)
- [methods/artifact-contract.md](methods/artifact-contract.md)
- [methods/artifact-rendering.md](methods/artifact-rendering.md)
- [methods/author-and-source.md](methods/author-and-source.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/interaction.md](methods/interaction.md)
- [methods/media-production.md](methods/media-production.md)
- [methods/media-study.md](methods/media-study.md)
- [methods/title-promises.md](methods/title-promises.md)
- [methods/visual-direction.md](methods/visual-direction.md)
- [methods/visual-understanding.md](methods/visual-understanding.md)
- [methods/work-records.md](methods/work-records.md)

## 507-setup

[资源声明](../skills/507-setup/RESOURCES.md)

- [README.md](README.md)
- [components/library-view.md](components/library-view.md)
- [components/library_view.py](components/library_view.py)
- [methods/continuation.md](methods/continuation.md)
- [methods/prompt-instruction-audit.md](methods/prompt-instruction-audit.md)
- [methods/skill-entry-resolution.md](methods/skill-entry-resolution.md)
- [methods/work-records.md](methods/work-records.md)
- [registry/skill-entry-index.md](registry/skill-entry-index.md)

## 507-product-map

[资源声明](../skills/507-product-map/RESOURCES.md)

- [README.md](README.md)
- [components/product-map.md](components/product-map.md)
- [components/product_map.py](components/product_map.py)
- [components/react_export.py](components/react_export.py)
- [components/visual-components.md](components/visual-components.md)
- [components/visual-runtime.md](components/visual-runtime.md)
- [components/visual-runtime/package.json](components/visual-runtime/package.json)
- [components/visual-runtime/scripts/render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/interaction-map.md](methods/interaction-map.md)
- [methods/validation.md](methods/validation.md)

## 507-plan

[资源声明](../skills/507-plan/RESOURCES.md)

- [README.md](README.md)
- [methods/authority-and-return.md](methods/authority-and-return.md)
- [methods/continuation.md](methods/continuation.md)
- [methods/decision-ownership.md](methods/decision-ownership.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/question-frontier.md](methods/question-frontier.md)
- [methods/validation.md](methods/validation.md)
- [methods/work-records.md](methods/work-records.md)

## 507-visualize

[资源声明](../skills/507-visualize/RESOURCES.md)

- [README.md](README.md)
- [components/visual-components.md](components/visual-components.md)
- [components/visual-runtime/package.json](components/visual-runtime/package.json)
- [components/visual-runtime/scripts/render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)
- [methods/artifact-rendering.md](methods/artifact-rendering.md)
- [methods/evidence.md](methods/evidence.md)
- [methods/validation.md](methods/validation.md)
- [methods/visual-understanding.md](methods/visual-understanding.md)

## 507-demo

[资源声明](../skills/507-demo/RESOURCES.md)

- [README.md](README.md)
- [components/visual-components.md](components/visual-components.md)
- [components/visual-runtime.md](components/visual-runtime.md)
- [components/visual-runtime/LICENSE](components/visual-runtime/LICENSE)
- [components/visual-runtime/UPSTREAM.json](components/visual-runtime/UPSTREAM.json)
- [components/visual-runtime/package.json](components/visual-runtime/package.json)
- [components/visual-runtime/references/choreography.md](components/visual-runtime/references/choreography.md)
- [components/visual-runtime/references/craft.md](components/visual-runtime/references/craft.md)
- [components/visual-runtime/references/framing.md](components/visual-runtime/references/framing.md)
- [components/visual-runtime/references/kit.md](components/visual-runtime/references/kit.md)
- [components/visual-runtime/references/motion.md](components/visual-runtime/references/motion.md)
- [components/visual-runtime/references/rehearse.md](components/visual-runtime/references/rehearse.md)
- [components/visual-runtime/references/review.md](components/visual-runtime/references/review.md)
- [components/visual-runtime/scripts/render-artifact.mjs](components/visual-runtime/scripts/render-artifact.mjs)
- [methods/artifact-rendering.md](methods/artifact-rendering.md)

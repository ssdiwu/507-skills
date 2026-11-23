# 技能职责与共有库直接依赖

本表由现行入口合同、packages.json 身份登记和每技能 RESOURCES.md 资源声明生成。所有技能目录只保留职责、采用条件、交付标准、专用文字方法和元数据；执行代码、共有方法、React 组件、范例与运行工具只在 lib 存在一份。技能集合按 skills/ 与 lib/ 并列布局使用，禁止生成共有资源副本。

各列按用途统计声明文件。工具列统计交付工具，库维护测试列标明维护共有库时需要回归的技能。每项声明在合计中只计一次。点击技能名查看明细。

| 技能 | 独有职责 | 方法 | 工具 | 界面组件 | 库务资料 | 库维护测试 | 合计 |
| --- | --- |  ---: | ---: | ---: | ---: | ---: | ---: |
| [507-skill](#507-skill) | 规划、编写、重构或审计技能体系与共有资源。 | 12 | 3 | 0 | 3 | 1 | 19 |
| [507-what](#507-what) | 定义要解决的问题、目标、范围与关键取舍。 | 9 | 0 | 0 | 1 | 0 | 10 |
| [507-track](#507-track) | 发现并推进待办事项，接续已有工作的约定和交付。 | 7 | 10 | 4 | 2 | 1 | 24 |
| [507-explain](#507-explain) | 只读调查陌生项目，解释现有代码或机制怎样运作、为何如此。 | 15 | 0 | 0 | 1 | 0 | 16 |
| [507-design](#507-design) | 在目标与约束下构造新方案或已有系统的变更路径。 | 15 | 0 | 0 | 1 | 0 | 16 |
| [507-create](#507-create) | 推敲文章、方案和讲稿的主线，校准作者口吻，完成写作或改稿。 | 26 | 6 | 0 | 1 | 0 | 33 |
| [507-behavior-spec](#507-behavior-spec) | 整理唯一现行的软件行为要求与验收规格。 | 9 | 0 | 0 | 1 | 0 | 10 |
| [507-build](#507-build) | 按需求写代码开发功能，复现并修复故障，用原操作和测试验证结果。 | 13 | 4 | 3 | 2 | 1 | 23 |
| [507-clean](#507-clean) | 清理指定模块的死代码、重复逻辑和失效规则。 | 3 | 0 | 0 | 1 | 0 | 4 |
| [507-peer-review](#507-peer-review) | 由未参与实施的人只读审查指定交付，核对已确认要求、质量风险和实际证据。 | 9 | 1 | 0 | 1 | 0 | 11 |
| [507-work-issue](#507-work-issue) | 起草或维护可跟进的软件工单，把调查记录原位升级为可领取的执行任务。 | 6 | 0 | 0 | 1 | 0 | 7 |
| [507-task-dispatch](#507-task-dispatch) | 拆分多执行者的工作，隔离写入范围，接收并验证组合结果。 | 12 | 8 | 4 | 3 | 1 | 28 |
| [507-version-deliver](#507-version-deliver) | 准备版本交付与 PR 说明，跟进评审评论并读回已授权动作的结果。 | 8 | 2 | 0 | 2 | 0 | 12 |
| [507-work-retro](#507-work-retro) | 复盘已发生的工程尝试与重复摩擦，提炼有依据的防复发措施或工具化建议。 | 7 | 0 | 0 | 1 | 0 | 8 |
| [507-source-material](#507-source-material) | 核清指定资料的来源、身份、重复与支持范围，或按请求组织已有知识入口。 | 7 | 0 | 0 | 1 | 0 | 8 |
| [507-adapt](#507-adapt) | 把成熟内容改写并制作成适合目标受众与载体的作品。 | 16 | 8 | 4 | 2 | 1 | 31 |
| [507-setup](#507-setup) | 建立或维护项目工作依据、README 和文档阅读导航。 | 4 | 2 | 0 | 2 | 0 | 8 |
| [507-audit](#507-audit) | 盘点项目现行规则和已有检查，把能由机器可靠判断的要求落实为静态检查、测试或持续集成门禁。 | 1 | 0 | 0 | 1 | 0 | 2 |
| [507-product-map](#507-product-map) | 梳理指定产品功能的交互点及其关系，把设计、实现和实际运行证据对到同一节点。 | 5 | 6 | 4 | 2 | 1 | 18 |
| [507-step-plan](#507-step-plan) | 为当前任务的执行者安排实施步骤、依赖、验证点和恢复办法。 | 7 | 0 | 0 | 1 | 0 | 8 |
| [507-visual-explain](#507-visual-explain) | 用状态图、时序图、关系图或同条件对比表讲清复杂机制与差异。 | 5 | 3 | 3 | 2 | 1 | 14 |
| [507-ui-demo](#507-ui-demo) | 制作产品界面的静态功能卡片或带光标的模拟操作短动画。 | 8 | 4 | 4 | 4 | 1 | 21 |
| [507-domain-model](#507-domain-model) | 构建或校准领域概念、词义边界与关系。 | 5 | 0 | 0 | 1 | 0 | 6 |
| [507-case-synthesis](#507-case-synthesis) | 围绕当前决策，去重归纳多份访谈、反馈或问题记录。 | 3 | 0 | 0 | 1 | 0 | 4 |

## 统一分工

- create 负责作品内容和作者表达，adapt 负责受众与载体，visual-explain 负责图解关系与理解路径。新建独立阅读页采用[阅读页方法](../methods/design/reading-page.md)，修改已有页面优先复用项目组件。
- ui-demo 负责产品识别、构图和动作编排。
- track 和 task-dispatch 校验过程记录，再按[任务页方法](../methods/design/task-page.md)组织页面。product-map 校验交互与证据记录，再按[地图页方法](../methods/design/product-map-page.md)组织页面。共有 React 渲染器继续承接已有生成页。
- build 负责真实产品行为，按目标项目和本次参考选择界面实现。
- peer-review 独立核对职责、直接依赖、实际效果与未覆盖范围。


## 507-skill

[技能说明](../../skills/507-skill/SKILL.md) · [资源声明](../../skills/507-skill/RESOURCES.md)

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

### 工具（3）

- 使用说明 · [components/tools/projections/library-view.md](../components/tools/projections/library-view.md)
- 执行文件 · [components/tools/projections/library_view.py](../components/tools/projections/library_view.py)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 库务资料（3）

- 导航 · [README.md](../README.md)
- 登记与溯源 · [catalog/registry/library-map.json](../catalog/registry/library-map.json)
- 登记与溯源 · [catalog/registry/skill-entry-index.md](../catalog/registry/skill-entry-index.md)

### 库维护测试（1）

- 回归测试 · [components/visual/scripts/ui.test.mjs](../components/visual/scripts/ui.test.mjs)

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

## 507-track

[技能说明](../../skills/507-track/SKILL.md) · [资源声明](../../skills/507-track/RESOURCES.md)

### 方法（7）

- 指引 · [methods/design/task-page.md](../methods/design/task-page.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/collaboration/task-coordination.md](../methods/collaboration/task-coordination.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（10）

- 使用说明 · [components/tools/checks/delivery-check.md](../components/tools/checks/delivery-check.md)
- 执行文件 · [components/tools/checks/delivery_check.py](../components/tools/checks/delivery_check.py)
- 执行文件 · [components/tools/export/react_export.py](../components/tools/export/react_export.py)
- 执行文件 · [components/tools/checks/state_diff.py](../components/tools/checks/state_diff.py)
- 使用说明 · [components/tools/projections/task-view.md](../components/tools/projections/task-view.md)
- 执行文件 · [components/tools/projections/task_view.py](../components/tools/projections/task_view.py)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
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

### 库维护测试（1）

- 回归测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)

## 507-explain

[技能说明](../../skills/507-explain/SKILL.md) · [资源声明](../../skills/507-explain/RESOURCES.md)

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

## 507-design

[技能说明](../../skills/507-design/SKILL.md) · [资源声明](../../skills/507-design/RESOURCES.md)

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
- 指引 · [methods/design/reading-page.md](../methods/design/reading-page.md)
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

### 工具（6）

- 使用说明 · [components/tools/export/artifact-receipt.md](../components/tools/export/artifact-receipt.md)
- 执行文件 · [components/tools/export/artifact_receipt.py](../components/tools/export/artifact_receipt.py)
- 执行文件 · [components/tools/checks/check_prose.py](../components/tools/checks/check_prose.py)
- 执行文件 · [components/tools/checks/check_spoken.py](../components/tools/checks/check_spoken.py)
- 使用说明 · [components/tools/export/media-adapters.md](../components/tools/export/media-adapters.md)
- 使用说明 · [components/tools/checks/text-checks.md](../components/tools/checks/text-checks.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-behavior-spec

[技能说明](../../skills/507-behavior-spec/SKILL.md) · [资源声明](../../skills/507-behavior-spec/RESOURCES.md)

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

## 507-build

[技能说明](../../skills/507-build/SKILL.md) · [资源声明](../../skills/507-build/RESOURCES.md)

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

### 工具（4）

- 执行文件 · [components/tools/checks/check_run.py](../components/tools/checks/check_run.py)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（3）

- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

### 库维护测试（1）

- 回归测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)

## 507-clean

[技能说明](../../skills/507-clean/SKILL.md) · [资源声明](../../skills/507-clean/RESOURCES.md)

### 方法（3）

- 指引 · [methods/engineering/behavior-preserving-change.md](../methods/engineering/behavior-preserving-change.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-peer-review

[技能说明](../../skills/507-peer-review/SKILL.md) · [资源声明](../../skills/507-peer-review/RESOURCES.md)

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

## 507-work-issue

[技能说明](../../skills/507-work-issue/SKILL.md) · [资源声明](../../skills/507-work-issue/RESOURCES.md)

### 方法（6）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-task-dispatch

[技能说明](../../skills/507-task-dispatch/SKILL.md) · [资源声明](../../skills/507-task-dispatch/RESOURCES.md)

### 方法（12）

- 指引 · [methods/design/task-page.md](../methods/design/task-page.md)
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

### 工具（8）

- 使用说明 · [components/tools/projections/library-view.md](../components/tools/projections/library-view.md)
- 执行文件 · [components/tools/projections/library_view.py](../components/tools/projections/library_view.py)
- 执行文件 · [components/tools/export/react_export.py](../components/tools/export/react_export.py)
- 使用说明 · [components/tools/projections/task-view.md](../components/tools/projections/task-view.md)
- 执行文件 · [components/tools/projections/task_view.py](../components/tools/projections/task_view.py)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
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

### 库维护测试（1）

- 回归测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)

## 507-version-deliver

[技能说明](../../skills/507-version-deliver/SKILL.md) · [资源声明](../../skills/507-version-deliver/RESOURCES.md)

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

## 507-work-retro

[技能说明](../../skills/507-work-retro/SKILL.md) · [资源声明](../../skills/507-work-retro/RESOURCES.md)

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

## 507-source-material

[技能说明](../../skills/507-source-material/SKILL.md) · [资源声明](../../skills/507-source-material/RESOURCES.md)

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
- 指引 · [methods/design/reading-page.md](../methods/design/reading-page.md)
- 指引 · [methods/writing/author-and-source.md](../methods/writing/author-and-source.md)
- 指引 · [methods/collaboration/continuation.md](../methods/collaboration/continuation.md)
- 指引 · [methods/engineering/interaction.md](../methods/engineering/interaction.md)
- 指引 · [methods/design/media-production.md](../methods/design/media-production.md)
- 指引 · [methods/design/media-study.md](../methods/design/media-study.md)
- 指引 · [methods/writing/title-promises.md](../methods/writing/title-promises.md)
- 指引 · [methods/design/visual-direction.md](../methods/design/visual-direction.md)
- 指引 · [methods/design/visual-understanding.md](../methods/design/visual-understanding.md)
- 指引 · [methods/collaboration/work-records.md](../methods/collaboration/work-records.md)

### 工具（8）

- 使用说明 · [components/tools/export/artifact-receipt.md](../components/tools/export/artifact-receipt.md)
- 执行文件 · [components/tools/export/artifact_receipt.py](../components/tools/export/artifact_receipt.py)
- 执行文件 · [components/tools/checks/check_prose.py](../components/tools/checks/check_prose.py)
- 执行文件 · [components/tools/checks/check_spoken.py](../components/tools/checks/check_spoken.py)
- 使用说明 · [components/tools/export/media-adapters.md](../components/tools/export/media-adapters.md)
- 使用说明 · [components/tools/checks/text-checks.md](../components/tools/checks/text-checks.md)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)

### 界面组件（4）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

### 库维护测试（1）

- 回归测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)

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

## 507-audit

[技能说明](../../skills/507-audit/SKILL.md) · [资源声明](../../skills/507-audit/RESOURCES.md)

### 方法（1）

- 指引 · [methods/engineering/engineering-evidence.md](../methods/engineering/engineering-evidence.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-product-map

[技能说明](../../skills/507-product-map/SKILL.md) · [资源声明](../../skills/507-product-map/RESOURCES.md)

### 方法（5）

- 指引 · [methods/design/product-map-page.md](../methods/design/product-map-page.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/engineering/interaction-map.md](../methods/engineering/interaction-map.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)

### 工具（6）

- 使用说明 · [components/tools/projections/product-map.md](../components/tools/projections/product-map.md)
- 执行文件 · [components/tools/projections/product_map.py](../components/tools/projections/product_map.py)
- 执行文件 · [components/tools/export/react_export.py](../components/tools/export/react_export.py)
- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（4）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 接入说明 · [components/visual/visual-runtime.md](../components/visual/visual-runtime.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

### 库维护测试（1）

- 回归测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)

## 507-step-plan

[技能说明](../../skills/507-step-plan/SKILL.md) · [资源声明](../../skills/507-step-plan/RESOURCES.md)

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

## 507-visual-explain

[技能说明](../../skills/507-visual-explain/SKILL.md) · [资源声明](../../skills/507-visual-explain/RESOURCES.md)

### 方法（5）

- 指引 · [methods/design/artifact-rendering.md](../methods/design/artifact-rendering.md)
- 指引 · [methods/design/reading-page.md](../methods/design/reading-page.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)
- 指引 · [methods/design/visual-understanding.md](../methods/design/visual-understanding.md)

### 工具（3）

- 运行配置 · [components/visual/package.json](../components/visual/package.json)
- 执行文件 · [components/visual/scripts/component-library.mjs](../components/visual/scripts/component-library.mjs)
- 执行文件 · [components/visual/scripts/render-artifact.mjs](../components/visual/scripts/render-artifact.mjs)

### 界面组件（3）

- 接入说明 · [components/visual/visual-components.md](../components/visual/visual-components.md)
- 示例 · [components/visual/scenes/examples/record-browser/index.tsx](../components/visual/scenes/examples/record-browser/index.tsx)
- 示例 · [components/visual/scenes/examples/record-browser/records.css](../components/visual/scenes/examples/record-browser/records.css)

### 库务资料（2）

- 导航 · [README.md](../README.md)
- 导航 · [components/visual/catalog.json](../components/visual/catalog.json)

### 库维护测试（1）

- 回归测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)

## 507-ui-demo

[技能说明](../../skills/507-ui-demo/SKILL.md) · [资源声明](../../skills/507-ui-demo/RESOURCES.md)

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
- 执行文件 · [components/visual/scripts/film.mjs](../components/visual/scripts/film.mjs)
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

### 库维护测试（1）

- 回归测试 · [components/visual/scripts/component-library.test.mjs](../components/visual/scripts/component-library.test.mjs)

## 507-domain-model

[技能说明](../../skills/507-domain-model/SKILL.md) · [资源声明](../../skills/507-domain-model/RESOURCES.md)

### 方法（5）

- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/evidence-and-decisions/decision-ownership.md](../methods/evidence-and-decisions/decision-ownership.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)
- 指引 · [methods/evidence-and-decisions/question-frontier.md](../methods/evidence-and-decisions/question-frontier.md)
- 指引 · [methods/evidence-and-decisions/validation.md](../methods/evidence-and-decisions/validation.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

## 507-case-synthesis

[技能说明](../../skills/507-case-synthesis/SKILL.md) · [资源声明](../../skills/507-case-synthesis/RESOURCES.md)

### 方法（3）

- 指引 · [methods/evidence-and-decisions/alternatives.md](../methods/evidence-and-decisions/alternatives.md)
- 指引 · [methods/evidence-and-decisions/authority-and-return.md](../methods/evidence-and-decisions/authority-and-return.md)
- 指引 · [methods/evidence-and-decisions/evidence.md](../methods/evidence-and-decisions/evidence.md)

### 库务资料（1）

- 导航 · [README.md](../README.md)

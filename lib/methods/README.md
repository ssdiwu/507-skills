# 共有方法

| 工作需要 | 方法所在目录 |
| --- | --- |
| 来源、决定、反证与验收 | `evidence-and-decisions/` |
| 工程行为、架构与原型验证 | `engineering/` |
| 协作、记录和中断后接续 | `collaboration/` |
| 作者、内容与表达 | `writing/` |
| 呈现方式、交互与设计参考 | [设计与呈现](design/README.md) |

本目录的方法按条件提供判断与工作做法，没有独立技能入口。消费者与采用条件以[资源登记](../catalog/catalog.json)为准；专用方法留在各技能包内。脚本和工具说明见[components](../components/README.md)，设计参考见[design](design/README.md)。

| 方法 | 当前使用者 |
| --- | --- |
| [事实、来源与工作基线](evidence-and-decisions/evidence.md) | skill-design, 507-what, 507-work, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-review, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-material, 507-product-map, 507-plan, 507-visualize |
| [目标、边界与决定归属](evidence-and-decisions/decision-ownership.md) | skill-design, 507-what, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-plan |
| [信息缺口与问题依赖](evidence-and-decisions/question-frontier.md) | skill-design, 507-what, 507-why, 507-how, 507-create, 507-spec, 507-plan |
| [真实候选、反证与代价](evidence-and-decisions/alternatives.md) | skill-design, 507-what, 507-why, 507-how, 507-create, 507-coordinate, 507-retro |
| [可观察验收与相称验证](evidence-and-decisions/validation.md) | skill-design, 507-what, 507-work, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-review, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-product-map, 507-plan, 507-visualize |
| [当前权威、冲突与返回](evidence-and-decisions/authority-and-return.md) | skill-design, 507-what, 507-work, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-review, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-product-map, 507-plan |
| [最小清晰表达与关系类型](writing/clear-expression.md) | skill-design, 507-what, 507-why, 507-how, 507-create, 507-coordinate, 507-deliver |
| [作品版本与语义保护](writing/artifact-contract.md) | 507-create, 507-adapt, 507-review |
| [独立阅读页](design/reading-page.md) | 507-create, 507-adapt, 507-visualize |
| [离线 React 呈现合同](design/artifact-rendering.md) | 507-visualize, 507-demo |
| [任务页的内容与验证](design/task-page.md) | 507-work, 507-coordinate |
| [产品地图的内容与验证](design/product-map-page.md) | 507-product-map |
| [作者归属与材料支持](writing/author-and-source.md) | 507-create, 507-material, 507-adapt, 507-review |
| [工程原动作与运行证据](engineering/engineering-evidence.md) | 507-spec, 507-do, 507-review |
| [按情境拆解与协调](collaboration/task-coordination.md) | 507-coordinate, 507-create, 507-work |
| [外部取证与证据交接](evidence-and-decisions/external-research.md) | skill-design, 507-why, 507-how, 507-create, 507-material |
| [对象关系、比较与观察](design/visual-understanding.md) | 507-why, 507-how, 507-adapt, 507-coordinate, 507-visualize |
| [视觉方向与真实反馈](design/visual-direction.md) | 507-create, 507-adapt, 507-do |
| [真实中断、交接与续办](collaboration/continuation.md) | skill-design, 507-what, 507-work, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-review, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-material, 507-adapt, 507-setup, 507-clean, 507-plan |
| [可丢弃原型证据](engineering/probe-lifecycle.md) | 507-why, 507-how |
| [架构摩擦与候选证据](engineering/architecture-candidates.md) | 507-why, 507-how |
| [行为不变修改证据门](engineering/behavior-preserving-change.md) | 507-how, 507-do, 507-clean |
| [操作、状态与实际呈现](engineering/interaction.md) | 507-do, 507-adapt, 507-create |
| [显化作者一手材料](writing/author-interview.md) | 507-create, 507-material |
| [同一场景的解释检验](writing/explanation-progression.md) | 507-why, 507-create |
| [参考视听证据与原创借鉴](design/media-study.md) | 507-why, 507-material, 507-create, 507-adapt |
| [媒体版本、时间与验收](design/media-production.md) | 507-create, 507-adapt |
| [传播标题与正文兑现](writing/title-promises.md) | 507-create, 507-adapt |
| [旧技能引用与当前职责](collaboration/skill-entry-resolution.md) | skill-design, 507-setup, 507-deliver, 507-coordinate |
| [交互点、关系与证据](engineering/interaction-map.md) | 507-product-map, 507-how, 507-spec, 507-review |
| [持续工作的记录与读回](collaboration/work-records.md) | skill-design, 507-what, 507-why, 507-how, 507-plan, 507-do, 507-clean, 507-create, 507-adapt, 507-work, 507-setup, 507-spec, 507-coordinate, 507-issue, 507-deliver, 507-retro, 507-material |
| [提示与指令审计](collaboration/prompt-instruction-audit.md) | skill-design, 507-setup, 507-review |

主入口说明何时读取和读后做什么；这里集中维护方法正文，消费者按[清单](../../packages.json)直接引用同一份方法。方法共享不要求每个任务通读整套资料。

项目依据与项目导航仅由setup消费，现分别在其包内维护[项目依据](../../skills/507-setup/references/project-foundation.md)与[项目导航](../../skills/507-setup/references/project-navigation.md)，不再参与共有副本生成。

# 共有方法

本目录的 28 份方法按条件提供判断与工作做法，没有独立技能入口。消费者与采用条件以[资源登记](../catalog.json)为准；专用方法留在各技能包内。脚本和工具说明见[components](../components/README.md)，设计参考见[design](../design/README.md)。

| 方法 | 当前使用者 |
| --- | --- |
| [事实、来源与工作基线](evidence.md) | skill-design, 507-what, 507-work, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-review, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-material, 507-component, 507-product-map |
| [目标、边界与决定归属](decision-ownership.md) | skill-design, 507-what, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-issue, 507-coordinate, 507-deliver, 507-retro |
| [信息缺口与问题依赖](question-frontier.md) | skill-design, 507-what, 507-why, 507-how, 507-create, 507-spec |
| [真实候选、反证与代价](alternatives.md) | skill-design, 507-what, 507-why, 507-how, 507-create, 507-coordinate, 507-retro |
| [可观察验收与相称验证](validation.md) | skill-design, 507-what, 507-work, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-review, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-component, 507-product-map |
| [当前权威、冲突与返回](authority-and-return.md) | skill-design, 507-what, 507-work, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-review, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-component, 507-product-map |
| [最小清晰表达与关系类型](clear-expression.md) | skill-design, 507-what, 507-why, 507-how, 507-create, 507-coordinate, 507-deliver |
| [作品版本与语义保护](artifact-contract.md) | 507-create, 507-adapt |
| [离线HTML呈现合同](artifact-rendering.md) | 507-create, 507-adapt |
| [作者归属与材料支持](author-and-source.md) | 507-create, 507-material, 507-adapt |
| [工程原动作与运行证据](engineering-evidence.md) | 507-spec, 507-do, 507-review |
| [按情境拆解与协调](task-coordination.md) | 507-coordinate, 507-create, 507-work |
| [外部取证与证据交接](external-research.md) | skill-design, 507-why, 507-how, 507-create, 507-material |
| [对象关系、比较与观察](visual-understanding.md) | 507-why, 507-how, 507-adapt, 507-coordinate |
| [视觉方向与真实反馈](visual-direction.md) | 507-create, 507-adapt |
| [真实中断、交接与续办](continuation.md) | skill-design, 507-what, 507-work, 507-why, 507-how, 507-create, 507-spec, 507-do, 507-review, 507-issue, 507-coordinate, 507-deliver, 507-retro, 507-material, 507-adapt, 507-setup |
| [可丢弃原型证据](probe-lifecycle.md) | 507-why, 507-how |
| [架构摩擦与候选证据](architecture-candidates.md) | 507-why, 507-how |
| [行为不变修改证据门](behavior-preserving-change.md) | 507-how, 507-do, 507-component |
| [操作、状态与实际呈现](interaction.md) | 507-do, 507-adapt, 507-create |
| [显化作者一手材料](author-interview.md) | 507-create, 507-material |
| [已有知识入口组织](knowledge-organization.md) | 507-material |
| [同一场景的解释检验](explanation-progression.md) | 507-why, 507-create |
| [参考视听证据与原创借鉴](media-study.md) | 507-why, 507-material, 507-create, 507-adapt |
| [媒体版本、时间与验收](media-production.md) | 507-create, 507-adapt |
| [传播标题与正文兑现](title-promises.md) | 507-create, 507-adapt |
| [旧技能引用与当前职责](skill-entry-resolution.md) | skill-design, 507-setup, 507-deliver, 507-coordinate |
| [交互点、关系与证据](interaction-map.md) | 507-product-map, 507-how, 507-spec, 507-review |

主入口说明何时读取和读后做什么；这里集中维护方法正文，随包副本按[清单](../../next/packages.json)生成。方法共享不要求每个任务通读整套资料。

项目依据与项目导航仅由setup消费，现分别在其包内维护[项目依据](../../next/skills/507-setup/references/project-foundation.md)与[项目导航](../../next/skills/507-setup/references/project-navigation.md)，不再参与共有副本生成。

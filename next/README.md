# 507-skills 新体系

同一个507-skills新版当前源码包含20个入口：五主要、十五次要，新增交互点功能梳理。职责与当前清单见下表；工作角色可直接进入，不构成固定流水线。旧30保留为来源与回退。实际用户环境仍使用已核验的c333固定版19入口／262文件；本轮20入口候选未因构建或试跑自动安装。当前接入证据见[说明](../doc/40-版本实施方案/2026-10-14-c333使用环境接入.md)，交互地图实施与试用见[本轮记录](../doc/40-版本实施方案/2026-10-14-交互点功能地图实施与试用.md)。

## 主要职责

| 实际入口 | 独有责任 |
| --- | --- |
| [skill-design](../next/skills/skill-design/SKILL.md) | 技能设计与编写（skill-design） |
| [507-what](../next/skills/507-what/SKILL.md) | 目标与关键取舍 |
| [507-why](../next/skills/507-why/SKILL.md) | 理解、解释与证据 |
| [507-how](../next/skills/507-how/SKILL.md) | 介入点与变更策略 |
| [507-create](../next/skills/507-create/SKILL.md) | 作者主线与作品责任 |

## 次要工作能力

| 实际入口 | 独立结果 |
| --- | --- |
| [507-setup](skills/507-setup/SKILL.md) | 项目依据、规范迁移与局部导航维护 |
| [507-work-update](../next/skills/507-work-update/SKILL.md) | 工作发现、更新与推进 |
| [507-spec](../next/skills/507-spec/SKILL.md) | PRD、行为与验收规格 |
| [507-implement](../next/skills/507-implement/SKILL.md) | 实施与行为测试 |
| [507-component](skills/507-component/SKILL.md) | 产品界面组件库查找、复用或重复块抽取与调用迁移 |
| [507-product-map](skills/507-product-map/SKILL.md) | 指定功能的交互点及关系，同对象设计／实现／运行证据与可探索地图 |
| [507-fix](../next/skills/507-fix/SKILL.md) | 原动作复现与根因修复 |
| [507-review](../next/skills/507-review/SKILL.md) | 独立只读审查 |
| [507-issue](../next/skills/507-issue/SKILL.md) | 可跟进工单 |
| [507-coordinate](../next/skills/507-coordinate/SKILL.md) | 依赖、并行隔离与集成 |
| [507-deliver](../next/skills/507-deliver/SKILL.md) | PR表达与授权版本交付 |
| [507-retro](../next/skills/507-retro/SKILL.md) | 复盘与工具化建议 |
| [507-material](../next/skills/507-material/SKILL.md) | 作者材料、来源与支持范围 |
| [507-compose](../next/skills/507-compose/SKILL.md) | 组织、完整成文与局部改稿 |
| [507-adapt](../next/skills/507-adapt/SKILL.md) | 受众、容量与载体适配 |

明确故障、成熟稿、充分规格和已有任务图可直接进入相应能力；不因技能存在重跑what/why/how或全链。技能缺失可按同一合同直接工作，独立审查仍须另一执行者。

## 初始化仓库从哪里开始

明确要初始化仓库时可直接使用[507-setup](skills/507-setup/SKILL.md)。它采用[项目依据](../lib/methods/project-foundation.md)建立或归位 README、AGENTS、GLOSSARY、DESIGN、spec、doc，确需接续时维护 PROGRESS；内容与风险决定详略，不创建没有内容和消费者的空文件。维护地图时采用[项目导航](../lib/methods/project-navigation.md)。这些方法仍由setup持有修改范围与完成责任，不自行启动其它技能。

具体功能行为与验收需要成文时由507-spec承接；已有充分需求可直接进入工程实施。目标明确的仓库初始化不必先走what、why、how。

## 产品组件工作从哪里进入

直接要求查产品组件库、复用现有组件或将重复界面块送进库时，可使用[507-component](skills/507-component/SKILL.md)。已有适用组件先采用；库内没有且有多个确定使用位置才抽取并迁移已有调用；单处使用留原位。结果返回原页面或功能，页面操作、状态与反馈仍由507-implement按需读interaction并验证。不要求所有界面任务先过此入口。

该职责修改目标产品的组件及相关调用，不写本技能库的共有方法／脚本；后者仍由skill-design负责。技能主合同可直接触发，lib资料按条件消费，不会自动发现抽取工作或自行写入组件。

## 资源维护与构建

lib是唯一共有维护源，无SKILL入口。当前30方法源、10脚本源；包内普通生成副本共215份，273构建文件。作者/作品/呈现、工程证据和按情境协调是按实际消费者维护的共有方法，专用内容留包内。数据以[清单](packages.json)与[资源登记](../lib/catalog.json)为准。

明确要梳理产品功能与可操作节点时，可直接进入[507-product-map](skills/507-product-map/SKILL.md)。[共有方法](../lib/methods/interaction-map.md)由product-map、how、spec、review按需采用；专用[地图组件](../lib/components/product-map.md)从同一记录生成包含树、筛选、证据详情、全部关系与登记路径，更新记录后生成新目录。普通策略、规格、审查和实现不因此强制建图。

coordinate已覆盖工程、写作、研究与一般工作，按需选择局部协作、任务图推进、持续协调；create/work-update按相应缺口采用同一协调方法。临时任务网页由[task_view组件](../lib/components/task-view.md)读取已有过程记录生成与更新，不能直接编辑生成HTML；表达不足改组件后重生成。无需网页或独立工作时直接完成，不新增技能身份或强制日志。

在仓库根运行：

```sh
python3 next/scripts/package_skills.py sync
python3 next/scripts/package_skills.py check
python3 next/scripts/package_skills.py build
python3 -m unittest discover -s next/tests -v
python3 -m unittest discover -s lib/components/tests -v
```

sync先验证完整候选再切换，失败恢复；check拒绝未登记身份、文件、越界、软链、语法错误、副本漂移及过期名称声明；build以内容指纹保留完整不可变快照，独占发布避免覆盖同时出现的目标。当前实现按精确清单维护，不是通用调度或安装器。

遇到旧技能引用时，setup、deliver、coordinate及skill-design按[旧引用方法](../lib/methods/skill-entry-resolution.md)采用包内名称查询；普通目标已有准确入口时跳过。查询只返回当前声明、旧来源及候选消费者，不执行技能、不核验宿主启用，也不扩大原任务许可。未知名称保留未知，多个消费者不成为固定调用链。历史原件继续保留；项目维护仍按具体授权原位修改对应引用。

维护者改变入口合同或旧能力处置后，先用[库投影组件](../lib/components/library-view.md)的`--emit-index`从真实清单生成并核对索引候选，再替换`lib/registry/skill-entry-index.md`并运行sync/check/build。索引只保存声明和合同身份，不把自身随包文件哈希写回自身；调用时只需包内脚本与索引，不要求作者仓库或兄弟包。

声称完整首次使用时，spec、implement和review按工程证据区分实际用户起点与夹具预置。用户必需的配置、绑定或确认被预置后仍是未验证；明确只验已绑定项目或SDK切片时保留该范围，不额外扩成全产品验收。

本轮按真实试用卡点校准当前信息与授权采用、完整目标对账及更新后新建消费者的验证；交付回报明确完成、是否符合有效预期和具体差距。主要职责和采用关系保持原边界；新增产品组件次要职责的验证及接入状态由根PROGRESS记录。

## 已验证与未覆盖

[本轮路径安排](../doc/40-版本实施方案/2026-10-12-创作与工程路径接入.md)与[整体覆盖](../doc/10-架构与运行/新体系实现覆盖.md)区分源码、显式菜单试跑、实际工具、独立审读、宿主自然发现及正式业务。当前进度见[PROGRESS](../PROGRESS.md)。

原三入口接入见[历史work-update试用](../doc/10-架构与运行/work-update接入与真实工作试用.md)；原两入口及候选记录保留阶段身份。HTML只证明该载体，不能作为图片、PPTX或视频制作完成。

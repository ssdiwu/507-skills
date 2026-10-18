# 当前技能入口

当前清单包含 **18 个入口：6 个主要技能、12 个次要工作能力**。`next` 是现行源码目录名，不表示这些技能仍待接入。源码与安装状态见[当前进度](../PROGRESS.md)，历史方案与验证见[历史导航](../doc/历史导航.md)。

主要／次要沿[术语表](../GLOSSARY.md#分层与共有资源)定义：用户主要触发主要技能，Agent 按需采用主次技能。清楚任务由 Agent 直接采用所需能力，不固定串行调用；这不表示运行环境权限或宿主已经隐藏次要入口。

## 主要职责

| 实际入口 | 独有责任 |
| --- | --- |
| [skill-design](skills/skill-design/SKILL.md) | 技能设计与编写（skill-design） |
| [507-what](skills/507-what/SKILL.md) | 目标与关键取舍 |
| [507-why](skills/507-why/SKILL.md) | 陌生项目初识、理解、解释与证据 |
| [507-how](skills/507-how/SKILL.md) | 介入点与变更策略 |
| [507-do](skills/507-do/SKILL.md) | 工程实现、修复、局部修改与指定测试，已有方案直接执行 |
| [507-create](skills/507-create/SKILL.md) | 创作、完整成文与指定修订 |

## 次要工作能力

| 实际入口 | 独立结果 |
| --- | --- |
| [507-setup](skills/507-setup/SKILL.md) | 项目依据、规范迁移与局部导航维护 |
| [507-work-update](skills/507-work-update/SKILL.md) | 工作发现、更新与推进 |
| [507-spec](skills/507-spec/SKILL.md) | PRD、行为与验收规格 |
| [507-component](skills/507-component/SKILL.md) | 产品界面组件库查找、复用或重复块抽取与调用迁移 |
| [507-product-map](skills/507-product-map/SKILL.md) | 指定功能的交互点及关系，同对象设计／实现／运行证据与可探索地图 |
| [507-review](skills/507-review/SKILL.md) | 独立只读审查 |
| [507-issue](skills/507-issue/SKILL.md) | 可独立接手的调查／执行工单；只起草也整理依据、下一动作与推进条件 |
| [507-coordinate](skills/507-coordinate/SKILL.md) | 依赖、并行隔离与集成 |
| [507-deliver](skills/507-deliver/SKILL.md) | PR表达与授权版本交付 |
| [507-retro](skills/507-retro/SKILL.md) | 复盘与工具化建议 |
| [507-material](skills/507-material/SKILL.md) | 作者材料、来源与支持范围 |
| [507-adapt](skills/507-adapt/SKILL.md) | 受众、容量与载体适配 |

明确故障、成熟稿、充分规格和已有任务图可直接进入相应能力；不因技能存在重跑what/why/how或全链。技能缺失可按同一合同直接工作，独立审查仍须另一执行者。

工单只起草时直接采用507-issue主文的正文组织方法，调查态保留关键未知并给证据动作和推进条件；行为、范围、依赖与验收充分后才作为ready交接。平台参考只在对应动作已获授权时读取，不把正文组织挂在平台许可之后。

## 常见任务的直接入口

| 任务 | 采用方式 |
| --- | --- |
| 实现功能、修 bug、局部修改或只跑测试 | do 沿已有需求和方案直接处理；修复保留复现、根因和原动作复验；只跑测试不自动改代码 |
| 了解可定位的陌生项目 | why 自主建立必要全貌并核对代表路径；交互地图只在确有需要时使用 |
| 初始化仓库或维护文档导航 | setup 按范围建立或维护项目依据；具体行为要求由 spec 承接 |
| 整理材料、成文或换载体 | 材料需要核身份时用 material；已有目标和材料由 create 直接成文或修改；成熟内容换受众或载体用 adapt |
| 找产品界面组件 | component 先核目标产品已有组件；没有适用组件且有多个确定使用位置时才抽取并迁移调用 |
| 梳理功能与实际操作证据 | product-map 对齐交互点、关系及设计／实现／运行证据；普通实现不强制建图 |
| 推进已有工作或安排协作 | work-update 维护事项并推进授权工作；coordinate 按实际依赖组织独立结果与集成 |

产品界面组件库与本技能库的共有资源库是不同对象。`507-component` 处理前者，`skill-design` 处理后者。方法和工具可以直接采用，不必为读取一段参考再启动一个技能。

## 资源维护与构建

[共有资源库](../lib/README.md)分开说明方法、执行脚本、工具说明、设计参考与名称索引。当前登记 30 份共有方法、10 个执行脚本；52 个共有源形成 199 份随包副本。加上各技能的 55 份自有文件，精确包清单共 254 个文件。事实以[packages.json](packages.json)与[catalog.json](../lib/catalog.json)为准。

共有源修改后生成对应副本，不手改随包副本。入口合同或旧名处置改变时，按[名称索引说明](../lib/components/library-view.md)先生成并核对索引，再同步包。名称查询只返回声明，不执行技能或证明宿主已启用。

在仓库根按变更范围运行：

```sh
python3 next/scripts/package_skills.py sync
python3 next/scripts/package_skills.py check
python3 next/scripts/package_skills.py build
python3 -m unittest discover -s next/tests -v
python3 -m unittest discover -s lib/components/tests -v
```

sync 验证候选后切换并保留失败恢复；check 核身份、精确文件、资源闭包、软链接、副本漂移和索引新鲜度；build 生成按内容指纹定位的不可变快照。构建工具不承担宿主安装或自动调度。只改导航说明时核链接、范围和内容保全，不为文档整理重跑业务。

## 能力与验证边界

入口和资源已实现，不等于每个自然任务都已稳定采用。离线 HTML 与 PNG、PPTX、音频或视频分别核验；源码检查、实际操作、独立审查、安装发现与人的接受保留各自证据。

当前已接入内容及未验证项在[PROGRESS](../PROGRESS.md)维护；各轮首次、反馈修订和独审记录见[历史导航](../doc/历史导航.md)。历史测试命令和已发布专项能力仍保留在原版本记录中，不作为本清单的默认执行流程。

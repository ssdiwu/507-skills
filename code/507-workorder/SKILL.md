---
name: 507-workorder
description: "写 GitHub issue 工单——把任务结构化成可上传 GitHub、可被 AI 领取执行的工单。正向把方案/PRD 拆成可领取 issue，反向把 bug/gap 落成可追踪 issue。模板以 507 实际 issue 实践为骨架（正向八板块 + 反向现象/影响/方案/验收/风险），issue 本身就是执行合同，不另产 Agent Brief。Use when user mentions 写 issue, 开 issue, 拆 issue, 开工单, 上传 issue, 让 AI 领取任务, 把任务传 GitHub, bug 转 issue, gap 转 issue, 记个 bug, 落成工单, 提 issue, workorder, work order, github issue, ticket."
---

# 写工单（workorder）

把任务结构化成**可上传 GitHub、可被 AI 领取执行的工单**。

解决的核心问题是 **任务留档与协同**——当你需要把一个任务交给 GitHub 上的 AI 或协作者领取时，口头描述不够，要落成一份结构化、自足、可追踪的 issue。issue 既是留档载体，也是执行合同：AI 领取后照着 issue 内容直接做，不需要你在 issue 之外再补一份执行说明。

`507-workorder` 做的是：**任务 → 结构化 GitHub issue 工单**。

## 覆盖什么

- **正向**：把方案 / PRD / 对话拆成可领取的 issue（垂直切片，窄但完整的端到端路径）
- **反向**：把 bug / gap / 坏行为落成可追踪的 issue
- 多个 issue 的推进顺序与依赖总表

## 不覆盖什么

- 开工前把方案问透 → 不在本 skill 范围（先问透再开工单）
- 把对话/方案落成**需求规格文档（PRD）** → 用 `507-blueprint`（PRD 是"想清楚要做什么"，工单是"把要做的事写成可领取的单元"）
- 真实调用 issue tracker 创建 issue（除非项目已有 `gh` CLI 等明确工具与权限）
- 执行本身（领取后怎么做走执行入口，不在本 skill 范围）

> 和 blueprint 的关系：blueprint 产 PRD（需求规格），workorder 产 issue（可领取工单）。PRD 可作为 workorder 的可选输入（重任务先 PRD 再拆工单），但 workorder 也可独立触发（bug 直接开工单，不经 PRD）。

## 核心纪律（不可违反）

1. **issue 即执行合同**——issue 要写得足够完整，让领取的 AI 照着内容直接做，不依赖你在 issue 之外再补说明。含：当前状态、目标行为、范围、验收、依赖。这就是 Agent Brief 该做的事——**融进 issue，不单独产**。
2. **垂直切片**——正向 issue 每个是一条窄但完整的端到端路径，能独立 demo 或验证。避免按 schema / API / UI / 测试等水平层拆。
3. **耐久优先于精确**——issue 可能几天后才被领取，代码结构会变。写接口、类型、行为契约、验收标准；少写文件路径，更不写行号。
4. **写行为，不写步骤**——描述系统应做什么，不规定领取者去哪个文件怎么改。
5. **用项目语言**——先读 `doc/术语表.md` 和相关 `doc/决策档案/`；issue 标题和正文使用项目术语。
6. **不空访谈**——综合已有上下文（对话/PRD/代码），不重新采访 507。缺关键事实时，一次只问一个问题，并附推荐答案。
7. **范围外要显式**——明确写"不做什么"，防止领取者镀金（擅自加东西）。
8. **远程元数据必须完整**——上传 GitHub 后必须设置并核验 `labels（标签）` 与 `assignees（负责人）`；默认负责人使用当前 GitHub 登录用户，除非 507 明确指定其他负责人。

## 模式一：正向 issue（把方案/PRD 拆成可领取工单）

适用：507 说"拆 issue""开 issue""把方案传 GitHub""让 AI 领取"。

### 正向 issue 八板块模板

来自 507 实际 issue 实践（如 diwu-flow-dev #650/#651），这是验证过的成熟形态：

```md
## 1. 标识 [identity]
- **id**: 唯一标识（若项目有 id 规则则遵循，否则用 issue 编号）
- **title**: 人类可读名称
- **type**: 对象类别（infra / feature / bug / gap / 治理 等）

## 2. 背景与目标 [background]
- **why**: 为什么要做，承接哪个上层目标/issue
- **problem**: 不做会怎样
- **goal**: 这一轮要得到什么（一句话）

## 3. 当前状态快照 [current_state]
- 当前现状（已有什么、还缺什么）
- 已拍板补充约束（若有）

## 4. 范围与不做 [scope]
### includes
- 这一轮要做的
### excludes
- 明确不做的（防止镀金）

## 5. 关系与依赖 [relations]
- **depends_on**: #...（前置 issue）
- **blocks**: 后续什么依赖这个
- **related_issues**: #...

## 6. 验收与验证 [acceptance]
### criteria
- [ ] 标准 1（可独立验证）
- [ ] 标准 2
### verification
- 怎么验证（由谁/怎么核对）

## 7. 执行与决策 [execution]
- **decision**: 已定方向（若有）
- **next_action**: 建议先做什么

## 8. 远程映射 [remote]（若上传 GitHub）
- **parent_issue**: #...
- **role**: 这个 issue 在整体里的角色
- **labels**: 使用仓库已有标签，至少包含类型标签（`缺陷` / `能力` / `体验优化` / `规范治理`）和优先级标签（`P0`–`P3`）；按任务需要补充领域标签（如 `界面` / `服务` / `贴纸` / `测试`）。
- **assignees**: 默认当前 GitHub 登录用户；若项目协作约定另有负责人，以明确指定为准。
```

### 可选：推进顺序与依赖总表

当一次拆出多个 issue 时，在其中一个主 issue（或单独文档）里附推进顺序：

```md
## 推进顺序与依赖总表
### 推荐线性推进顺序
1. #A — ...
2. #B — ...
3. #C — ...

### 关键依赖关系
- #A 为 #B/#C 提供前置锚点
- #B 先于 #D，因为 ...

### issue 类型分组
- 开路 issue: #A, #B
- 内容层 issue: #C, #D
- 收尾 issue: #E
```

## 模式二：反向 issue（bug/gap 转工单）

适用：507 说"记个 bug""这个行为不对帮我转 issue""这个 gap 要落成 issue""提个 QA"。

### 反向 issue 模板

来自 507 实际 gap issue 实践（如 diwu-flow-dev #659）：

```md
## 现象
客观描述实际发生了什么（不掺判断）。
- 具体行为
- 数据/日志证据

## 为什么这是个问题
| 维度 | 影响 |
|------|------|
| 功能 | ... |
| 性能 | ... |
| 可读性 | ... |
| 正确性风险 | ... |

核心矛盾：设计定位说 X，实现上却是 Y。

## 前置依赖
无 / #...（这是独立 gap / 依赖某 issue）

## 方向（待决策）
### 方案 A：...（推荐）
- 优点 / 缺点 / 改动范围

### 方案 B：...
- 优点 / 缺点 / 改动范围

## 验收标准（方案确定后补充）
- [ ] ...
- [ ] ...

## 风险提示
- 需确认的隐式假设
- 可能受影响的相邻功能
```

### 反向 issue 纪律

- **轻澄清，不过访**：最多 2-3 个短问题，补齐三件事——实际发生了什么、预期是什么、怎么复现。
- **用户视角**：写行为，不写代码实现；不用文件路径、行号或内部模块名（除非是定位必需）。
- **复现步骤必填**：还原路径不清楚时，先补步骤再写 issue。
- **先判单 issue 还是拆分**：一个坏行为 → 单 issue；多个独立坏点 → 拆成多个薄 issue。

## 发布

- 按依赖顺序发布：blocker 先发，后续 issue 才能引用真实编号。
- 发布前先用 `gh label list` 读取仓库已有标签，不自造标签；用 `gh api user` 确认当前登录用户。
- 用 `gh issue create` 等工具上传（若项目有 gh CLI 和权限）。
- 创建成功后必须补齐远程元数据：`gh issue edit <number> --add-label "..." --add-assignee "..."`。
- 创建后必须用 `gh issue view <number> --json labels,assignees` 核验标签和负责人确实已落远程。
- **不关闭或修改 parent issue**。

## 和其他 skill 的边界

| skill | 分工 |
|---|---|
| **workorder** | 任务 → GitHub issue 工单（本 skill） |
| **blueprint** | 对话/方案 → PRD 需求规格（workorder 的可选上游；PRD 想清楚，再拆工单） |
| **grill** | 把方案/改动问透（开工单前对齐） |
| **执行入口** | 编排执行（领取 issue 后另行编排；本 skill 只产工单，不编排执行） |
| **修 bug** | 修复走执行入口（反向 issue 记录问题后，修复另行处理） |

时序：对齐 → blueprint 画 PRD（可选）→ workorder 开工单 → AI 领取 → 执行。

## 启动姿势

当 507：
- 说"拆 issue""开 issue""把方案传 GitHub""让 AI 领取"→ 正向模式
- 说"记个 bug""这个 gap 落成 issue""提个 QA"→ 反向模式

你就：
1. 识别正向还是反向。
2. 读 `doc/术语表.md` 和相关上下文，用项目语言。
3. 按对应模板写 issue（issue 即执行合同，要自足完整）。
4. 多个 issue 时附推进顺序与依赖总表。
5. 按依赖顺序发布（有工具就上传，没有就本地文档）。

## 红线

- 不产 Agent Brief 作为独立文档（融进 issue，issue 本身就是执行合同）。
- 不写文件路径/行号作为执行指令（写行为契约，耐久优先）。
- 不把 issue 写成实现步骤（写"做什么"不写"怎么改"）。
- 不跳过范围外声明（excludes 防镀金）。
- 不在和 blueprint 的边界上抢 PRD 的活。
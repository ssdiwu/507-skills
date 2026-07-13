---
name: 507-ground
description: "为一个或多个代码项目做 507 工作流初始化/巡检。重点检查项目自己的 AGENTS.md、doc/、doc/术语表.md、doc/决策档案/、分层 README 和已口述但未沉淀的约束。Use when user mentions setup 507, 项目初始化, 巡检这些项目, 校准 AGENTS.md, 补项目地图, 沉淀术语表, 整理项目规范, 工作流初始化, 初始化项目, 巡检项目, 项目规范巡检, 补 README, 补 doc, 沉淀约束, 校准工作流, 项目体检, 给这个项目配 507, project setup, AGENTS.md, project map, project bootstrap, scaffold."
---

# 507 项目初始化 / 巡检

这个 skill 用来给**具体代码项目**做 507 工作流初始化或巡检。

它关注的是每个项目自己的规范和知识沉淀，而不是整理全局 agent 配置。

巡检基准是 `references/project-standard.md`（项目标准规范）。如果项目有明确历史例外，先说明差异，再问 507 是否保留。

核心对象：

- 项目根 `AGENTS.md`
- 项目根 `README.md`
- 项目根 `CHANGELOG.md`（主动维护项目从开局建立；以 `Unreleased` 段承接未发布变更）
- `doc/README.md`（文档地图）
- `doc/术语表.md`（项目术语表）
- `doc/决策档案/`（架构决策记录）
- 各代码目录的 `README.md`
- 已经在对话里反复口述、但还没落到文件里的约束

权威标准定义见本技能 `references/project-standard.md`。巡检时以该文件为单一事实源，本文件不重抄具体规则。

## 什么时候使用

- 新项目需要接入 507 工作流。
- 老项目的 `AGENTS.md` 太胖、太旧或缺关键约束。
- 项目有 `doc/`，但缺术语表、ADR 或文档地图。
- 多个项目需要统一检查初始化质量。
- 507 口述了项目规则，需要沉淀进项目文件。

## 不做什么

- 不整理全局 `/Users/diwu/.pi/agent/AGENTS.md`，除非用户明确要求。
- 不把所有规则塞进项目 `AGENTS.md`。
- 不自动重写项目文档；先巡检、列建议、等确认。
- 不为了“规范完整”创建空目录或空文档。

## 巡检输入

用户可以给一个或多个项目根目录，例如：

```text
/Users/diwu/Documents/codes/Githubs/pi-daily
/Users/diwu/Documents/codes/Githubs/pi-dloop
/Users/diwu/Documents/codes/Githubs/pi-dteam
```

如果用户给的是 workspace（如 `/Users/diwu/Documents/codes/Githubs`），先识别里面的 repo 列表，等 507 选项目，不要自动全量修改。

## 巡检流程

### 0. 先读项目标准

先读 `references/project-standard.md`（本技能的权威标准定义），再读目标项目。不要凭记忆执行标准。

### 1. 先扫项目结构

对每个项目读取：

- 根目录文件：`AGENTS.md`、`README.md`、`CHANGELOG.md`、`package.json`、入口文件
- `doc/` 或 `docs/` 结构，特别检查是否按编号段组织（`00 / 10 / 20 / 30 / 40 / 90`）
- `doc/README.md`
- `doc/术语表.md`
- `doc/决策档案/`
- 代码目录 README：如 `src/README.md`、`tests/README.md`、`scripts/README.md`

输出项目体检表：

```md
| 项目 | AGENTS.md | README | CHANGELOG | doc/README | doc 编号地图 | 术语表 | adr | 分层 README | 主要缺口 |
|---|---|---|---|---|---|---|---|---|---|
```

### 2. 读现有规范

如果存在 `AGENTS.md`，判断它承担了什么职责：

- 项目一句话定位
- 先读文档顺序
- 项目结构地图
- 代码边界 / 安全边界
- README 规则
- 验证命令
- Git 规范
- 项目特有“不做”清单

如果某部分太长，建议迁到 `doc/`；如果缺关键硬约束，建议补进 `AGENTS.md`。

### 3. 检查 `doc/` 是否像项目地图

按 `references/project-standard.md` 的 `doc/` 必备项逐项核验：

- `doc/README.md` 是否存在，并回答阅读顺序、权威性、历史归档边界。
- 是否采用或明确豁免编号目录地图：`00-产品与原则/`、`10-架构与运行/`、`20-能力参考/`、`30-路线图/`、`40-版本实施方案/`、`90-归档/`。
- 已有路线图是否放在 `30-路线图/`，而不是平铺在 `doc/` 根目录。
- 已有版本实施方案是否放在 `40-版本实施方案/`，且方案内包含 checklist。
- 历史材料、旧方案、验证日志是否放在 `90-归档/`，且不被当前入口当作权威。

本步骤不重写规则，只输出"是否达标 + 缺什么"。

若 `doc/` 涉及**结构改造**（按编号段组织、新建/合并 `doc/决策档案/`、归档历史文档、移动路线图 / 实施方案等），走专项地图流程；本 skill 不复制地图细节。

### 4. 检查术语表

按 `references/project-standard.md` 的术语表规范核验（写什么 / 不写什么 / 格式）。本步骤只输出"是否达标 + 缺什么"。

若涉及**新增/扩充术语**，先用 `507-grill` 对齐术语定义（避免把未对齐的“漂亮词”塞进术语表）。

### 5. 检查 ADR

按 `references/project-standard.md` 的 ADR 三条判定标准（难逆转 / 无上下文会困惑 / 真实权衡）核验。本步骤不重写规则。

同时核验载体规则（定义见 `references/project-standard.md`，不在此重抄）：文件名是否为 `0001-中文标题.md`（中文为主、项目术语沿用术语表规范叫法）；若有 ADR 文件，`doc/决策档案/README.md` 索引是否与文件同步（编号 + 标题 + 一句话主旨）。

没有这样的决策时，不建议创建空 `doc/决策档案/` 目录。

### 6. 检查分层 README

按 `references/project-standard.md` 的"含代码目录的 `README.md`"清单核验（`src/` / `tests/` / `scripts/` / `bin/` / `packages/` / `apps/` 等）。本步骤只输出"哪些目录缺 README、哪些 README 失真"。

若涉及**补缺失 / 校准失真**的实际写入，走专项地图流程；本 skill 不复制地图的载体细节。

### 7. 检查 `CHANGELOG.md`

按 `references/project-standard.md` 的 CHANGELOG 条件必备项核验：

- 主动维护型代码项目（包括尚未发布但会持续演进的项目）→ 从开局应有 `CHANGELOG.md`；以 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 基本格式建立 `## [Unreleased]`，不倒填历史提交。
- 一次性原型、明确不再维护的实验或私人临时脚本 → 可明确豁免。
- 已存在的 CHANGELOG：版本倒序、变更类型标注、破坏性变更和迁移是否显式；`Unreleased` 只写用户/使用者可感知变更，不误塞内部计划、实现细节或逐提交日志。

只输出"是否达标 + 缺什么"。

### 8. 可选：生成 / 校准 `.pi/` 配置

巡检完文档规范后，如果项目还没有 Pi 配置，顺手补齐：

- 从 `package.json` scripts / `Makefile` / `pyproject.toml` 等推导 build / test / lint / check 命令。
- 确认 `.pi/AGENTS.md`（项目级 agent 规范）是否存在且与根 `AGENTS.md` 不冲突。
- 不重复检测 Node/Python/Go/Rust 这种项目类型——pi 运行时本身会处理。

只做必要配置；不为“完整”生成多余 settings。

### 9. 给初始化建议，不直接写

先输出建议清单：

```md
## <项目名> setup 建议

### 应保留在 AGENTS.md
- ...

### 应补到 doc/
- ...

### doc 编号地图缺口
- ...

### 应新增 `术语表.md` 术语
- ...

### 可能需要 ADR
- ...

### CHANGELOG.md 缺口
- ...

### README 缺口
- ...

### 建议执行顺序
1. ...
2. ...
```

一次只问 507 一个确认问题，并附推荐答案。

## 三个样本的判断基准

从当前已看过的样本出发：

- `pi-daily`：已有 `AGENTS.md`、`doc/README.md`、路线图和系统架构，缺 `doc/术语表.md` / `doc/决策档案/` / `CHANGELOG.md`；适合补术语表候选，不急着补 ADR；若对外发布应补 CHANGELOG。
- `pi-dloop`：目前只有 `README.md`，没有 `AGENTS.md` / `doc/`；适合做完整初始化：项目 AGENTS、doc/README、`术语表.md` 候选、README 分层检查。
- `pi-dteam`：已有丰富 `doc/` 和 `doc/术语表.md`，但 `术语表.md` 仍偏薄；适合做术语表扩充和 ADR 候选提取，而不是重建。

这些只是判断基准；实际执行仍要先读项目当前文件。

## 输出格式

默认先输出巡检报告，不写文件：

```md
# 507 Setup 巡检报告

## 总览

| 项目 | 状态 | 主要缺口 | 推荐动作 |

## 项目详情

### <project>
- AGENTS.md：...
- README：...
- CHANGELOG：...
- doc/：...
- doc 编号地图：...
- 术语表：...
- ADR：...
- README 地图：...
- 建议下一步：...
```

507 确认后再落地改文件。

## 红线

- 不把 workspace 当单项目初始化。
- 不未经确认重写项目 `AGENTS.md`。
- 不创建空 `doc/决策档案/` 或空 `术语表.md` 充数。
- 不把术语表写成实现细节列表。
- 不把历史归档文档当当前权威。
- 不自动跨多个项目批量改文件。
- 不在本 skill 中重抄 `references/project-standard.md` 的规则；改动以该文件为唯一权威。

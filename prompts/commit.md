---
description: 收尾检查并为本次改动生成 Conventional Commit 提交信息（中文描述）
argument-hint: "[补充说明或代码路径]"
---
结合我们前面的讨论，以及以下补充内容，对本次改动做收尾检查、生成提交信息，并 commit：

$@

这是本次工作的**收尾**，不只是写 commit message。先确认代码、文档、版本与项目地图已经同步，再提交。

## 收尾流程

1. **确认范围并复核 diff**
   - `git status --short` 区分 staged / unstaged / untracked；发现非本次工作的意外改动，停下问用户。
   - 读 `git diff` 和 `git diff --cached`，确认无调试日志、临时文件、密钥、无关格式化。
   - 只精准暂存本次工作相关文件，不要 `git add .`；暂存区为空时先 `git add <path>`，仍不确定就问。

2. **同步收尾产物**：按下面「同步检查清单」判断是否要补 README / CHANGELOG / doc / 版本号；需要同步但还没同步的，先补齐并验证。

3. **验证**：跑最相关的 test / lint / build / smoke；无法验证时说明原因和可复验方式，不假装已验证。

4. **提交**：生成 Conventional Commits 中文提交信息，执行 `git commit`，提交前最后再看一次 `git status --short`。

5. **可选：打 tag**：只有版本发布才打。tag 跟随项目惯例（通常 `v<版本号>`，如 `v1.2.0`），必须和 `package.json` / manifest / CHANGELOG 版本段一致；打前确认对应 commit 已提交；是否 push 到远端先问用户，不自动推送。

## 同步检查清单

按变更类型逐项判断；不要求机械全改，但必须显式想过：

- **入口 README**：用户可见能力、安装/运行方式、项目定位、目录结构、主要入口变化时同步根 `README.md`。像 `Curio/README.md`、`pi-dgoal/README.md` 这类入口说明，不能在功能完成后失真。
- **分层 README / 项目地图**：目录职责、入口、边界、上下游变化时同步目标目录及上下级 `README.md`；涉及 `doc/` 组织或分层 README 按 `/map` 规则处理。
- **CHANGELOG**：主动维护型代码项目从开局就应有 `CHANGELOG.md`。缺失时先按以下最小骨架创建，不倒填历史提交：
  ```md
  # Changelog

  本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的基本格式；版本以 Git tag（Git 标签）为准。

  ## [Unreleased]
  ```
  本次用户/使用者可感知变更必须写入 `Unreleased` 的 `Added` / `Changed` / `Fixed` / `Removed` / `Breaking`；不塞内部实现细节、未来计划或逐提交日志，纯内部重构、测试或文档地图调整不强塞条目。
- **doc 知识库**：架构、运行方式、路线图、版本实施方案、能力边界变化时同步 `doc/README.md`、`doc/10-架构与运行/`、`doc/30-路线图/`、`doc/40-版本实施方案/` 等当前权威文档；归档文档不作当前权威。
- **术语表**：新增或澄清稳定项目语言时同步 `doc/术语表.md`；只写领域词。
- **决策档案**：同时满足「难逆转 / 无上下文会困惑 / 有真实权衡」才新增或更新 `doc/决策档案/`；不为小约定补空条目。新增 / 更新 ADR 时同步 `doc/决策档案/README.md` 索引（编号 + 标题 + 一句话主旨），文件名用 `0001-中文标题.md`（中文为主、项目术语沿用术语表规范叫法）。
- **版本相关**：发布或版本语义变化时同步 `package.json` / manifest / app version / lockfile / README 安装示例 / CHANGELOG 版本段 / 文档版本号；对外发布的库 / CLI / SDK / App 同时打 git tag，tag、版本号、CHANGELOG 版本段三者必须一致。
- **配置与脚本**：新增命令、环境变量、权限、迁移步骤、开发流程时同步 README、AGENTS、相关 doc 和示例配置。

## 提交信息格式

Conventional Commits，中文描述：

```text
type: 中文描述

[可选正文]
```

type 用英文：`feat` / `fix` / `refactor` / `docs` / `test` / `chore` / `perf` / `ci` / `style` / `build`。

- 主题行 ≤ 72 字符，中文简洁明了。
- 正文解释「为什么」，不重复 diff 已经展示的「做了什么」。
- 一次 commit 只做一件事；diff 混多个主题时先拆分提交或问用户。

## 完成后

提交成功后报告结果，让收尾可复验：

- 输出 commit hash（`git rev-parse --short HEAD`）。
- 最后跑一次 `git status --short` 确认工作区干净，或只剩预期外改动并说明。
- 打了 tag 就确认已创建（`git tag -l "v<版本号>"`）；是否 push 按你指示。
- 明确本轮工作到此结束，除非还有未完成项。

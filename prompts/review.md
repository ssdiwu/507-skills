---
description: 审查当前工作是否符合项目规范、需求和代码质量
argument-hint: "[补充说明、对比基准、issue/PRD/spec 路径或代码路径]"
---
结合前面的讨论，以及以下补充内容，审查当前工作：

$@

做一次统一 review，不只看未提交改动或 bug，同时检查三件事：

1. **Standards（项目规范）**：是否符合项目已有规范和约束。
2. **Spec（需求符合度）**：是否实现了原需求，有无漏做、误做、范围蔓延。
3. **Code Quality（代码质量）**：是否存在 bug、安全、错误处理、性能或可读性问题。

## 确定审查范围

不默认只看工作区未提交内容，按顺序尝试：

1. 507 明确给了 commit、branch、tag 或路径 → 以它为准。
2. 有未提交改动 → 审查 `git diff` 和 `git diff --staged`。
3. 当前分支相对 `origin/main` / `main` / `origin/master` / `master` 有差异 → 审查 `git diff <base>...HEAD`。
4. 已 commit/push 且无未提交改动 → 审查当前分支相对默认主干 diff；工作区干净不等于没可审内容。
5. 主干上无明确基准 → 审查最近一个 commit（`HEAD~1..HEAD`），说明是临时默认。
6. 仍无法判断 → 只问一个问题："要审查哪个范围？推荐 `origin/main...HEAD`。"

审查前简短说明选用的范围和原因。

## 审查依据

**项目规范来源**：`AGENTS.md`、`doc/README.md`、`doc/术语表.md`、`doc/决策档案/`、目标代码目录及上下级 `README.md`、`CONTRIBUTING.md` / `STYLE.md` / `STANDARDS.md`、lint / format / test / tsconfig 配置。只指出违反「已存在规范」的问题，不把个人偏好包装成规范。

**需求来源**：507 明确给的 issue / PRD / spec / 文档 → commit message / branch name 线索 → `doc/40-版本实施方案/` / `doc/30-路线图/` / `.scratch/` → 当前对话已确认需求。找不到需求来源不跳过，Spec 标「无明确 spec」，只检查范围蔓延和行为风险。

## 审查重点

**Standards**

- 是否违反项目 `AGENTS.md`、`doc/`、`README.md` 或决策档案；术语是否和 `doc/术语表.md` 冲突。
- 是否改了职责、入口、运行方式却没同步文档。
- 主动维护型代码项目是否从开局具备采用 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 基本格式的 `CHANGELOG.md` 与 `## [Unreleased]` 段；用户可见能力、安装 / 运行方式变化是否同步到对应分类条目。版本发布时 tag、版本号、CHANGELOG 版本段三者是否一致。
- 是否违反项目明确的「不做」边界。

**Spec**

- 需求要求的行为是否缺失或只做一半；是否做了需求没要求的事。
- 验收标准是否可验证；文档、测试和实际行为是否一致。
- 收尾产物是否完整：入口 README、项目地图、CHANGELOG、版本号是否和本次行为变化一致；版本发布是否漏打 git tag。

**Code Quality**：重点找真实问题——

- Bug / 逻辑错误：边界、空值、竞态、状态不一致。
- 安全：注入、权限绕过、数据泄露、硬编码密钥。
- 错误处理：静默失败、未处理 Promise、错误信息不可行动。
- 性能：明显 N+1、不必要重算、内存泄漏。
- 可维护性：复杂度过高、命名误导、死代码、重复逻辑。

## 给出后续工作流

Review 只负责发现问题和建议路径，不默认直接修。根据最严重发现给下一步：

- bug / 逻辑错误 / 安全风险 → 按 `/fix` 纪律修复。
- 测试缺口 / 失败测试 → 按 `/test` 纪律处理；明确 test-first 用 `/tdd`。
- 局部复杂度 / 行为不变清理 → 按 `/simplify` 纪律处理。
- README / doc / 项目地图失真 → 按 `/map` 纪律处理；全项目巡检转 `507-ground`。
- 架构摩擦 / 模块形状问题 → 不在 review 顺手重构，转 `507-inspection`。
- 漏做的新任务或需要持续完成 → 转 `/dgoal`，或先用 `507-blueprint` 落 PRD / `507-workorder` 开 issue 工单。

## 输出格式

先给结论，再列问题。

```md
## Review Scope
- 范围：...
- 基准：...
- 依据：...

## Summary
- Standards：通过 / 有问题 N 个
- Spec：通过 / 有问题 N 个 / 无明确 spec
- Code Quality：通过 / 有问题 N 个
- 最严重问题：...

## Findings
### 🔴 严重 / 🟡 警告 / 🔵 信息
- `file:line`：问题
  - 依据：规范 / spec / 代码证据
  - 建议：具体修复方向

## Recommended Next Mode
- 默认下一步：...
- 如果要继续处理：...

## Verification
- 已检查：...
- 建议运行：...
```

## 约束

- 不要因工作区干净就结束；很多 review 发生在 commit/push 之后。
- 不把 formatter / linter 会自动抓的问题重复列为人工发现，除非影响理解。
- 不大段复述 diff，只列有行动价值的问题。
- 没有证据的问题标为风险，不断言。
- 没发现问题时明确说「未发现阻塞问题」并说明审查范围。

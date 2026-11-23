# 项目状态

本页仅维护当前运行期状态；`v0.3.3`–`v0.3.6` 的历史验证过程已归档至[2026-11-23 阶段快照](doc/90-归档/阶段快照/2026-11-23-v0.4.0定版前.md)，更早记录见[历史导航](doc/历史导航.md)。

## 当前版本

- **发布版本**：`v0.4.1`（2026-11-23；在 `v0.4.0` 基础上完成 `AGENTS.md` 精简、`PROGRESS.md` 阶段归档与各层 `README.md` 名称对齐）
- **技能规模**：**24 个现行技能**（11 个主要技能，13 个次要工作能力）；退役 `507-coach`「判断陪练」，15 个非初代 30 旧入口已归档至 `doc/90-归档/技能/`。
- **本地应用地图**：可从[投影合同](lib/components/tools/projections/library-view.md)导出零外网单文件 HTML，提供 5 列 `Stage Flow`、6 条接力配方、5 列 78 项共有原则与 50 条历史旧名检索。
- **已验证范围**：
  - 仓库与前端检查：包检查（24 技能 / 328 文件 / 0 副本）、共有工具 104 项、仓库 67 项、前端 JS 34 项及类型/CSS/构建均通过；核心提交 `3d1d3d1` 已通过 [GitHub Actions Run #45143089555](https://github.com/ssdiwu/507-skills/actions/runs/45143089555)（Python 3.10 / 3.12）。
  - 本机宿主与自然触发：已切换 `~/.agents/skills/507-skills` 至不可变构建 `153c385...`，新启动的 Antigravity CLI 与 3 组无提示 `codex exec` 会话分别发现全部 24 技能并自动选用读取 `507-explain`、`507-build`、`507-design`。

## 能力范围

| 范围 | 已提供能力 |
| --- | --- |
| 判断与设计 | 明确目标（`507-what`）、解释现状（`507-explain`）、构造方案（`507-design`）、领域建模（`507-domain-model`）、归纳研判（`507-case-synthesis`）与造技能（`507-skill`） |
| 工程与审查 | 功能实现与修复（`507-build`）、清理（`507-clean`）、行为规格（`507-behavior-spec`）、执行计划（`507-step-plan`）、软件工单（`507-work-issue`）、功能地图（`507-product-map`）、独立审查（`507-peer-review`）、版本交付（`507-version-deliver`）与工程复盘（`507-work-retro`） |
| 内容与表达 | 创作成文（`507-create`）、换载体（`507-adapt`）、整理材料（`507-source-material`）、图解表达（`507-visual-explain`）与界面演示（`507-ui-demo`） |
| 推进与治理 | 推进事项（`507-track`）、协同派工（`507-task-dispatch`）、立规范（`507-setup`）与转门禁（`507-audit`） |
| 共有资源 | `lib/` 单份维护方法、校验与投影脚本、离线 React 呈现运行库与注册表 |

各入口职责见[技能清单](skills/README.md)、[术语表](GLOSSARY.md)和[共有资源库](lib/README.md)。

## 已知限制

- 当前仅完成 3 个单轮隔离样本的自然触发验证，其余 21 个技能及复杂多轮跨任务的长期自然选用率尚未做批量实测。
- 结构、打包、静态和离线浏览器测试通过，不代表真实业务需求理解、跨宿主环境配置或最终用户验收自动通过。
- 可选的 [Codex 维护钩子](scripts/codex-maintenance-hooks.md)保持未启用状态，实际宿主触发未验证。

## 待办

- 在日常真实任务中持续观察新命名（1 词 3 字主要技能 / 2 词 4 字次要技能）的长期自然命中率。
- 若本机桌面端 Codex App（`ChatGPT.app`）尚未重启，需先彻底退出再清空 `~/.codex/memories/` 回写残留，防止旧记忆继续影响新会话。

## 现行目录

`skills/` 为唯一现行技能源码，根目录 `packages.json` 为精确包清单，`lib/` 为共有维护源，`scripts/`、`tests/` 为维护与验证入口。旧 30 技能原件固定于 `v0.3.4`，可通过[历史导航](doc/历史导航.md#旧版原件与回归)查看并运行 `scripts/test_all.py`。

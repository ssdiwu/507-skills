# 507-skills 仓内工作规范

本仓库面向公开使用者提供 Agent Skills（智能体技能）；通用沟通、工程与验证原则沿用宿主全局规则，本文件仅规定本仓库独有约束。

## 阅读与运行时文档

- **首次进入**：读取本文件、根 [README](README.md) 与 [现行技能清单](skills/README.md)；历史原件与固定回归见[历史导航](doc/历史导航.md#旧版原件与回归)。改技能前读目标 `SKILL.md` 及适用的局部参考，不展开无关分支。
- **跨会话与进度**：续办先看 [PROGRESS.md](PROGRESS.md)；版本、能力范围、限制或待办变化时同步更新。**换阶段或定版前，先把已完成的旧验证过程归档至 `doc/90-归档/阶段快照/`**，保持 `PROGRESS.md` 只留当前状态。本机安装、试验过程与私有原始回执留在库外。
- **变更日志与规格**：用户可感知变化在交付前写入 [CHANGELOG.md](CHANGELOG.md) 的 `Unreleased`；技能分工与共有资源变更先核[分层规格](spec/技能分层与共有资源.md)和[设计依据](doc/10-架构与运行/技能分层设计依据.md)；创建或重构技能使用 [507-skill](skills/507-skill/SKILL.md)。

## 目录与共有库红线

- **24 技能分层结构**：`skills/` 是唯一现行源码（11 个主要技能 `507-<1词>` / 3 汉字；13 个次要技能 `507-<2词>` / 4 汉字），[skills/README](skills/README.md) 与各技能 `SKILL.md` 为行为边界权威。
- **单份共有库**：通用内容仅保留在 `lib/`（`methods/` 做法、`components/visual/` React 组件、`components/tools/` 检查/投影/导出、`catalog/` 清单与索引；[决策 0025](doc/决策档案/0025-按用途组织共有资源库.md)）。禁止向 `skills/` 复制共有内容或放置可执行脚本、runtime 与业务素材。
- **每技能单一声明源**：每个技能的自有文件与直接共有依赖唯一登记在各自的 `RESOURCES.md`；`packages.json` 只记身份、角色、路径与共有库总清单。迁移路径或增删共有资源时，同步 `RESOURCES.md`、`lib/catalog/`、调用方与文档。
- **独立阅读页与产品边界**：`507-create`、`507-adapt`、`507-visual-explain` 制作离线阅读页遵守[阅读页方法](lib/methods/design/reading-page.md)；共享技能不写特定产品分支或宿主专属调度。
- **可逆替换与中立模板**：[templates/](templates/AGENTS.global.example.md) 保持宿主中立，不同步个人配置回仓；替换本机已安装集合时先在库外生成并校验，再原子切换软链接，保留上一版供回退。

## 改完必跑检查

- **改技能、声明或维护文档**：`python3 -B scripts/package_skills.py check`（必须通过后才可报完成）。
- **改 `lib/`、目录或 `library-map.json`**：补跑 `python3 -B scripts/resource_map.py --check`，以及受影响的 `python3 -B -m unittest discover -s lib/components/tools/tests` 与 `tests`。
- **改 `lib/components/visual/`**：在 `lib/components/visual` 运行 `npm run typecheck && npm run check:css && npm run build && npm test && npm run test:ui`（视改动范围加跑 `test:library`、`test:visuals`、`test:layout`）。
- **发布前**：运行 `git diff --check`、密钥扫描，并确认公开说明未承诺未实现的能力。

## 安全与 Git 约定

- 不提交密钥（仅从环境变量读取）、Cookie（会话凭据）、个人知识库、客户数据、原始私密素材或本机绝对路径；脚本与测试样本写明运行条件。
- 提交遵循 `Conventional Commits`（`type: 中文描述`），单次提交聚焦一个可说明的改动，不混入 `__pycache__/`、临时测试产物或无关格式化。

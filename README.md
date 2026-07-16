# Agent Skills

一套把工作方法拆成**可独立触发、可组合、以明确产物衔接**的 Agent Skills（智能体技能）。每个 skill 都说明什么时候用、解决什么、产出什么，以及明确不做什么。

本仓库遵循 [Agent Skills 标准](https://agentskills.io/specification)，以 Pi 与 OpenAI Codex 为同等支持的主要宿主。共享 `SKILL.md`（技能说明）只定义动作、边界、产物和验收；宿主专属调度留在使用者自己的 `AGENTS.md`（智能体规范）。

## 适合谁

- 想把“和 Agent 聊聊”变成可复用工作流的人；
- 需要区分调研、对齐、规格化、实施、审查和交付的人；
- 同时使用 Pi、Codex 或其它兼容 Agent Skills 的宿主，希望共用一套方法的人；
- 想按需采用单个 skill，而不是一次引入完整框架的人。

## 工作流

```text
写作：素材 → mine 挖碎片 → fuse 融选题 → forge 共创收敛成文 → rednote 小红书图卡（可选）

代码：explain 理解项目 → prd 需求规格 / issue 任务定义（按需）→ 实现
      → map 项目地图（按需）→ review 交付审查 → commit Git 提交

架构回路：inspect 只读架构审查 → simplify 逐项验证与行为不变简化 → review
```

| 目录 | 目的 | 入口 |
| --- | --- | --- |
| [`write/`](write/README.md) | 从素材、视频到文章、讲稿、方案与创作包 | `507-mine`、`507-fuse`、`507-forge`、`507-breakdown` 等 |
| [`code/`](code/README.md) | 从项目理解、需求与实现到审查、提交和架构回路 | `507-explain`、`507-fix`、`507-simplify`、`507-review` 等 |
| [`common/`](common/README.md) | 不依赖具体场景的对齐、调研、解释与会话移交 | `507-grill`、`507-research`、`507-teach`、`507-handoff` |

完整触发词、输入输出和职责边界以各目录的 `SKILL.md` 为准。

## 代码工作流入口

| Skill | 动作 |
| --- | --- |
| `507-explain` | 读取项目依据，定位并解释问题，默认不实施 |
| `507-setup` | 初始化项目工作规范或执行全量规范检查 |
| `507-prd` | 把对话或方案沉淀成 PRD 需求规格 |
| `507-issue` | 把任务写成可上传 GitHub、可被领取的 issue |
| `507-prototype` | 在正式实现前用可丢弃原型验证具体问题 |
| `507-fix` | 建反馈环，最小修复 bug、报错、回归或冲突 |
| `507-test` | 测试是主任务时补测、运行和缩小失败范围 |
| `507-tdd` | 明确 test-first/TDD 时按红绿重构实施 |
| `507-simplify` | 保持外部行为不变，简化内部模块、抽象和接缝 |
| `507-map` | 以代码为证据，只维护 README/doc 项目地图 |
| `507-review` | 审查任意明确交付范围的规范、需求与质量 |
| `507-commit` | 明确要求提交时，验证、精确暂存并创建本地 commit |
| `507-inspect` | 只读寻找架构摩擦并输出完整证据报告 |
| `507-handoff` | 中断、换会话、压缩上下文或转交时输出临时交接摘要 |

## 安装

先 fork（派生）或 clone（克隆）仓库，再将它链接到两个宿主都支持的用户级技能目录：

```bash
mkdir -p ~/Workspace/Skills ~/.agents/skills
cd ~/Workspace/Skills
git clone https://github.com/ssdiwu/507-skills.git
ln -s ~/Workspace/Skills/507-skills ~/.agents/skills/507-skills
```

当前版本的 [Pi](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md) 与 [Codex](https://developers.openai.com/codex/build-skills#where-to-save-skills) 文档都将 `~/.agents/skills/` 列为用户级技能目录，并支持符号链接。这个发现位置属于宿主实现约定，不是 Agent Skills 标准本身；新增或修改 skill 后若没有立即出现，重开对应会话。

## 使用

### 自然语言触发

skill 的 `description`（描述）保留常用动作词，两个宿主都可按意图自动加载。例如：

- “先帮我定位这个问题在项目里的位置” → `507-explain`
- “修复这个回归，先建立复现” → `507-fix`
- “校准这个目录的 README 和项目地图” → `507-map`
- “审查这个分支相对 main 的全部改动” → `507-review`
- “用 TDD 做这个功能” → `507-tdd`
- “把 inspect 报告逐项处理完” → `507-simplify`

### 显式调用

需要强制使用某个技能时，使用宿主原生语法：

```text
Pi:    /skill:507-review
Codex: $507-review
```

两端允许使用不同工具和调度方式，但必须保持触发条件、修改权限、停止位置、产物和验证标准一致。

## 配套 Agent 配置

[`templates/AGENTS.global.example.md`](templates/AGENTS.global.example.md) 提供宿主中立的全局 `AGENTS.md` 示例。复制到自己的宿主配置后，再按该宿主可用工具补充调度规则；不要把个人称呼、机器路径、私有仓库或凭据同步回公开仓库。

项目局部约束始终优先于全局习惯。

## 设计原则

1. **一 skill 一动作**：相邻能力靠明确产物和路由接力，不用总控技能吞并。
2. **以产物接力**：碎片、候选 idea、PRD、issue、证据报告和 commit 是阶段交接物。
3. **流程可跳过**：每个 skill 可独立触发，完整链路是地图，不是强制仪式。
4. **结果跨宿主一致**：共享技能不写 Pi/Codex 条件分支；工具过程可以不同。
5. **先证据后优化**：先定位真实问题、失败样例或验证信号，再扩大工作量。
6. **安全默认**：不提交密钥、个人/客户资料或未经授权的素材；外部密钥只通过环境变量传入。

## 依赖与边界

多数 skill 是纯 Markdown（标记语言）工作流，无额外依赖。带脚本的写作 skill 会在自身说明中列出运行时依赖和环境变量。请先阅读对应目录的 `README.md`。

本仓库不包含任何 API key（接口密钥）、账号 Cookie（会话凭据）、个人 vault（知识库）或客户材料。详见 [`SECURITY.md`](SECURITY.md)。

## 贡献与发布

- 贡献方式见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
- 安全问题见 [`SECURITY.md`](SECURITY.md)。
- 变更记录见 [`CHANGELOG.md`](CHANGELOG.md)。
- 使用条款见 [`LICENSE`](LICENSE)。

欢迎提 issue（问题单）讨论 skill 边界、可复现失败和跨宿主行为。个人偏好优先留在自己的 `AGENTS.md` 或 fork 中。

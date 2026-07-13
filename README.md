# 507 Skills

一套把个人工作法拆成**可独立触发、可组合、以明确产物衔接**的 Agent Skills（智能体技能）。它不是 prompt（提示词）大杂烩：每个 skill 都说明什么时候用、解决什么、产出什么，以及明确不做什么。

> 这是 507 正在使用的工作流公开版。它以 [Pi](https://github.com/badlogic/pi-mono) 的 skill（技能）发现机制为主要使用环境；内容本身也可作为其他 Agent（智能体）平台的工作流参考。

## 适合谁

- 想把“和 Agent 聊聊”变成可复用工作流的人；
- 需要区分调研、对齐、规格化、实施、审查等不同动作的人；
- 想借鉴内容生产或代码项目工作流，但不想一次性引入完整框架的人。

## 两条工作流

```text
写作：素材 → mine 挖碎片 → fuse 融选题 → forge 共创收敛成文
代码：grill 对齐 → blueprint 写需求 → workorder 开工单 → 实现 → inspection 体检
```

| 目录 | 目的 | 入口 |
| --- | --- | --- |
| [`write/`](write/README.md) | 从素材、视频到文章、讲稿、方案与创作包 | `mine`、`fuse`、`forge`、`breakdown`、`remix` 等 |
| [`code/`](code/README.md) | 从项目对齐到需求、工单、原型和架构体检 | `ground`、`blueprint`、`workorder`、`mockup`、`inspection` |
| [`common/`](common/README.md) | 不依赖具体场景的对齐、调研与解释动作 | `grill`、`research`、`teach` |

完整的职责边界、输入输出和触发词在各 skill 的 `SKILL.md`（技能说明）中；流程图与总览见各目录的 `README.md`（说明文档）。

## 快速开始（Pi）

> 先 fork（派生）本仓库，便于保留自己的修改；以下路径可按你的环境调整。

```bash
# 1. 获取仓库
mkdir -p ~/Workspace/Skills
cd ~/Workspace/Skills
git clone https://github.com/ssdiwu/507-skills.git

# 2. 让 Pi 发现这些 skills
mkdir -p ~/.agents/skills
ln -s ~/Workspace/Skills/507-skills ~/.agents/skills/507-skills
```

重开 Pi 会话后，按自然语言触发对应 skill。例如：

- “帮我把这个方案问透” → `507-grill`
- “把刚才讨论整理成 PRD” → `507-blueprint`
- “把这些碎片融成一个选题” → `507-fuse`
- “给这个项目做架构体检” → `507-inspection`

不必安装全套：可以只复制一个 `SKILL.md`（技能说明）及其引用的 `references/`、`scripts/`、`assets/` 文件到自己的 skill 目录。带脚本的 skill 会在自身说明中列出运行时依赖和环境变量。

## 配套 Agent 配置

这个仓库额外公开了 507 的配套配置，供阅读、借鉴和按需采用：

- [`templates/AGENTS.global.example.md`](templates/AGENTS.global.example.md)：全局 `AGENTS.md`（代理行为规范）模板。它保留个人工作流取向，请替换称呼、路径和工具约定后再使用。
- [`prompts/`](prompts/)：`/explain`、`/fix`、`/review`、`/commit` 等 Pi prompt（提示词）模板。部分 prompt 引用 `dgoal`（目标闭环）或本仓库的 `507-*` skills；未安装相应能力时，请删改相关路由规则。

这些文件不是安装 skills 的必需项，也不应覆盖你已有的项目级 `AGENTS.md`（项目规范）。项目局部约束始终应优先于全局习惯。

## 设计原则

1. **一 skill 一动作**：`mine` 不写文章，`forge` 不挖素材；相邻 skill 不抢职责。
2. **以产物接力**：碎片、候选 idea、PRD、issue、报告是阶段之间的交接物，而不是口头状态。
3. **流程可跳过**：每个 skill 都可独立触发；完整链路是地图，不是强制仪式。
4. **先证据后优化**：先定位真实问题、失败样例或验证假设，再扩大工作量。
5. **安全默认**：不提交密钥、个人/客户资料或未经授权的素材；外部 API（接口）密钥仅通过环境变量传入。

## 依赖与边界

多数 skill 是纯 Markdown（标记语言）工作流，无额外依赖。`write/507-breakdown`（视频拉片）和 `write/507-remix`（视频重组）包含 Python（编程语言）脚本，可能需要 `ffmpeg`、`yt-dlp`、OCR（文字识别）或 `MiniMax_API_KEY`（接口密钥）；请先阅读其目录内的 `README.md`。

本仓库不包含任何 API key（接口密钥）、账号 Cookie（会话凭据）、个人 vault（知识库）或客户材料。请勿把它们提交到 fork（派生仓库）或 issue（问题单）。详见 [`SECURITY.md`](SECURITY.md)。

## 贡献与发布

- 贡献方式见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
- 安全问题见 [`SECURITY.md`](SECURITY.md)。
- 变更记录见 [`CHANGELOG.md`](CHANGELOG.md)。
- 使用条款见 [`LICENSE`](LICENSE)。

欢迎提 issue（问题单）讨论：一个 skill 的边界是否清楚、是否有可复现的失败场景、怎样让它更容易独立采用。对于非常个人化的偏好，优先在自己的 fork（派生仓库）中调整。

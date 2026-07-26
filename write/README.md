# write/ 写作与内容工作流

`write/` 处理碎片、选题、知识沉淀、书面作品、现场内容、人类方案、视频创作包、视频母版和平台适配。主创作链保留冶金隐喻；视频、舞台、方案与平台适配使用各自领域的动作名。

`common/` 是横向层：任何写作阶段遇到项目未知、概念障碍、外部证据或用户取舍，都可以调用 `explore`、`explain`、`research` 或 `grill`，解决后返回。它们不是写作前必须依次跑完的仪式。

## 三类入口

### 1. 素材、观点与知识

```mermaid
flowchart LR
    source["用户想法 / 指定素材 / research 证据 / 完成拉片包"] --> mine["507-mine<br/>碎片与观点"]
    mine --> fuse["507-fuse<br/>候选 idea"]
    mine --> cast["507-cast<br/>成熟碎片簇主题页"]
    fuse -->|"存在中心判断取舍"| grill["507-grill"]
    grill --> selected["已确认创意"]
    fuse -->|"材料只支持一条路径"| selected
    selected -->|"书面作品"| forge["507-forge"]
    selected -->|"现场讲述 / 视频旁白"| stage["507-stage"]
    stage -->|"成熟逐页内容"| ppt["507-ppt"]
    stage -->|"TTS / 克隆声音配音"| narrate["507-narrate"]
    narrate -->|"本地配音包"| video["507-video"]
    stage -->|"真人配音 / 已有声音 / 无旁白"| video
    forge -->|"社交视觉摘要 / Live Photo / 公众号封面"| rednote["507-rednote"]
```

`research` 与 `mine` 不合并：research 负责把外部世界查清并交付证据；mine 负责把想法、素材或证据变成自己的可复用碎片。事实缺口可以 `mine → research → mine` 返回。

### 2. 面向人的方案

```mermaid
flowchart LR
    need["活动 / 培训 / 工作坊 / 合作 / 项目需求"] --> grill["507-grill<br/>确认受众、边界与取舍"]
    grill --> frame["507-frame<br/>正式方案"]
    frame -->|"进一步形成软件产品需求"| prd["507-prd<br/>code/"]
    frame -->|"需要追踪"| issue["507-issue<br/>code/"]
```

`frame` 服务“人如何理解、批准和行动”；具体软件产品应表现为什么行为、如何验收，归 `507-prd`。frame 不在写方案过程中重新承担用户决策确认，缺口返回 grill。

### 3. 视频

```mermaid
flowchart LR
    reference["参考视频"] --> breakdown["507-breakdown<br/>可核验拉片包"]
    breakdown -->|"挖内容、观点、经验"| mine["507-mine"]
    breakdown -->|"借结构、镜头、字幕、节奏"| remix["507-remix"]
    remix -->|"成熟原创创作包"| production["507-video<br/>制作 · Studio 审片 · 渲染 · 验收"]
    confirmed["已确认视频目标 / 成熟内容"] --> production
    narration["507-stage<br/>视频旁白内容包"] -->|"需要本地 TTS"| narrate["507-narrate<br/>配音 · 真实时长 · manifest"]
    narrate --> production
    narration -->|"真人配音 / 已有声音 / 无旁白"| production
    assets["授权素材 / 现有视频项目"] --> production
    production --> master["本地母版 + 交付回执"]
```

`breakdown` 负责参考片取证；`mine` 消费内容；`remix` 消费创作手法；`video` 消费成熟内容/创作包和授权素材，止于经审片与验收的本地母版。用户自己的录像只作为成片素材时直接进入 `video`，不先跑完整拉片。

## 冶金主链

```text
mine（挖掘） → fuse（融合） → forge（锻造）
素材变碎片       碎片变候选 idea   已确认创意变书面主稿
01-碎片/         02-创意/候选/     03-作品/

cast（铸造）与 fuse 平行：成熟碎片簇 → 04-知识库/主题页
```

- **mine** 不做系统外搜、不产选题、不写正文；
- **fuse** 比较竞争解释并产候选，不替用户拍板中心判断；
- **forge** 只在写作合同和证据承重成立后成文；
- **cast** 只聚合碎片链接与元信息，不把主题页写成长文。

## Skill 边界

### `507-mine` 碎片挖掘

输入是用户想法、指定素材、research 证据交接或 `video_completed` 拉片包；先查既有碎片/作品/知识库去重和互链，再产可复用碎片、观点与材料交接。跨来源核实、时效查证或反例搜索进入 research 后返回。

### `507-fuse` 候选融合

比较碎片背后的支持证据、反例、替代解释和边界，材料确有竞争路径时产 2～5 条候选 idea；材料只支持一条时说明收敛理由。用户拥有的中心判断选择通过 grill 完成，Agent 再按既有交付目标路由到 forge 或 stage。

### `507-cast` 知识铸造

把成熟碎片簇聚合成 `04-知识库/` 主题页，并同步知识图谱与索引。主题结构涉及用户知识组织取舍时通过 grill 确认；不够成熟时继续留在碎片图谱生长。

### `507-forge` 书面成文

把已确认创意、写作合同和承重证据统一写成可发布主稿。外部事实缺口进 research，碎片缺口进 mine，竞争解释进 fuse，中心判断取舍进 grill；完成后可直接结束或进入 rednote/stage。

### `507-stage` 现场讲述

把已确认的听众、场景、时长、目标和内容编排成演讲稿、PPT 逐页稿、课程、企业培训内容或视频旁白内容包。每页/每段只推进一个认知台阶；内容未收口时不进入视觉制作。成熟逐页内容进入 `507-ppt`；成熟视频旁白需要本地 TTS 时进入 `507-narrate`，已有真人/现成音频或无需旁白时可直接进入 `507-video`。

### `507-ppt` 视觉幻灯片

消费成熟逐页内容包，按显式选择或 officecli 能力生成可编辑 `.pptx` 或离线单文件 HTML；页面组件与六个设计方向在双载体保持内容映射与风格辨识，并交付 notes、alt、来源/notice 与载体验证证据。不编排未收口内容，不做小红书图卡。

### `507-narrate` 本地配音

消费成熟旁白与已授权、已在 Voicebox 由人确认的声音档案，通过本地 REST API 按 `daily`（Qwen 0.6B）或 `precision`（Qwen 1.7B）生成配音，两者默认以 `1.2×` 保留音高变速；按最终 WAV 真实帧数与时长输出可被视频时间线消费的 `narration-manifest.json`。不创建声音档案、不写稿、不使用 MCP，也不制作或发布视频。

### `507-frame` 人类方案

消费 grill 已确认的需求与边界，写活动、培训、工作坊、合作提案或项目计划。写法、章节和呈现由 Agent 自主完成；用户意图缺口返回 grill，软件产品规格进入 PRD。

### `507-breakdown` 视频拉片

将一个视频经 MiniMax-M3 整段理解、本地文本定位、受限视觉搜索、自适应抽帧和图片证据回写，编译成 validator 通过的 `video_completed` 拉片包。时间窗只能由本地证据承重。

### `507-remix` 视频借鉴重组

只消费一个或多个完成拉片包，借结构、叙事、镜头、字幕和节奏模式，明确不借逐句内容、人物身份和品牌资产，输出人读创作包与工具无关 `prompt-pack.json`；需要进入制作时补齐声音/时间来源、证据、素材和隐私边界，再交给 `507-video`，不直接生成成片。

### `507-video` 视频制作

消费已确认的视频目标、成熟内容、`507-narrate` 本地配音包、真人/已有声音、`507-remix` 原创创作包、授权素材和现有项目。当前首选 Remotion，负责制作合同归一、素材清单、真实时间基准、字幕/音频、Studio 审片循环、当前版本明确确认后的渲染，以及技术和视觉验收；止于本地母版与交付回执，不负责生成克隆声音、平台登录或发布。

### `507-rednote` 社交视觉摘要

把成熟书面主稿提炼为一页一个观点的视觉摘要，以编辑杂志或瑞士国际主义视觉系统生成 3:4 图卡、HTML、联系表和渲染清单；可把用户选定短视频放入动态图片槽并打包 Live Photo，也可生成独立构图的公众号 `21:9 + 1:1` 封面对。入选观点逐页映射来源，未入选的重要内容记录去向；不负责长视频剪辑、公众号正文、账号登录和发布。

## 产物接力

| 上游产物 | 可被谁消费 | 说明 |
| --- | --- | --- |
| research 证据交接 | mine / forge / stage / grill | 外部事实与来源边界 |
| mine 碎片与材料交接 | fuse / cast | 观点、经验、问题和证据关系 |
| fuse 候选 idea | grill → forge / stage | 先确认中心判断，再按交付目标成文 |
| cast 主题页 | fuse / 直接查阅 | 知识入口，不是文章正文 |
| forge 书面主稿 | rednote / stage / 直接发布 | 唯一正文真相源 |
| breakdown 拉片包 | mine / remix | 内容与创作手法分流 |
| stage 视频旁白内容包 | narrate / video | 需要本地 TTS 时进入 narrate；真人配音、已有声音或无旁白时直接进入 video |
| narrate 本地配音包 | video | 分段 WAV、真实起止时间、生成参数、授权声明与文件哈希 |
| remix 创作包 | video | 补齐制作交接后的蓝图，不是最终成片 |
| video 本地母版 + 交付回执 | 用户 / 授权后的发布流程 | 已审片、已验证，不含平台上传 |
| frame 正式方案 | PRD / issue / 人类决策 | 面向人的行动载体 |
| rednote 社交视觉包 | 授权后的发布流程 | 3:4 图卡、HTML、联系表、清单，以及按需生成的 Live Photo 或公众号封面对 |

## 出口纪律

- 每个 skill 可独立触发，不强制走完整链路。
- 每个 skill 声明完成信号、产物、候选出口与回退条件；出口可以有多个。
- Agent 根据用户已表达的目标选择下一 skill 并说明理由，不让用户选择 `forge / stage / frame / remix` 等内部名称。
- 真正属于用户的内容判断、方案边界和发布承诺统一进入 `507-grill`；工程、格式、测试与渲染细节由 Agent 自主完成并告知用户。
- 共享知识库目录与流水线纪律以目标 vault（知识库）的 `AGENTS.md` 和 README 为准。

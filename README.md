# 507 Skills

一套围绕 507 个人工作法设计的 agent skill 系列。按**两条工作流 + 通用层**组织。

核心目标不是"多功能"，而是把 507 已经稳定有效的工作方式做成可复用入口。

## 目录结构

```
507/
├── write/    写作工作流（素材 → 碎片 → 选题 → 成品）
├── code/     代码工作流（对齐 → 方案 → 实现 → 体检）
├── common/   通用 skill（两条流都用）
└── README.md 本文件
```

## write/ 写作工作流

写作流的主链是 **mine → fuse → forge**（冶金隐喻：挖矿 → 熔炼 → 锻造），外加平行的沉淀支线 cast、视频支线 breakdown/remix、和成文层的变体 stage/frame。

```
【入口/挖掘层】→ 产碎片进 vault 01-碎片/
  mine        吃三种入口（507想法/外部文章/视频拉片内容）
              先看 vault → 有目的外搜正反例 → 产碎片，边产边落碎片流水线
  breakdown   你指定视频 → 拉片包（不外搜，拉完给 mine 挖内容）

【融合层】→ 两条平行分支
  fuse        碎片 → 候选 idea（进 02-创意/候选/）     ← 走向"写出来"
  cast        碎片簇 → 知识库主题页（进 04-知识库/）   ← 走向"系统化沉淀"

【成文层】→ 基于想法手动分流，产成品进 03-作品/
  forge       ≥1 idea（+可选碎片/多创意）→ 长文（博客/公众号/专栏）
  stage       多 idea + 多碎片组合 → 讲稿/PPT/课程稿/企业培训
  frame       需求（+参考方案）→ 方案/计划/提案
  remix       拉片包（+碎片/idea 增色）→ 视频创作包
```

**主链核心动作**：mine 挖碎片 → fuse 融成候选 idea → 507 审 → forge 锻成长文。

**关键边界**：
- mine 不产选题（归 fuse）、不写正文（归 forge）
- fuse 不挖碎片（归 mine）、不写正文（归 forge）
- cast 和 fuse 平行（都从碎片聚合，fuse→选题，cast→知识库页）
- 成文层四个（forge/stage/frame/remix）靠 507 基于想法手动分流

## code/ 代码工作流

```
grill(对齐) → blueprint(画 PRD 蓝图) → workorder(开 issue 工单) → prototype(验证) → 实现 → inspection(体检)
                                                              ↑
                                                        setup(项目初始化/巡检)
```

| skill | 解决什么 |
|---|---|
| `507-ground` | 代码项目初始化/巡检（AGENTS.md、doc/、术语表、决策档案） |
| `507-blueprint` | 对话/方案 → PRD 需求规格（承接 grill→dgoal 的中间规格化层） |
| `507-workorder` | 任务 → GitHub issue 工单（正向拆 issue + 反向 bug 转 issue，可被 AI 领取） |
| `507-inspection` | 代码库架构体检，找"加深机会" |
| `507-mockup` | 可丢弃原型，正式实现前回答一个具体问题 |

## common/ 通用 skill

场景无关，两条流都用：

| skill | 解决什么 |
|---|---|
| `507-grill` | 开工前对齐的决策树追问，把改动/方案问透，沉淀术语/决策/经验 |
| `507-research` | 调研外部参照物（项目/文章/库）的真实机制 + 借鉴意义判断 |
| `507-teach` | 概念解释器，用各种通俗易懂的话讲懂一个概念（默认不落盘） |

## 命名约定

write/ 的 skill 用**动作隐喻**命名（冶金/影视工序），成链：

- **mine**（挖矿）→ **fuse**（熔炼）→ **forge**（锻造）— 文字内容主链
- **cast**（铸造）— 碎片浇铸成知识库主题页
- **breakdown**（拆片）+ **remix**（混剪重组）— 视频支线
- **stage**（上台）— 内容搬上舞台讲出去
- **frame**（框定）— 把需求框成结构化方案

code/ 的 skill 用**建造隐喻**命名，同构于建造链"设计院画图→施工队施工→监理验收"的角色分离：

- **ground**（奠基）— 项目初始化
- **blueprint**（画蓝图）— 把方案落成 PRD 需求规格
- **workorder**（开工单）— 把任务落成可领取的 GitHub issue 工单
- **mockup**（样板）— 用可丢弃代码试探假设，锚回"验证设计的试做件"原义
- **inspection**（验收巡检）— 架构体检，找浅模块加深

核心同构：建造链"施工外包"↔ code 层"实现外包给 prompts"——code 层只管画图、试做、验收，不碰实现。

common/ 的 skill 保留原名（grill/research/teach 已是场景无关的动作名）。

## 系列纪律

- 每个 skill 都是**可独立触发**的入口，不强制走完整条链。
- 阶段之间用"输出物"衔接：mine 的碎片 → fuse 的候选 idea → forge 的长文。
- 写作流 skill 共享 vault 的目录结构（`01-碎片/` `02-创意/` `03-作品/` `04-知识库/`）和碎片/选题/知识库流水线纪律（见 vault `AGENTS.md`）。
- 通用 skill（grill/research/teach）在两条流里扮演不同角色，不重复建。

## 边界（这些不在这个系列里）

- `dteam`（多角色实施）：当 implementation 需要后台多 agent 协作时引用，是系列外能力。
- 架构职责由系列内 `507-inspection` 承担，无外部架构评审 skill 依赖。

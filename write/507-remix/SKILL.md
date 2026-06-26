---
name: 507-remix
description: "507 的视频借鉴重组 skill。不直接读原视频，消费一个或多个 breakdown 的拉片包，自动抽取可借鉴手法，重组为原创创作包；可叠加碎片/idea 增色。输出人读版文档 + 工具无关的 prompt-pack.json。创作包归宿 03-作品/{选题}/视频/。Use when user mentions 把这些拉片组合成原创, 借这些视频做一个新视频, 视频借鉴重组, 视频重组, 原创创作包, 视频二创, 二创视频, 视频翻拍, 重组视频, 借鉴视频手法, 混剪重组, 视频混剪, 创作包, 提炼视频手法, remix, video remake, recombine, video remix, mashup."
---

# 507 混剪（remix）

这个 skill 负责：**把别人的手法，重组为 507 自己的新视频创作包。**

## 输入

- 一个或多个 `507-breakdown` 工作区
- 你的创作目标：
  - 主题
  - 平台
  - 时长
  - 风格
  - 想借什么
  - 明确不借什么

## 输出

```text
03-作品/{选题}/视频/{project-name}/
├── brief.md
├── borrow-map.md
├── structure.md
├── storyboard.md
├── style-lock.md
└── prompt-pack.json
```

- 创作包是**作品产出的一部分**，与课程 PPT 稿同性质，归宿在作品主轴 `03-作品/{选题}/视频/`，不再使用顶层 `video-remake/` 目录
- `md` 给人看
- `json` 给后续执行器吃
- `prompt-pack.json` 必须**完全工具无关**

## 职责边界

它不做：
- 下载原视频
- 重跑字幕 / ASR / OCR / 抽帧
- 直接生图或生成成片
- 绑定某个具体模型或视频工具

## 执行纪律

1. 默认全量读取所有输入拉片包，再自动挑借用项。
2. `borrow-map.md` 自动生成，用户只负责追加约束。
3. 人读版讲清楚“借了什么、为什么借、不借什么”。
4. 机器版只保留稳定结构字段，不写某个模型专用 prompt。

## 参考文件

先读这些：
- `README.md`
- `references/remake-method.md`
- `assets/prompt-pack.schema.json`

## 给 agent 的工作方式

1. 先读所有输入拉片包的 `meta.md / breakdown.md / breakdown.json`。
2. 从 `breakdown.json` 抽取结构、字幕/UI、镜头、节奏等机器字段。
3. 从 `breakdown.md` 抽取人读摘要、可借鉴理由和不该借的人工修订信息。
4. 识别冲突项和不该混用的项。
5. 先写 `borrow-map.md`，再写 `structure.md / storyboard.md / style-lock.md`。
6. 最后按 schema 产出 `prompt-pack.json`。

## 推荐工作流（与 `507-breakdown` 联用）

拉片包归宿 vault 的 `05-视频拉片/` 取证档案区；本 skill 的创作包归宿作品主轴 `03-作品/{选题}/视频/`。`--output-dir` 必须显式指定到作品选题目录。

```bash
# 1. 拉片，产物进 05-视频拉片/ 档案区
python3 ../507-breakdown/scripts/video_pull.py run --video <url-or-path> --output-dir video-pull
# 产物：05-视频拉片/<video-name>/

# 2. 从拉片包提炼 derived 碎片进 01-碎片/（由 agent 读 breakdown 后手动归纳，这是真正“入网”的部分）

# 3. 本 skill 重组创作包，产物进作品主轴
python3 scripts/video_remake.py run \
  --pull-dir 05-视频拉片/<video-name> \
  --project-name "<theme>" \
  --theme "..." --platform "..." --duration "..." --style "..." \
  --output-dir 03-作品/<选题slug>/视频
# 产物：03-作品/<选题slug>/视频/<project-name>/
```

---
name: 507-breakdown
description: "507 的视频拉片 skill（不外搜，只取证）。输入视频链接或本地视频，跑本地取证链路（下载、字幕/ASR/OCR、抽帧、联系图），产出可复用拉片包；拉完后交给 mine 挖内容判断。主攻 talking-head / tutorial（口播/教程）视频。拉片包归宿 05-视频拉片/。Use when user mentions 拉片, 拉一个片, 拆解这个视频, 拆视频, 看看这个视频怎么做的, 分析这个视频怎么剪的, 视频借鉴, 视频拆解, 视频分析, 取证视频, 视频取证, 视频结构分析, 口播视频拉片, 教程视频拉片, 帧抽取, 抽帧, 字幕提取, breakdown, video pull, video breakdown, video analysis, shot breakdown, transcript extraction."
---

# 507 拆片（breakdown）

这个 skill 只做一件事：**把一个视频稳定拆成可复用的拉片包**。

## 适用场景

当 507 说这些时进入：
- “拉一下这个视频”
- “看看这个视频是怎么做的”
- “帮我拆这个视频”
- “分析这个口播视频怎么剪的”
- “我想借鉴这个视频”

## 不做什么

- 不直接复刻视频
- 不直接生图或生成成片
- 不吃多个视频做原创组合（那是 `507-remix`）

## 输入契约

第一版一次只处理**一个视频**：
- 一个视频 URL
- 或一个本地视频 path（路径）

## 推荐工作流（与 `507-remix` 联用）

拉片包归宿在 vault 的 `05-视频拉片/` 取证档案区；remake 创作包归宿在作品主轴 `03-作品/{选题}/视频/`（创作包是作品的一部分，与课程 PPT 稿同性质）。

```bash
# 1. 拉片，产物进 05-视频拉片/ 取证档案区
python3 scripts/video_pull.py run --video <url-or-path> --output-dir video-pull
# 产物：05-视频拉片/<video-name>/

# 2. 从拉片包提炼 derived 碎片进 01-碎片/（这是真正“入网”的部分，由 agent 读 breakdown 后手动归纳）

# 3. 重组创作包，产物进作品主轴
python3 ../507-remix/scripts/video_remake.py run \
  --pull-dir 05-视频拉片/<video-name> \
  --project-name "<theme>" \
  --theme "..." --platform "..." --duration "..." --style "..." \
  --output-dir 03-作品/<选题slug>/视频
# 产物：03-作品/<选题slug>/视频/<project-name>/
```

可选：
- `video_type`：手动覆盖自动判定
- `output_dir`：输出目录
- `lang`：字幕 / ASR 语言
- `title_hint`：标题提示
- `force`：显式允许覆盖旧工作区

## 输出契约

默认输出一个独立工作区（归宿在 vault 的 `05-视频拉片/` 外部视频取证档案区）：

```text
./05-视频拉片/{video-id-or-slug}/
├── raw/
│   ├── video.*
│   ├── subtitles/
│   ├── asr/
│   ├── ocr/
│   ├── frames_uniform/
│   ├── frames_scenecut/
│   ├── contact_sheets/
│   ├── manifest.json
│   └── windows.jsonl
├── meta.md
├── transcript.md
├── breakdown.md
└── breakdown.json
```

- `md`（说明文档）给人看
- `json`（结构化数据）给机器吃
- 默认不覆盖旧目录

## 执行纪律

### 1. 先取证，再分析

脚本只做确定性的取证和预处理：
- 下载视频
- 提取字幕 / ASR / OCR
- 抽帧
- 拼联系图
- 生成 `raw/manifest.json`

默认脚本只生成**证据包与模板**；agent 负责在此基础上完成最终拉片：
- 判定 `video_type`
- 读取证据
- 填写或增强 `meta.md / transcript.md / breakdown.md / breakdown.json`

### 2. 成功一路跑完，失败再回到对话

- 成功时不要中途停下来等确认
- 失败时明确报出：失败在哪一层、拿到了什么、没拿到什么
- 不要在失败时自动脑补半成品结论

### 3. 文字证据链四级降级

严格按这个顺序拿文字：
1. 平台原生字幕
2. 平台自动字幕
3. 本地 ASR
4. 帧内 OCR

规则：
- 前一层成功，就不要继续混用下一层
- 任何一层失败都记进 `raw/manifest.json`
- 禁止用视觉理解去补台词

### 4. 视觉证据用双采样 + 双视图

- `1 fps` 均匀抽帧
- `scene-cut` 场景切换抽帧
- 联系图用于看节奏
- 原始帧用于看细节
- 涉及字幕 / UI 小字时，必须回看原始帧

### 5. 两层分段

- 分析层：先按小窗处理，防止 agent 输入过载
- 输出层：再按语义合并，不按固定 10 秒硬切
- `raw/windows.jsonl` 只做调试依据，不给人看

## 参考文件

先读这些：
- `README.md`
- `references/pull-method.md`
- `references/tag-vocabulary.md`
- `references/analysis-playbook.md`
- `assets/breakdown.schema.json`

## 脚本入口

优先用：
- `scripts/video_pull.py check`
- `scripts/video_pull.py run --video "..."`
- `scripts/draft_pull_analysis.py --workspace "..."`（刷新证据摘要模板；不做最终语义分析）

如果脚本失败，先看：
- `raw/manifest.json`
- stderr（标准错误输出）

某些平台 URL 可能受风控限制；此时先记录失败证据，再切到本地文件或可访问直链，不要把平台限制误判成拉片逻辑错误。

## 给 agent 的工作方式

1. 先跑脚本拿证据。
2. 看 `raw/manifest.json`，确认最终文字来源和视觉材料是否齐。
3. 先读 `transcript`，再看联系图，再回看关键原始帧。
4. 按 `assets/breakdown.schema.json` 产出 `breakdown.json`。
5. 再把同一份判断写成人读版 `breakdown.md`。
6. 第一版主攻口播 / 教程；其他类型保守处理，不乱推断。

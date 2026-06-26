# 507 Video Pull

`507-video-pull` 是 507 的视频拉片 skill。

它只做一件事：**把一个视频稳定拆解成可复用的拉片包**，方便后续借鉴、比较和再创作。

## 它解决什么

- 给一个视频链接或本地视频，先把**证据链**拉下来：视频文件、字幕、ASR、抽帧、联系图。
- 默认先由脚本把证据层整理成**可复核证据包与模板**，最终拉片分析由 agent 读取证据后完成。
- 第一版主攻 `talking-head / tutorial`（口播 / 教程）视频，其他类型先走通用兜底。

## 它不做什么

- 不直接复刻视频
- 不直接生图或生成成片
- 不把多个视频自动拼成原创方案（那是 `507-video-remake` 的职责）

## 目录结构

- `SKILL.md`：skill 的定位、触发条件、执行纪律
- `scripts/`：本地取证脚本
- `references/`：拉片方法、标签词表、输出契约
- `assets/`：结构化 schema（模式）和模板

## 默认产物

一次运行默认输出一个独立工作区：

```text
./video-pull/{video-id-or-slug}/
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

## 运行原则

- 一次只处理**一个视频**。
- 成功就一口气跑完，失败再回到对话里修 skill 或补输入。
- 默认不覆盖旧工作区；需要重跑时显式传 `--force`。
- 不用视觉理解去脑补台词；拿不到文字证据就明确报出来。
- 某些平台 URL 可能有风控或需要 cookie；这种情况下优先看 `raw/manifest.json` 的失败信息，并改用本地文件或可访问直链重试。

## 与 `507-video-remake` 联用

产物分工：拉片包归宿 vault 的 `video-pull/` 取证档案区；remake 创作包归宿作品主轴 `works/{选题}/视频/`（创作包是作品的一部分）。

```bash
# 1. 拉片，产物进 video-pull/ 档案区
python3 scripts/video_pull.py run --video <url-or-path> --output-dir video-pull
# → video-pull/<video-name>/...

# 2. 从拉片包提炼 derived 碎片进 fragments/（由 agent 读 breakdown 后手动归纳）

# 3. 重组创作包，产物进作品主轴
python3 scripts/video_remake.py run \
  --pull-dir video-pull/<video-name> \
  --project-name "<theme>" \
  --theme "..." --platform "..." --duration "..." --style "..." \
  --output-dir works/<选题slug>/视频
# → works/<选题slug>/视频/<project-name>/...
```

这样拉片取证档案在 `video-pull/` 可复查，创作包作为作品产出归位 `works/` 主轴。拉片包提炼的每个借鉴点 = 一个 derived 碎片，进 `fragments/` 入网。

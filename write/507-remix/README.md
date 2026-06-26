# 507 Video Remake

`507-video-remake` 是 507 的视频借鉴重组 skill。

它不直接读原视频，只消费一个或多个 `507-video-pull` 产出的拉片包，把别人的手法整理成**自己的原创创作包**。

## 它解决什么

- 从多个拉片包里抽取可借鉴手法
- 自动生成借鉴映射、结构节拍、分镜脚本、风格锁定
- 产出既能给人看，也能给后续执行器消费的创作包

## 它不做什么

- 不下载原视频
- 不再重复跑字幕、ASR、抽帧、OCR
- 不直接生图或生成成片
- 不绑定任何特定模型或工具

## 与 `507-video-pull` 联用

产物分工：拉片包归宿 vault 的 `video-pull/` 取证档案区；本 skill 的创作包归宿作品主轴 `works/{选题}/视频/`。`--output-dir` 必须显式指定到作品选题目录。

```bash
# 1. 拉片，产物进 video-pull/ 档案区
python3 ../507-video-pull/scripts/video_pull.py run --video <url-or-path> --output-dir video-pull
# → video-pull/<video-name>/...

# 2. 从拉片包提炼 derived 碎片进 fragments/（由 agent 读 breakdown 后手动归纳）

# 3. 本 skill 重组创作包，产物进作品主轴
python3 scripts/video_remake.py run \
  --pull-dir video-pull/<video-name> \
  --project-name "<theme>" \
  --theme "..." --platform "..." --duration "..." --style "..." \
  --output-dir works/<选题slug>/视频
# → works/<选题slug>/视频/<project-name>/...
```

这样拉片取证档案在 `video-pull/` 可复查，创作包作为作品产出归位 `works/` 主轴；拉片包提炼的每个借鉴点 = 一个 derived 碎片，进 `fragments/` 入网。

## 输入

- 一个或多个 `507-video-pull` 的工作区
- 你的创作目标（主题、平台、时长、风格、想借什么、不借什么）

## 默认产物

```text
works/{选题}/视频/{project-name}/
├── brief.md
├── borrow-map.md
├── structure.md
├── storyboard.md
├── style-lock.md
└── prompt-pack.json
```

创作包是作品产出的一部分，归宿在 `works/{选题}/视频/`，不再使用顶层 `video-remake/` 目录。

## 目录结构

- `SKILL.md`：skill 的定位、触发条件、执行纪律
- `references/`：创作包字段定义、借鉴原则
- `assets/`：结构化 schema 和模板

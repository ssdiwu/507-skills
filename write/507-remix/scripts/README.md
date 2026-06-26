# scripts

`507-video-remake` 的脚本层负责读取一个或多个 `507-video-pull` 工作区，并生成一个**工具无关的原创创作包**。它同时消费 `breakdown.md` 和 `breakdown.json`：机器字段优先取 JSON，人读理由与人工修订信息优先取 Markdown。

当前入口：
- `video_remake.py run --pull-dir ...`

## 当前能力

- 读取多个拉片包中的 `meta.md` / `breakdown.md` / `breakdown.json`
- 自动汇总结构段与可借鉴模式
- 从 `breakdown.md` 提取人读摘要、可借鉴点和不建议借鉴点
- 生成：
  - `brief.md`
  - `borrow-map.md`
  - `structure.md`
  - `storyboard.md`
  - `style-lock.md`
  - `prompt-pack.json`

## 边界

- 不直接读原视频
- 不做字幕、ASR、抽帧、OCR
- 不生成模型专用 prompt
- 不调用生图或生视频工具

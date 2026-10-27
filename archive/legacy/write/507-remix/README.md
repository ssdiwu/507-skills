# 视频借鉴重组（remix）

`507-remix` 只读取并核对状态为 `video_completed` 的 `507-breakdown` 拉片包，并把可借鉴的结构、镜头、字幕、UI 与节奏重组为原创创作包。

输入必须包含 `raw/video_manifest.json`、`video_meta.md`、`video_breakdown.md` 和 `video_breakdown.json`。旧 `breakdown.json` 包不兼容。

创作包本身不是成片。需要继续制作时，`brief.md`、`storyboard.md` 与 `style-lock.md` 在交付 `507-video` 前还要补齐受众/画幅/时间与声音来源、逐节拍证据和素材缺口、事实/隐私边界，再交给 `507-video`；工具无关 `prompt-pack.json` 不写入 Remotion 或本机字段。

更多边界见 [`doc/README.md`](doc/README.md)。

# scripts

`507-video-pull` 的脚本层只负责**确定性的取证与预处理**，不负责语义判断。

当前入口：
- `video_pull.py check`：检查本地依赖
- `video_pull.py run --video ...`：执行单视频取证链路，并默认生成证据包与模板
- `video_pull.py normalize-subs --subtitle-path ... --output-path ...`：把字幕文件标准化为 `transcript.txt`
- `draft_pull_analysis.py --workspace ...`：刷新证据摘要模板，不输出最终语义分析
- `validate_breakdown.py <breakdown.json>`：校验结构、`videoType` 枚举与封闭标签词表

## 当前能力

- 下载视频或复制本地视频
- 收集平台字幕 / 自动字幕
- 本地 `faster-whisper` ASR 兜底
- `1fps` 均匀抽帧
- `scene-cut` 场景切换抽帧
- 生成高分辨率联系图
- 写 `raw/manifest.json` 和 `raw/windows.jsonl`

## 当前边界

- OCR 已有脚本链路，但前提是本机安装 `tesseract`
- `video_pull.py run` 默认生成证据层与模板
- `draft_pull_analysis.py` 仅用于证据摘要刷新或审计重放，不承担最终语义分析

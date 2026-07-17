# 视频拉片（breakdown）

`507-breakdown` 将单个视频编译为可复核的拉片包：MiniMax-M3 仅给整段语义参考；ASR/OCR 命中才会定位语义窗口，PTS 与 scene-cut 只提供本地视觉搜索点。抽帧按窗口证据调整密度，并在图片理解后核验。

## 完成契约

只有 `video_validate_breakdown.py --workspace <workspace>` 通过后，工作区才是 `video_completed`，可由 `507-remix` 消费。

```text
05-视频拉片/<video-id>/
├── video_meta.md
├── video_transcript.md
├── video_breakdown.md
├── video_breakdown.json
├── raw/video_manifest.json
└── analysis/
```

旧 `meta.md` / `breakdown.json` 包不兼容。

## 运行条件

- Python 3.10+；默认使用启动 `video_pull.py` 的当前 Python。
- `ffmpeg` 与 `ffprobe`。
- 当前 Python 已安装 `faster-whisper`；也可通过 `--asr-python <path>` 或 `VIDEO_ASR_PYTHON=<path>` 指定另一个可执行文件，优先级依次为参数、环境变量、当前 Python。
- URL 输入额外需要 `yt-dlp`；本地输入不需要。
- Tesseract 为可选 OCR（光学字符识别）增强；未安装时流水线会明确记录跳过。
- MiniMax-M3 与图片理解需要 `MiniMax_API_KEY` 环境变量。

先运行依赖检查：

```bash
python3 scripts/video_pull.py check
# 或检查单独的 ASR Python
python3 scripts/video_pull.py check --asr-python /path/to/python
```

## 使用

```bash
python3 scripts/video_pull.py run --video <url-or-path> --output-dir 05-视频拉片
# agent 根据 analysis/video_analysis_brief.md 和本地证据填写最终 video_breakdown.*
python3 scripts/video_validate_breakdown.py --workspace 05-视频拉片/<video-id>
```

MiniMax-M3 为默认必经步骤。显式 `--force-local-fallback` 只跳过 M3 **整段视频理解**，但图片理解仍需 `MiniMax_API_KEY`；未导出密钥时无法完成拉片。

设计与真实 smoke evidence 见 [`doc/README.md`](doc/README.md)。

# 视频拉片脚本

所有视频流水线脚本使用小写 `snake_case` 与 `video_` 前缀。

| 脚本 | 职责 |
|---|---|
| `video_pull.py` | 公共编排入口：取得视频、ASR、scene-cut、M3、定位、抽帧、图片理解、分析简报 |
| `video_understand_minimax.py` | MiniMax-M3 Files API + `/anthropic/v1/messages` 整段视频理解 |
| `video_locate_segments.py` | 10 秒 1 帧定位索引和本地证据候选窗口 |
| `video_extract_adaptive_frames.py` | 对候选窗口有界加密抽帧 |
| `video_describe_key_frames.py` | 关键帧图片理解 |
| `video_prepare_analysis.py` | 写 video_* 最终模板与分析简报 |
| `video_validate_breakdown.py` | 校验最终包并写入 `video_completed` |
| `video_asr_faster_whisper.py` / `video_ocr_tesseract.py` | 本地证据叶子工具 |

## 运行条件

- Python 3.10+、`ffmpeg`、`ffprobe`；
- `faster-whisper` 安装在当前 Python，或安装在 `--asr-python` / `VIDEO_ASR_PYTHON` 指定的 Python 中；
- URL 输入需要 `yt-dlp`；
- Tesseract 可选，未安装时跳过 OCR；
- `MiniMax_API_KEY` 必须由进程环境导出。

ASR Python 的选择优先级是命令行参数、环境变量、当前 Python，不读取固定虚拟环境：

```bash
python3 video_pull.py check
python3 video_pull.py check --asr-python /path/to/python
VIDEO_ASR_PYTHON=/path/to/python python3 video_pull.py run --video <url-or-path> --output-dir <dir>
```

脚本不读取、source 或打印 `~/.zshrc`。M3 失败默认使拉片失败；`--force-local-fallback` 只跳过 M3 **整段视频理解**，图片理解仍需 `MiniMax_API_KEY`。

## 验证

```bash
# ASR Python 选择和依赖状态回归
python3 test_video_pull_runtime.py

# 静态合成 M3 契约 fixture 校验（无需 API key）
python3 test_understanding_fixtures.py

# 图片响应带 Markdown JSON 围栏的回归测试（无需 API key）
python3 test_image_response_parser.py

# 严格真实 M3 上传 smoke test（默认生成 8 秒输入；需要 key）
export MiniMax_API_KEY=...
python3 test_minimax_adapter.py

# 无 key 的失败契约
python3 test_minimax_adapter.py --no-key

# 默认全链路：M3 → 定位 → 帧 → 图片 → validator → remix
python3 test_video_pipeline_e2e.py
```

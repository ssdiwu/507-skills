# 视频重组脚本

`video_remake.py` 只读取已完成的 `507-breakdown` 新契约：

```text
raw/video_manifest.json  # status=video_completed
video_meta.md
video_breakdown.md
video_breakdown.json
```

旧拉片包文件名不兼容，也没有 fallback（回退）或迁移逻辑。

```bash
python3 video_remake.py run --pull-dir <completed-pull-dir> --project-name <name> --theme <theme> --platform <platform> --duration <duration> --style <style> --output-dir <works-dir>
```

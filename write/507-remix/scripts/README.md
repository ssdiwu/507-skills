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

脚本生成以下原创创作包骨架：

```text
README.md
brief.md
borrow-map.md
structure.md
storyboard.md
style-lock.md
prompt-pack.json
```

若出口是视频成片，agent 还需按 `../SKILL.md` 补齐 `brief.md`、`storyboard.md` 与 `style-lock.md` 的制作交接字段，再交给 `507-video`。脚本不向 `prompt-pack.json` 写入具体视频引擎或本机路径。

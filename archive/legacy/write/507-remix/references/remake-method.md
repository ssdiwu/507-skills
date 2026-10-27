# 视频重组方法

`507-remix` 只读取并核对 `507-breakdown` 已完成的新拉片包：

```text
raw/video_manifest.json  # status=video_completed
video_meta.md
video_breakdown.md
video_breakdown.json
```

从 `video_breakdown.json` 读取稳定的结构与标签，从 `video_breakdown.md` 读取人读理由和不建议借鉴项。旧包不兼容。

创作包输出到 `03-作品/{选题}/视频/{project_name}/`，不绑定具体生成工具。

脚本先生成文件骨架；这些文件可供人阅读，也可按 schema 解析，但初始输出还不是完整制作合同。若当前目标是继续制作成片，agent 再在 `brief.md`、`storyboard.md` 和 `style-lock.md` 补齐 `507-video` 所需的声音与时间来源、画面证据、素材/授权缺口、事实和隐私边界；`prompt-pack.json` 保持工具无关。

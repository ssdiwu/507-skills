# 视频重组方法

`507-remix` 只消费 `507-breakdown` 已完成的新拉片包：

```text
raw/video_manifest.json  # status=video_completed
video_meta.md
video_breakdown.md
video_breakdown.json
```

从 `video_breakdown.json` 读取稳定的结构与标签，从 `video_breakdown.md` 读取人读理由和不建议借鉴项。旧包不兼容。

创作包输出到 `03-作品/{选题}/视频/{project_name}/`，不绑定具体生成工具。

---
name: 507-remix
description: "507 的视频借鉴重组 skill。只消费 video_completed 的 507-breakdown video_* 拉片包，抽取可借鉴手法并重组为原创创作包。Use when user mentions 视频借鉴重组, 原创创作包, 视频二创, remix, video remake, recombine."
---

# 507 混剪（remix）

将一个或多个已完成拉片包重组为原创视频创作包；不读取原视频，不做取证。

## 输入契约

每个输入工作区必须是：

```text
raw/video_manifest.json   # status 必须为 video_completed
video_meta.md
video_breakdown.md
video_breakdown.json
```

只接受这个新 `video_*` 契约。旧文件名没有兼容或迁移路径。

## 输出

`03-作品/{选题}/视频/{project-name}/` 下生成 `brief.md`、`borrow-map.md`、`structure.md`、`storyboard.md`、`style-lock.md` 与工具无关的 `prompt-pack.json`。

```bash
python3 scripts/video_remake.py run --pull-dir 05-视频拉片/<video-id> --project-name <name> --theme <theme> --platform <platform> --duration <duration> --style <style> --output-dir 03-作品/<选题>/视频
```

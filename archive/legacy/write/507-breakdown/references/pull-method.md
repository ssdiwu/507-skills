# 视频拉片取证方法

`507-breakdown` 的拉片不是普通总结：先由 MiniMax-M3 建立整段语义参考，再用本地证据定位与核验。

```text
video_understanding_minimax
→ video_frames_locator（每 10 秒 1 帧）
→ video_locations
→ video_frames_adaptive
→ video_frame_observations
→ video_breakdown.*
```

- M3 时间、顺序、方向不能作为事实。
- 本地 ASR、OCR、PTS 帧与 scene-cut 才能确认最终时间窗。
- 图片理解针对已定位窗口提供画面证据；对尚未定位的语义单元，它只提供受限视觉搜索点。后一种情况必须找到图片锚点并回写本地定位，否则失败。
- `video_validate_breakdown.py` 通过前，工作区不是 `video_completed`。

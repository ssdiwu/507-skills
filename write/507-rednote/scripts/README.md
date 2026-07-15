# 小红书图卡脚本

`render_rednote.py` 与 `render_style_gallery.py` 是 `507-rednote` 的内部执行脚本，不是独立产品。

## 运行条件

- Python 3.10+
- Pillow
- 本机 Google Chrome / Chromium；也可通过 `CHROME_PATH` 或 `--chrome` 指定

安装 Pillow：

```bash
python3 -m pip install Pillow
```

## 样式预览

用户未指定样式时，先渲染全部 18 套外观的“封面 + 一页正文”联系表：

```bash
python3 render_style_gallery.py \
  --spec <rednote-project.json> \
  --output-dir <小红书目录>/style-preview
```

可用 `--styles newspaper,editorial,mono` 缩小候选。完整样式与选择建议见 `../references/styles.md`。

## 正式渲染

```bash
python3 render_rednote.py --spec <rednote-project.json> --output-dir <小红书目录>
```

完成过一次全量渲染后，仅 `layoutMode: cards` 的显式卡片页、且页数/主题/头像未变化时可局部重渲染：

```bash
python3 render_rednote.py --spec <rednote-project.json> --output-dir <小红书目录> --pages 3,5
```

长文任一逻辑块变化都可能让后续物理页位移，必须全量重渲染；脚本会拒绝对已变化的长文规格执行局部渲染。

脚本会：

1. 校验 JSON 输入、本地素材、`stylePreset`，以及封面和正文逻辑块的 `sourceMap` 保真映射。
2. 按选定样式把图片转为 `data:` URI，生成不依赖外部资源的 `rednote.html`。
3. 长文模式按真实排版高度自动把逻辑段落装入物理页；卡片模式保持显式逐页。
4. 用 750×1000 CSS 像素、2 倍设备比例渲染为 1500×2000 JPG。
5. 检查页面溢出、动态页数、尺寸和文件完整性。
6. 生成 `contact-sheet.jpg` 与包含物理页来源映射的 `render-manifest.json`。

测试：

```bash
python3 -m unittest scripts/test_render_rednote.py
```

完整烟测会调用本机 Chrome：

```bash
python3 scripts/render_rednote.py \
  --spec scripts/fixtures/sample-project.json \
  --output-dir /tmp/507-rednote-smoke
```

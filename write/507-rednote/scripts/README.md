# 社交视觉包脚本

`render_rednote.py` 与 `render_style_gallery.py` 是 `507-rednote` 的内部执行脚本，不是独立产品，也不负责安装环境依赖。

## 运行条件

静态图卡和公众号封面对：

- Python 3.10+
- Pillow
- 本机 Google Chrome / Chromium；可通过 `CHROME_PATH` 或 `--chrome` 指定

动态图片槽额外需要：

- `ffmpeg` 与 `ffprobe`
- macOS 和 `makelive` 0.6.2+，用于 Live Photo `.pvt` 打包

参考安装命令：

```bash
python3 -m pip install Pillow
brew install ffmpeg
uv tool install makelive==0.6.2
```

脚本不会执行这些安装命令。外部工具的来源与许可证记录见 [`../third-party-notices.md`](../third-party-notices.md)。

## 视觉系统预览

未指定视觉系统和主题时，渲染全部“封面 + 一页正文”候选：

```bash
python3 render_style_gallery.py \
  --spec <rednote-project.json> \
  --output-dir <小红书目录>/style-preview
```

可用 `--themes editorial-paper,swiss-blue` 缩小候选。预览会按主题自动切换对应视觉系统，不改观点文案。

## 正式渲染

```bash
python3 render_rednote.py \
  --spec <rednote-project.json> \
  --output-dir <小红书目录>
```

有动态图片槽、且 `makelive` 不在 PATH 时：

```bash
python3 render_rednote.py \
  --spec <rednote-project.json> \
  --output-dir <小红书目录> \
  --makelive /absolute/path/to/makelive
```

纯静态项目完成过一次全量渲染后，可以局部重渲染：

```bash
python3 render_rednote.py \
  --spec <rednote-project.json> \
  --output-dir <小红书目录> \
  --pages 3,5
```

未选页面的规格或全局配置变化时，脚本会拒绝局部渲染。含动态图片槽或公众号封面对时必须全量渲染。

文章模式的物理 `pages`（页面数组）必须在正式渲染前已经由连续正文经真实浏览器布局重排完成；脚本不会把字符数估算、旧页分组或临时候选当成页数变化。页数变化必须全量渲染；脚本先在同文件系统的隔离候选目录完成全部页面、联系表和 `manifest`（清单），验证通过后再事务式发布，届时才删除旧页。

全量发布管理 `rednote.html`（单文件网页）、联系表、清单、图卡、公众号封面对和动态页产物；局部发布只更新选中页面、`HTML`（网页）、联系表和清单，未选页面保持原文件。清单最后发布，并只记录相对来源或带摘要的外部来源标识，不写本机绝对路径；生成或发布失败时自动恢复上一版，只有恢复本身失败时才保留候选与备份并报告位置。

## 脚本负责

1. 校验文章模式或视觉摘要规格、来源映射、排除内容去向、视觉系统与主题；文章模式拒绝逐页观点、布局和摘要结构，全文逐段覆盖仍由 Agent 在渲染前后单独核验。
2. 把本地静态素材和动态首帧内嵌到单文件 `rednote.html`。
3. 用真实浏览器检查溢出、字号下限和标题间距；文章页尾由画布底部留白统一控制，最后一个内容块的外边距不再重复计入溢出。
4. 文章模式导出 1500×2000 封面与 1440×2400 正文，摘要模式导出 1500×2000 图卡，并生成不裁切页面的联系表与新鲜度 manifest；全量渲染会清除超出当前页数的旧页面。
5. 按需导出 2100×900、1080×1080 公众号封面对和组合预览。
6. 用 `ffprobe` 校验短视频，以 `ffmpeg` 抽首帧并合成整卡 MOV。
7. 调用外部 `makelive --pvt` 生成 Live Photo 包；缺失或失败时不写完成 manifest。

## 测试

单元测试：

```bash
python3 -m unittest scripts/test_render_rednote.py
```

静态与公众号集成烟测：

```bash
rednote_smoke_dir="$(mktemp -d)"
python3 scripts/render_rednote.py \
  --spec scripts/fixtures/sample-project.json \
  --output-dir "$rednote_smoke_dir/507-rednote-smoke"
```

文章模式集成烟测：

```bash
rednote_article_smoke_dir="$(mktemp -d)"
python3 scripts/render_rednote.py \
  --spec scripts/fixtures/sample-article-project.json \
  --output-dir "$rednote_article_smoke_dir/507-rednote-article-smoke"
```

动态图片槽测试会在临时目录用 `ffmpeg` 生成合成视频，不提交二进制 fixture。完整 Live Photo 端到端还需要在 macOS Photos 或 iPhone 发布路径验证 `.pvt` 可识别。

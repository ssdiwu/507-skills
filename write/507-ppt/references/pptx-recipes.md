# PPTX recipe

## 环境路由

运行 `python3 scripts/probe_environment.py`：输出 `officecli: true` 时默认载体为 `.pptx`；`--simulate-missing-officecli` 输出 HTML 路由。脚本不安装依赖。

## 生成

```bash
python3 scripts/generate_pptx.py --style swiss --output examples/collaboration-swiss.pptx
python3 scripts/generate_pptx.py --style magazine --output examples/collaboration-magazine.pptx
```

生成器消费公开 `fixture`（测试样例）的四页页面种类：封面、图文、三项结构、引用收束；每页写 `speaker notes`（讲者备注），图文页写本地 `SVG`（可缩放矢量图）的 `alt text`（替代文本）。字体按中文/拉丁角色分别设置；瑞士风使用无衬线与单锚点色，杂志风使用 `Songti`（宋体）/`Georgia`（乔治亚字体）标题角色、暖色与深浅节奏。生成过程只写同目录候选文件，关闭并通过下述完整验证后才原子替换目标。

## 验证

```bash
python3 scripts/validate_pptx.py examples/collaboration-swiss.pptx
python3 scripts/validate_pptx.py examples/collaboration-magazine.pptx
```

生成脚本会自动调用验证器；上述命令用于独立复验。验证器检查 `OpenXML schema`（OpenXML 结构模式）、0 个 `format issues`（格式问题）、图片 `alt text`（替代文本）、每页 `notes`（讲者备注），并检查逐页截图的尺寸、非空白状态和设计方向主题色。独立复验可用 `--screenshots-dir`（截图目录参数）保留截图；仓库样例的固定逐页截图和页面映射存入对应 `manifest`（清单），作为溢出和内容对照证据。

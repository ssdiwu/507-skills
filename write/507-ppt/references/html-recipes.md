# HTML recipe

HTML 是离线单文件横向演示。生成器消费 content v3 与 visual-plan v1，只生成静态通过的隔离候选；真实浏览器证据通过后，由独立晋升步骤原子替换当前成品与 evidence。

```bash
python3 scripts/generate_html.py \
  --input scripts/fixtures/system-showcase.json \
  --plan scripts/fixtures/system-showcase.visual-plan.json \
  --candidate-only \
  --output /tmp/system-showcase.candidate.html

python3 scripts/promote_html.py \
  --candidate /tmp/system-showcase.candidate.html \
  --input scripts/fixtures/system-showcase.json \
  --plan scripts/fixtures/system-showcase.visual-plan.json \
  --evidence-source /tmp/system-showcase-browser-evidence \
  --evidence-dir examples/system-showcase-html-evidence \
  --output examples/system-showcase.html
```

旧命令 `--style swiss` 一轮兼容为 preset 简写；新流程优先使用 `--plan`。

## 三轴映射

- slide 保留 `data-component / data-presentation / data-language / data-treatment / data-support`；
- 组件使用语义 DOM；视觉呈现只改变布局与表现，消费设计语言 CSS token；
- compatibility resolver 生成 suppression，例如 table 关闭背景网格；
- adapted/unsupported 不得由 HTML 自行伪装为 native。

## 中文换行

`textFlow.units` 输出为不可断 `.phrase`，unit 之间插入 `<wbr>`；每个字段带 `data-text-path`。路径覆盖 item、node、asset caption、chart 与 table cell；`preferSingleLine` 先真实测量一行宽度，放不下才释放语义边界。标题 `balance`、正文 `pretty` 只作辅助。

## 语义、交互与退化

- 标题、正文、图表标签、表格、素材说明和导航留在 DOM；
- 原生 chart 语义以可读标签与结构化 DOM/SVG 表达；table 使用真实 `<table>`；
- 键盘、按钮、滚轮、触控、页码和当前页状态可复验；
- JS 失败、静态模式、减少动态和装饰层失败时仍可阅读；
- 无远程 CDN，素材嵌入 data URI，并保留 alt/caption；
- 动画使用确定性状态，不承载事实或导航。

## 验证

```bash
python3 scripts/validate_html.py examples/system-showcase.html
bash scripts/test_html.sh
```

浏览器矩阵逐页使用 `?instant=1&slide=N`，只有 current ID、status、零转场、offset、overflow、phrase、每个 `maxLines` 路径的真实行数、截图 hash 和全部 profile 真实字段都通过才生成 `html-browser` 报告。移动端完整画幅不等于文本阅读通过；若字号不足，只能报告为构图预览。

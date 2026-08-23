# PPTX recipe

## 环境路由

`python3 scripts/probe_environment.py` 输出 `officecli: true` 时可生成 PPTX；脚本不安装依赖。当前实现按已安装 officecli schema 调用原生 shape、picture、chart、table 与 notes，不猜 API。

## 生成

```bash
python3 scripts/generate_pptx.py \
  --input scripts/fixtures/system-showcase.json \
  --plan scripts/fixtures/system-showcase.visual-plan.json \
  --evidence-dir examples/system-showcase-pptx-evidence \
  --output examples/system-showcase.pptx
```

旧 `--style swiss` 保留一轮并映射为 preset；新生成优先 `--plan`。生成器先写候选、关闭 resident、运行完整验证，保存逐页截图 evidence 后才替换目标；失败保留旧产物并清理本轮 evidence。

## 可编辑对象

- 标题、正文、metadata 与数字使用原生 text shape；
- media 使用带 alt 的 1～3 个 picture；缺失路径直接失败，不能静默换成项目占位图；
- chart 使用原生 PowerPoint chart，categories/series 按页 read-back；多序列保持独立 series；
- table 使用原生 PowerPoint table，行列、单元格、padding、wrap、字体、填充与边线可 read-back；textFlow cell 在建表后逐格回写；
- notes 每页写入；不以截图替代数据组件。

Visual presentation 的 PPTX 状态来自注册表。`editorial-print-led / hand-drawn-explainer` 当前为 adapted，以可编辑原生线条和 shape 保持层级，不复制不可编辑纹理；manifest 必须记录。

## 中文语义换行

visual-plan 的 `textFlow.units` 保护不可拆短语；PPTX 只在 `lines` 指定的 unit 边界写 `\v` 软换行。指定 textFlow 后关闭 Office 自动 wrap，显式软换行仍保留；放不下就调整容器或 lines，不能拆词或无限缩字。该入口同样覆盖 item、node、caption、chart category/series 与 table cell。

## 验证

```bash
python3 scripts/validate_pptx.py examples/system-showcase.pptx \
  --fixture scripts/fixtures/system-showcase.json \
  --plan scripts/fixtures/system-showcase.visual-plan.json \
  --screenshots-dir examples/system-showcase-pptx-evidence
```

验证包括 OpenXML schema、零 format issues、可见文字、notes、alt、语言字体、原生 chart/table 数量与内容 read-back、13 张 16:9 非空截图、各页语言主题色及人工中文换行检查。`issues=0` 不等于排版自然，最终必须看截图。

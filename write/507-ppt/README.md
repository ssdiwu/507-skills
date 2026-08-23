# 507-ppt：三轴视觉幻灯片制作

`507-ppt` 消费成熟逐页内容，按“语义组件 × 设计语言 × 视觉呈现”建立 visual-plan，先用真实内容原型确认，再输出可编辑 `.pptx` 或离线单文件 HTML；不承担演讲内容编排。

## 目录

- `SKILL.md`：触发、输入门、原型、中文换行、双载体与完成边界；
- `references/`：三轴系统、组合质量、排版、来源、manifest 与载体验证；
- `scripts/design_system.py`：13 个语义叶组件、6 个基础语言、8 个呈现族、旧 preset 与兼容矩阵；
- `scripts/visual_plan.py`：visual-plan v1、组合解析、原型代表页与旧入口映射；
- `scripts/text_layout.py`：HTML/PPTX 共用 phrase-aware（短语感知）换行合同；
- `scripts/generate_html.py / promote_html.py / generate_pptx.py`：HTML 候选—浏览器证据—晋升，以及完整验证后原子替换的 PPTX；
- `scripts/generate_prototypes.py / finalize_prototype.py`：2～3 个真实内容候选与用户选择的哈希化批准链；
- `examples/`：legacy 兼容样例、13 组件 showcase、8 呈现 pairwise 压测与三轴双载体证据。

## 核心合同

- content v3 保存组件和事实；visual-plan v1 保存设计语言、逐页呈现、treatment、prototype manifest 与 nested textFlow；manifest v2 保存 resolver 与机器报告可复验的交付证据。
- 一套 deck 只有一个基础设计语言，允许受控 treatment；呈现逐页变化但必须兼容组件。
- 旧 `swiss / magazine / cobalt / clay / forest / noir` 是 preset，不是底层样式枚举。
- 核心组合双载体；adapted 明示，unsupported 停止。
- 用户未锁定成熟 preset 时，默认推荐 2～3 组并显示封面、最密页、data/media 代表页；混合后先确认合并原型。
- 中文能一行则一行，换行只发生在词语/语义短语边界，并以最终 HTML/PPTX 截图验收。

## 验证入口

```bash
python3 -B -m unittest discover -s scripts -p 'test_*.py' -v
bash scripts/test_html.sh
python3 scripts/generate_pptx.py --input scripts/fixtures/system-showcase.json --plan scripts/fixtures/system-showcase.visual-plan.json --output examples/system-showcase.pptx
```

HTML 检查语义、交互、响应式、退化、phrase 换行和来源；PPTX 检查 schema、issues、notes、alt、原生 chart/table、字体、主题色、逐页截图与 evidence 保留。最终 manifest v2 要求每页都有 `screenshot-verified` 换行证据。具体说明见对应 reference 与 `scripts/README.md`。

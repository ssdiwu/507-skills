# 507-ppt 脚本

此目录存放确定性脚本：三轴注册表、视觉计划、中文短语换行、真实内容原型、`HTML`（网页）/`PPTX`（PowerPoint 演示文稿）生成与验证、`manifest`（清单）、来源报告和组合/内容报告。逐页截图内容检查与联系表使用 `Pillow`（图像处理库）；演示文稿生成、原生 chart/table（图表/表格）和截图使用 `officecli`（办公文档命令行工具）。样例和验证入口见 `../examples/README.md`（样例说明）。

## 核心模块

- `design_system.py`：13 个语义叶组件、6 个设计语言、8 个视觉呈现、4 个 treatment、兼容矩阵、抑制规则和 6 个 legacy preset（旧预设）。
- `visual_plan.py`：visual-plan v1 的建立、校验、解析与代表页选择；组件兼容、载体支持和降级均从注册表计算。
- `text_layout.py`：HTML/PPTX 共用的 phrase-aware（短语感知）换行校验与输出。
- `generate_prototypes.py` / `finalize_prototype.py`：先生成 2～3 个 candidate，再把用户选择、候选 artifact/plan、联系表和 SHA-256 固化为 approved prototype manifest。
- `generate_html.py`：只生成静态通过的 content v3 候选；`promote_html.py` 校验 `html-browser` 报告后原子晋升候选与 evidence。
- `generate_pptx.py`：用同一 content/plan 生成、完整验证并原子替换 PPTX；`--prototype-candidate` 只用于代表页。
- `build_support_matrix.py`：从同一 content 与 visual-plan 解析双载体 support、抑制项和适配摘要。
- `verification_report.py`：检查绑定 input/plan/artifact hash、逐项 passed 的机器报告。
- `build_manifest.py` / `validate_manifest.py`：都从 resolver 重算 support/suppression/degradation，并验证报告、原型与 support matrix 哈希；v1 只保留读回兼容。
- `validate_html.py` / `validate_pptx.py`：检查载体结构、内容映射、notes、alt、原生 chart/table、主题、字体和证据。
- `check_style_content.py`：输出当前组合与输入内容的可读映射报告，不把 preset 当底层样式分类。

## 最小工作流

```bash
python3 generate_prototypes.py \
  --input fixtures/system-showcase.json \
  --output-dir ../examples/system-prototypes

python3 finalize_prototype.py \
  --manifest ../examples/system-prototypes/prototype-manifest.json \
  --selected A \
  --evidence ../examples/system-prototypes/contact-sheet.png \
  --pptx-artifact ../examples/system-prototypes/candidate-a-swiss.pptx \
  --pptx-evidence-dir ../examples/system-prototypes/candidate-a-swiss-pptx-evidence \
  --output ../examples/system-prototypes/approved-prototype-manifest.json

python3 generate_html.py \
  --input fixtures/system-showcase.json \
  --plan fixtures/system-showcase.visual-plan.json \
  --candidate-only \
  --output /tmp/system-showcase.candidate.html

python3 generate_pptx.py \
  --input fixtures/system-showcase.json \
  --plan fixtures/system-showcase.visual-plan.json \
  --output ../examples/system-showcase.pptx

python3 build_support_matrix.py \
  --input fixtures/system-showcase.json \
  --plan fixtures/system-showcase.visual-plan.json \
  --output ../examples/system-showcase-support-matrix.json
```

visual-plan 的 `prototype.status` 必须是 `approved`，或在用户点名已验证 preset / 明确快速生成时写成带理由的 `skipped`；不允许用缺省状态绕过原型门。
content v3 缺少 `--plan` 或显式 `--preset` 时失败；无参数 Swiss 只留给 legacy v1 兼容。
候选包内部计划使用 `candidate`，只允许 `generate_prototypes.py` 的原型渲染路径消费，不能被整套生成或 manifest v2 接受。
目标载体为 PPTX 时，可对候选计划显式使用 `generate_pptx.py --prototype-candidate` 生成代表页截图；该开关只接受 `candidate` 状态，也不能被最终 manifest 接受。

`generate_pptx.py`（演示文稿生成脚本）在最终输出的同目录候选文件中生成并关闭演示文稿，调用 `validate_pptx.py`（演示文稿验证脚本）完成结构、格式、备注、替代文本与逐页截图内容验证后才原子替换目标；生成或验证失败时已有文件保持不变。原子替换回归入口为 `python3 -m unittest test_generate_pptx.py`（演示文稿原子替换回归命令）。

## 回归入口

```bash
python3 -B -m unittest discover -s . -p 'test_*.py' -v
bash test_html.sh
```

`test_html.sh` 在浏览器不可用时仍执行静态合同与内容映射检查；真实交付还必须按 `../references/verification-plan.md` 在最终载体上完成视觉、交互和中文换行验收。

脚本不负责决定内容、风格或素材授权；这些由输入合同与 `SKILL.md`（技能说明）约束。所有脚本必须声明运行条件、输入、输出、失败码和最小测试命令；运行时代码、依赖和资产必须在 `../third-party-notices.md`（第三方来源声明）与 `manifest`（清单）中有来源记录。

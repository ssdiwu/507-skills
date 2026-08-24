# 分层验证与样例计划

验证按内容、visual-plan、组合解析、载体、视觉、换行与来源分层。任何层失败都停止宣称完成；不通过修改阈值掩盖失败。

## Fixture 角色

- `collaboration-baseline.json`：旧 v1 内容和 `--style` preset 的兼容回归；
- `system-showcase.json`：content v3，覆盖 13 个语义叶组件、中文、data/media/relationship；
- `system-showcase.visual-plan.json`：三轴、受控 treatment、中文短语与 adapted 页；
- `presentation-pairwise.json + visual-plan`：八类视觉呈现与四种 treatment 的真实双载体代表页；
- 原型测试：代表页选择、2～3 候选、混合后合并原型；
- 中文换行测试：宽度足够保持单行，宽度不足只在 phrase units 边界换行。

## 单元与组合解析

1. 每个组件至少有一个 preferred 核心呈现；每个呈现至少有消费者；
2. 每个允许组合解析为唯一 support/suppression/degradation；禁止组合报错；
3. 一套 deck 只能有一个基础语言，单页 raw token override 拒绝；
4. `metric/chart/table` 字段、渲染和验收互不降级；
5. table 在所有组合中抑制背景网格和重复线；
6. 旧 kind/preset 标准化后 ID、顺序、文字、notes、alt 不变；
7. 顶层与 nested JSON Pointer 的 phrase units/lines 拼接等于原文，且只在 units 边界断行；
8. 缺失素材、伪造 fallback、未渲染的 photo/UI 组合与超过 3 个素材均失败；
9. 多序列 bar 使用独立轨道/series，并覆盖 0、最大值与 2～3 series；
10. manifest v1 兼容；v2 对 resolver support/suppression/degradation、prototype 链、support matrix 与 verification report 篡改严格拒绝。

## HTML

| 层 | 断言 | 证据 |
| --- | --- | --- |
| 三轴 | data component/presentation/language/treatment/support 齐全 | DOM 报告 |
| 结构 | slide ID、顺序、标题、table、chart、alt 完整 | 静态检查 |
| 交互 | 键盘、按钮、滚轮、触控、页码与焦点成立 | 浏览器检查 |
| 视觉 | `instant=1` 后 current ID、页码、offset 与截图一致；桌面/移动无裁切重叠 | 逐页截图/联系表 |
| 换行 | 单行优先、phrase 不拆、标点与尾行自然 | DOM rect + 截图 |
| 退化 | static、无 JS、减少动态仍保留内容 | 多模式截图 |
| 来源 | 无远程资源，嵌入资产/notice 可查 | 来源扫描 |

移动端完整画幅但小字不可读时只能报告“构图预览”，不能称移动阅读通过。

## PPTX

| 层 | 断言 | 证据 |
| --- | --- | --- |
| 结构 | OpenXML schema 有效、零 format issues | officecli validate/issues |
| 内容 | ID/文字/notes/alt 与输入一致 | text/query/read-back |
| 数据 | chart/table 是原生对象，categories/series/rows 可读回 | officecli query/get |
| 语言 | 字体角色、主题色、受控 treatment 和适配呈现成立 | query + 逐页截图 |
| 换行 | 只在 phrase lines 处软换行，无拆词/无限缩字 | plan + screenshot |
| 证据 | 验证截图保留在最终 evidence 目录；报告绑定 artifact/input/plan hash | manifest 回链 |

## 双载体与 pairwise

不生成无意义的全笛卡尔积成品。Resolver 对所有注册的组件 × 呈现 × 基础语言 × 载体组合执行全矩阵检查；13 页 showcase 覆盖全部组件，8 页 pairwise fixture 覆盖全部呈现与四种 treatment，高风险组合另做定向样例。HTML/PPTX 对同一内容与 visual-plan 保持页面映射与可见文本，adapted 页显式记录差异。

## 原型门

- 候选使用同一真实内容；
- 代表页覆盖封面、最密页、data/media；
- 推荐理由和目标载体支持可见；
- approved manifest 绑定候选 artifact/plan、选中项、代表页、联系表与全部 SHA-256；目标含 PPTX 时另绑定真实候选 PPTX 和每张代表页截图；
- 混合候选后必须生成合并 plan 与合并原型；
- 目标为 PPTX 时，锁定前必须有真实 PPTX 代表页截图。

## 执行顺序

静态 schema/来源 → 组合 resolver → 原型审批 manifest → HTML/PPTX 候选 → 自动验证 → CDP 真实交互、无 JavaScript、无转场逐页 PNG 与 phrase/table 计算样式检查 → 带工具/版本/时间/Git revision 的机器报告 → 原子晋升 → manifest v2 → 独立 review。旧产物只在新候选与 evidence 全部通过后替换。

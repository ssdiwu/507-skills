# 视觉幻灯片工作流合同

## 上游：507-stage

进入 `507-ppt` 前，每页至少有认知目标、观众可见内容、notes 或无备注声明，并已确认受众、场景、时长和素材边界。内容仍在争论、事实不足或讲者提示混入页面时返回 `507-stage`，不以视觉原型替代内容决定。

标题在内容阶段按页面任务确定，可以表达问题、判断、动作或资料定位；视觉阶段保留已确定的含义，只做保义缩句、断行与排版。需要改变判断、事实或责任主体时返回内容阶段。内容改动同步当前真相源及本次实际受影响的产物；HTML-only 不要求创建 PPTX 或独立讲稿，无备注声明不要求制造备注。

## 内容与视觉分离

- content v3 保存语义组件和事实；
- visual-plan v1 保存整套基础设计语言、逐页视觉呈现、受控 treatment、中文短语流和 prototype 状态；
- manifest v2 保存内容/plan 哈希、原型选择、载体支持、降级与验证证据。

visual-plan 的 `inputSha256` 针对 normalize 后的 canonical content v3；manifest 的 `inputSha256` 针对实际交付的原始输入文件。两者职责不同，均需复验。

旧 v1/v2 `kind` 内容与 `--style` 在一轮迁移期内标准化；新文件只写三轴合同。

## 自适应原型

用户未锁定已验证 preset 时：

1. Agent 根据内容、受众、场景、密度、素材和载体推荐 2～3 个兼容组合；
2. 每个候选使用同一真实内容，至少覆盖封面、文字最密页、首个 data/media 页；
3. 原型显式记录组件、设计语言、视觉呈现、推荐理由、HTML/PPTX support 与降级；
4. 用户选定或跨候选混合；混合后先生成并确认合并原型；
5. 用户选择后用 `finalize_prototype.py` 把候选 artifact/plan、联系表、选中项与 SHA-256 固化为 approved prototype manifest；目标包含 PPTX 时，还必须绑定真实候选 PPTX 与每张代表页截图的哈希。visual-plan 回链该文件与哈希后才允许生成整套。

点名成熟 preset 或明确要求快速生成时可以跳过原型，但不能省略 visual-plan。content v3 没有 plan 或显式 preset 时直接失败；只有 legacy v1 保留默认 Swiss 的一轮兼容。目标为 PPTX 时，HTML 总览只用于初筛；锁定前必须看真实 PPTX 代表页截图。

## 载体路由

1. 用户已指定 `.pptx` 或 HTML 时遵守；
2. 未指定时探测 officecli，可用优先 `.pptx`，否则生成 HTML；
3. 明确要求 `.pptx` 但 officecli 不可用时报告缺失，不自动安装或静默改载体；
4. 核心组合支持双载体，但只生成用户本次请求的载体；adapted 明示，unsupported 停止；
5. HTML 与 PPTX 各用原生表达，不机械互译坐标或截图冒充结构化对象。

## 安全制作

先在同目录隔离候选中生成。HTML 的 `generate_html.py --candidate-only` 不触碰当前成品；浏览器用 `instant=1` 禁用转场，逐页核对 current ID、页码、offset、overflow、短语与截图 hash，并在 mobile / reduced-motion / failure fallback 全部通过后，由 `promote_html.py` 原子晋升候选和 evidence。PPTX schema、零 issues、notes、alt、原生 chart/table 逐页 read-back、逐页截图与中文换行通过后才替换，并保留 evidence。

验证报告由载体对应的真实验证入口生成并使用机器合同，绑定 input、visual-plan 与 artifact 哈希及 producer 源码哈希；任一 check/profile/page 为 failed、截图不是有效 PNG、载体格式不匹配、输入/plan/artifact/evidence 越出交付包根目录或 producer 元数据缺失时，builder 和 validator 都拒绝 manifest。Manifest builder 先在同目录候选 manifest 上自验，失败时保留旧 manifest。Manifest 的 support、suppression 与 degradation 由 resolver 重新计算，不信任手填状态。

## 相邻 Skill

| Skill | 负责 | 交接边界 |
| --- | --- | --- |
| `507-stage` | 讲稿、课程与成熟逐页内容 | 内容包 → `507-ppt` |
| `507-prototype` | 一个具体技术未知的可丢弃验证 | verdict 返回当前 PPT 对齐或实施；不替代标准视觉候选 |
| `507-ppt` | visual-plan、原型确认、HTML/PPTX 视觉成品和验证 | 内容缺口返回 stage；成品交付或迭代 |
| `507-rednote` | 社媒图文改编 | 不消费或生成横向 deck，除非另有改编合同 |

## 完成与回退

完成时内容映射、组合计划、prototype 状态、载体支持、中文排版、来源和验证均可复验。内容、组合、授权或载体能力未成立，或最终截图仍有拆词、溢出和降级未记录时停止，不宣称完成。

---
name: 507-ppt
description: 原创视觉幻灯片制作：把成熟逐页内容用语义组件、设计语言与视觉呈现动态组合，先以真实内容原型确认，再生成并验证可编辑 .pptx 或离线单文件 HTML。Use when user mentions 制作 PPT、生成 pptx、做成幻灯片、做 HTML deck、网页演示、slides rendering、presentation visual design、瑞士风 PPT、杂志风 PPT；内容仍需编排、讲稿或逐页内容尚未完整确认时使用 507-stage，不使用本 skill。
license: MIT
---

# 视觉幻灯片（507-ppt）

将**成熟逐页内容包**制作为可演示、可验证的视觉成品。内容语义与视觉选择分开：内容包声明每页组件，独立 `visual-plan` 声明整套设计语言、逐页视觉呈现、受控 treatment（处理方式）与换行提示；HTML 和 `.pptx` 生成器读取同一份计划。

先读 [工作流合同](references/workflow-contract.md)、[三轴视觉系统](references/design-system.md)、[组合与视觉质量合同](references/style-contracts.md)、[中文排版合同](references/typography.md)和[来源合同](references/provenance.md)。

## 运行条件

生成 `.pptx` 及逐页截图验证需要已可用的 officecli 与 Pillow；含 SVG 素材时还需要 Chrome/Chromium 与 `websockets` 生成真实 PNG 备用图。生成 HTML 需要可写文件系统，浏览器交互与视觉验证需要 Chrome/Chromium、Pillow 与 `websockets`（用于 Chrome DevTools Protocol）。渲染环境必须有覆盖内容语言的字体；缺字方框不能当作成功截图。本 Skill 不自动安装这些依赖。

## 不覆盖什么

- 不写讲稿、不决定演讲主线；逐页目标、可见内容或备注尚未确认时返回 `507-stage`。
- 不制作小红书图卡，不登录、上传或发布。
- 不支持 legacy `.ppt`；只输出 `.pptx` 或单文件 HTML。
- 不自动安装 officecli、浏览器、字体或第三方依赖。
- 不复制外部演示 Skill 的模板、代码、版式、字体或资产；外部项目只提供带版本的研究证据。
- 不把 PPTX 模板填充、截图重建、旧 PPT 转网页或旁白视频顺带并入本轮视觉制作。

## 输入门

成熟逐页内容包必须具备页面认知目标、观众可见内容、notes（讲者备注）或无备注声明、受众、场景、时长和素材授权。组件属于内容语义，不能由视觉计划改写。

每个 `media-evidence` 素材都必须有唯一 ID、真实本地 path、alt 与明确授权；最终产物遇到缺失路径直接失败，不能把项目占位图伪装成用户素材。PPTX 与 HTML 均实际使用 1～3 个素材。

旧 `kind` 内容可在一轮迁移期内标准化为 v3；新内容只写语义组件。`metric / chart / table` 共享 `data-evidence` 家族，但保持独立输入、渲染和验收，不能互相降级。

## 三轴组合与载体

1. **语义组件**回答“这页承担什么内容关系”。
2. **设计语言**回答“整套如何说话”：字体角色、色彩行为、网格、轮廓、层次、间距和动效性格。一套 deck 只有一个基础语言；单页只能使用注册过的 `default / inverse / section-emphasis / dense` treatment，不能直接覆写 raw token。
3. **视觉呈现**回答“这一页如何被看见”，可逐页变化，但必须通过组件兼容矩阵。

命名样式只是已验证组合 preset，不是底层能力。自由组合不等于所有笛卡尔积自动有效；组件自身已有强组织手段时抑制重复装饰，例如 `table` 必须关闭背景网格并保留表格规则线。

核心组合同时提供 HTML 与可编辑 `.pptx`；`adapted（适配实现）`必须记录降级，`unsupported（不支持）`禁止生成。扩展呈现不得伪装成核心双载体能力。

## 自适应视觉原型

用户没有锁定成熟 preset 时，Agent 根据内容、受众、场景、密度、素材与目标载体推荐 2～3 组真正不同的“组件处理 × 设计语言 × 视觉呈现”组合，并用真实内容制作代表页原型：封面、可见文字最密页、首个数据或素材页。

- 用户已点名已验证 preset 或明确要求快速生成时可以跳过，但 visual-plan 必须记录原因。
- 用户可整组选中或跨候选混合；混合后必须先生成并确认合并原型，再生成整套。
- 原型属于本 Skill 的标准视觉探索阶段，不等于独立 `507-prototype`；只有一个具体技术未知需要可丢弃验证时才进入后者。
- 目标是 `.pptx` 时，可先用 HTML 总览判断方向，但锁定前必须生成真实 PPTX 代表页截图。
- `approved` 不是可手填字符串：visual-plan 必须回链带 SHA-256 的 approved prototype manifest、选中候选、代表页、候选 artifact/plan 与联系表；任一文件变化都会让审批失效。

## 中文语义换行硬规则

- 能在一行容纳时保持一行，不为了造型主动拆成两行。
- 必须换行时，只在词语或语义短语边界换行；不得拆开术语、专名、英文词、数字与单位。
- 避免闭标点出现在行首、开标点留在行末，也不留下孤立的一两个字尾行。
- `text-wrap: balance / pretty` 只作辅助，不能替代语义短语提示。
- HTML 用不可断短语与边界换行点；PPTX 只按同一组短语写显式软换行。短语自身放不下时扩大容器或失败，不继续缩字或拆词。
- `textFlow` 使用零基 JSON Pointer，可覆盖 `/items/0/label`、`/nodes/0/label`、`/assets/0/caption`、chart category/series 与 `/data/rows/0/2` 等嵌套可见文字；不可见 notes/goal 不进入该合同。
- 以最终 HTML / PPTX 真实尺寸与逐页截图验收；自动 issues 为零不等于换行成立。

## AI 味自检

交付前按三层排查生成器痕迹；任何一层命中都先修再交。

- **视觉层**：与内容无关的 AI 摆拍配图（暖光书桌、咖啡、绿植一类通用场景）、页面上出现"AI 生成 / AI 配图"类标注、一眼可辨的生成器默认皮肤。真实截图、照片与数据证据优先；没有真素材时纯色留白优于摆拍图。
- **文案层**：无内容依据或连续同构的排比、警句、固定总结陈词和引号体标题。标题沿用内容包已确定的问题、判断、动作或资料定位；真实比较与当事人原话按其内容作用保留。可做保义缩句、断行和排版，不为统一风格把判断标题改成类别标签；需改变含义或主线时返回 `507-stage`。
- **结构层**：每页同构（大标题 + 卡片 + 金句收尾），详略没有起伏；重点页与过渡页必须有密度差。

反模式：用另一种模板掩盖模板——全套手写体"装人味"、把口号换成口语对仗，都是换皮不是去味。去 AI 味的方向是回到事实与证据，不是换风格。

同步纪律：标题或文案改动先更新当前唯一内容包或主稿，再同步本次已请求且实际承载这些文字的页面、备注、独立讲稿与内容清单。输出 PPTX 时核对其 notesSlides；输出 HTML 时核对其页面及实际使用的备注。已有讲稿仍承载被修改内容时同步更新，不因未请求某种载体而强制生成它，也不为无备注声明制造备注。最终按所请求载体逐页看图验收，构建通过不能代替溢出、遮挡与内容一致性检查。

## 制作与验证

1. 校验并标准化内容包，建立或读取独立 visual-plan；support、suppression 与 degradation 由注册表计算，不能手填为通过。
2. 完成所需视觉原型与当前版本确认，再生成整套候选；content v3 没有 visual-plan 或显式 preset 时必须停止，不能静默默认 Swiss。
3. HTML 先以 `--candidate-only` 生成隔离候选。随后运行 `html_browser_evidence.py`，逐页用无转场 capture 模式核对当前 ID、关键文字、overflow、短语、table 背景抑制、按钮/键盘/滚轮/触控、mobile、无 JavaScript、reduced-motion、故障退化和真实 PNG 截图哈希。浏览器检查通过后，再由 `promote_html.py` 原子替换成品与 evidence；仅静态检查不能替换旧成品。
4. PPTX 必须使用可编辑文字、shape、picture、原生 chart/table 和 notes，不用截图冒充结构化数据。
5. 本次请求的每种载体都在隔离候选中生成；自动、视觉、来源与换行检查通过后才替换已有产物。验证失败保留上一版。chart/table 使用原生对象；多序列柱图使用独立分组轨道，不把多个数值挤进同一宽度。
6. manifest v2 记录内容哈希、visual-plan、prototype evidence、设计语言、逐页组件/呈现/treatment、载体支持、抑制项、降级、notes/alt、来源与截图证据；builder 与 validator 都重新调用 resolver，并复读绑定 artifact/input/plan 哈希且所有 checks 为 passed 的机器报告。旧 manifest v1 只作兼容读回。

载体命令与细节见 [HTML recipe](references/html-recipes.md)、[PPTX recipe](references/pptx-recipes.md)和[验证计划](references/verification-plan.md)。

## 完成与接力

- **完成信号**：内容语义未被视觉改写；当前 visual-plan 和原型选择可追溯；目标载体可打开；组合可辨识；中文换行、notes、alt、来源、自动与逐页视觉检查通过；AI 味自检通过；适配降级已明示。
- **产物**：`.pptx` 或单文件 HTML、visual-plan、prototype 证据、manifest v2、素材/notice、验证报告与逐页截图或联系表。
- **候选出口**：视觉迭代继续本 Skill；内容需调整返回 `507-stage`；成品可直接交付；社媒图文进入 `507-rednote`。
- **回退条件**：逐页内容尚未完整确认、组合未确认、素材授权不清、载体不支持、中文换行或验证未通过时，不宣称完成。

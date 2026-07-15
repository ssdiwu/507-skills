---
name: 507-rednote
description: "把已成立的书面作品改编并渲染成小红书 3:4 图片文章：锁定中心判断、论证链与原图去向，产逻辑 Copy Spec，按真实高度自动分页，从 18 套外观中选样式，导出 1500×2000 图卡、联系表并验收。Use when user mentions 做成小红书图文, 小红书图片文章, 小红书图卡, 3:4竖图, 把文章转成小红书, RedNoteImage, rednote cards, xiaohongshu carousel."
compatibility: "Requires Python 3.10+, Pillow, and local Google Chrome or Chromium."
---

# 小红书图文（rednote）

把一篇已经成立的书面作品改编成可发布的小红书图片文章。它不是重新写一篇教程，也不是给文章配几张插图。

## 覆盖什么

- 已有主稿 → 小红书逻辑文案 → 自动分页的 3:4 图卡 → 联系表与验收。
- 已有逻辑文案 → 直接自动分页并生成图卡。
- 根据反馈修改逻辑文案并重新自动分页；显式卡片模式可局部重渲染。

## 不覆盖什么

- 选题、挖素材和长文成稿，分别归 `507-mine`、`507-fuse`、`507-forge`。
- 单张封面、场景图或 AI 插图归 `image-workflow`；本 skill 只在确需额外素材时调用它。
- 不负责登录、发布或运营小红书。
- 不把成熟文章改造成原文没有的教程、清单或行动建议。

## 输入与输出

输入优先级：已确认的 `copy-spec.md` > 已发布/待发布主稿 > 其他草稿。

默认输出到作品目录的 `小红书/`：

```text
小红书/
├── README.md
├── copy-spec.md
├── rednote-project.json
├── style-preview/style-gallery.jpg
├── rednote.html
├── render-manifest.json
├── contact-sheet.jpg
└── pages/rednote_page_01.jpg ...
```

## 默认长文契约

1. **逻辑块不是物理页**：规格只描述章节、段落、图片与顺序，最终页数由真实排版决定。
2. **正文必须连续填页**：浏览器从页头排到安全区底部，不为凑页数制造标题、结论框或大片空白。
3. **章节标题不强制换页**：标题与第一段绑定；剩余空间放得下就接着排，放不下才整体换页。
4. **主稿图片逐张有去向**：默认保留数量和相对顺序；改作封面或删除都必须在改编合同中显式记录。
5. **结尾避免孤页**：最后两段与结论框绑定，并在必要时对倒数页面做密度再平衡。

## 工作流程

### 1. 锁定改编合同

先从主稿提取并写进 `copy-spec.md`：

1. 一句中心判断。
2. 按顺序排列的论证链。
3. 可删的支撑层与不可删的转折/结论。
4. 主稿全部图片的清单、原始顺序，以及“正文保留 / 改作封面 / 明确删除及理由”。
5. 帖子标题、封面标题、副标题和分页模式。
6. **保真清单**：以 `M1`、`M2`…逐项列出不可删的承重内容。若主稿含可直接复用的完整提示词、模板、表格、步骤或用户已明确要求保留的章节，默认视为不可压缩；除非用户明确同意拆成另一篇或删除，否则不得把它们静默概括成一句“文末有提示词”。
7. **资源分发策略**：对提示词、模板、清单、附件等可领取资源，必须明确选择“图卡全文交付 / 评论区钩子 / 拆为系列 / 外链或附件领取”之一；写清完整资源仍存在哪里，以及图卡怎样准确承诺。评论区钩子只在用户明确选择后可用，不能伪装成正文已经交付。

模板与逻辑文案约束见 [`references/copy-spec.md`](references/copy-spec.md)。没有锁定中心判断、论证链、保真清单、资源分发策略和图片去向，不进入分页。

### 2. 按章节拆跨页长文

默认使用**长文模式**，不是“一页一标题”的卡片模式：

- 先沿用主稿章节；一个章节可以连续跨多个物理页。
- 只在章节起点显示 `heading`；后续正文不为物理分页重复标题。
- `layoutMode: longform` 由浏览器按真实字体和图片高度自动填页：从页头连续排到安全区底部，放不下的下一个完整内容块才移到新页。章节标题与第一段绑定，但不强制另起一页。
- 逻辑规格只选择自然段落顺序，不预先拍板物理页数，也不强求每页独立提出观点或放结论框。
- 脚本把每个物理页实际承载的段落来源写入 `render-manifest.json`；连续页面无法映射，说明已经偷换主线。
- 标记为 `closing` 的结尾会绑定最后两段与结论框，并在分页后再平衡倒数页面，避免图片页或结论框成为孤页。
- 清单、流程、对比等内容才使用“一页一观点”的卡片模式，不把它当成长文默认。
- 主稿图片默认全部保留并维持相对顺序；原图改作封面时，其余正文图片仍须完整进入成品。任何删图都必须回到改编合同逐张说明理由。
- 只做删减、分页和视觉重排；新增观点必须明确升级为续写/重写。
- 默认先提交 `copy-spec.md` 供用户审核；用户明确要求直接生成时可跳过等待，但仍必须落规格。

### 3. 生成内容规格

按 [`assets/rednote-project.schema.json`](assets/rednote-project.schema.json) 和 [`references/project-spec.md`](references/project-spec.md) 创建 `rednote-project.json`。长文默认写 `layoutMode: longform`，其中 `pages` 是章节/段落逻辑块，不等于最终图片页；清单或对比卡片才用 `layoutMode: cards`。每个逻辑块的 `sourceMap` 必须写入它承接的 `M` 编号；渲染前逐项核对保真清单中的每个编号至少出现一次，未覆盖就回到 Copy Spec 补块，不以“整体大致讲到了”放行。尚未选风格时可暂用 `editorial-用户`。图片与头像尽量复制到作品目录并用相对路径引用；禁止远程图片 URL。

### 4. 选择外观样式

按 [`references/styles.md`](references/styles.md) 选择 `stylePreset`。用户没有指定时，不要直接沿用默认风格；先生成封面与一页正文的 18 样式联系表：

```bash
python3 <skill-dir>/scripts/render_style_gallery.py \
  --spec <作品目录>/小红书/rednote-project.json \
  --output-dir <作品目录>/小红书/style-preview
```

根据联系表选定一套主样式并写回 `rednote-project.json`。选样时必须同时看封面和正文，不把上一份作品的默认风格惯性沿用到新稿；若用户指出“风格还是一样”，先换一套整体视觉，而不是逐页随机换皮。

**作者识别资产**：检查来源作品及同仓库既有平台稿是否已有用户头像或署名资产。找到且适用时，复制到当前作品的 `小红书/assets/`，在 `rednote-project.json` 填 `avatar` 和 `author`；找不到或不适用时，必须在交付中说明“本次未放头像”，不能静默省略。样式只改变字体、颜色、背景、边框和卡片质感，不改逻辑文案；同一篇不逐页随机换皮。

### 5. 调用内部脚本

```bash
python3 <skill-dir>/scripts/render_rednote.py \
  --spec <作品目录>/小红书/rednote-project.json \
  --output-dir <作品目录>/小红书
```

仅 `layoutMode: cards` 的显式卡片页，且页数与全局视觉配置未变化时，才局部重渲染：

```bash
python3 <skill-dir>/scripts/render_rednote.py \
  --spec <...>/rednote-project.json --output-dir <...>/小红书 --pages 4,6,7
```

`layoutMode: longform` 修改任一逻辑块都可能让后续物理页整体位移，必须全量重渲染。

脚本负责：内嵌本地素材、生成单文件 HTML、调用本地 Chrome、导出 1500×2000 JPG、检查溢出、生成联系表和清单。运行条件见 [`scripts/README.md`](scripts/README.md)。

### 6. 交付硬门与双重验收

**先过交付硬门，才谈验收或提交。** 每次修改 `copy-spec.md`、`rednote-project.json`、图片、头像或全局样式后，必须重渲染受影响输出；`longform`（长文）任一逻辑块变化一律全量重渲染。独立核对：

1. `render-manifest.json` 的 `status` 为 `rendered`，其 `sourceSpecSha256` 必须等于当前 `rednote-project.json` 的 SHA-256（安全散列）；不相等表示图卡、HTML（网页）和联系表仍是旧规格。
2. 保真清单的每个 `M` 编号至少出现在一个当前 `rednote-project.json` 逻辑块的 `sourceMap` 中；未覆盖的承重内容不能被“概述过”替代。
3. `render-manifest.json` 所列全部图卡、`contact-sheet.jpg`、`rednote.html` 均存在；物理页数可以不同于逻辑块数，但必须来自当前规格。

任一项失败时，状态只能是“规格已更新、输出过期”，不得称为发布包完成、不得提交生成物、不得让用户按现有图卡发布。

**内容验收**：逐页映射回中心判断与论证链；渲染文案与 `copy-spec.md` 一致；没有凭空增加教程线。

**视觉验收**：打开 `contact-sheet.jpg` 检查全局节奏，再抽查每张原图的裁切、字号、截图隐私和顺序。规则见 [`references/visual-review.md`](references/visual-review.md)。

失败时改 `copy-spec.md` 或 `rednote-project.json` 后重渲染，不直接修 JPG。

## 红线

- 不把“平台适配”当成重写许可。
- 不在渲染阶段临时改文案。
- 不把私密截图未经脱敏直接嵌入。
- 不上传正文、图片、头像或凭据到远程渲染服务。
- 不交付未看联系表、未验证尺寸和页数、或未通过“当前规格 ↔ 渲染清单”新鲜度核对的图卡。

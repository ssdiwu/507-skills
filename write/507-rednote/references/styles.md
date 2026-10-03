# 小红书三轴视觉系统

底层模型是：

```text
语义组件 × 设计语言 × 视觉呈现 → 最终连续 DOM → 3:4 页面
```

文章模式中的物理页不是语义组件；视觉呈现绑定内容块，最终页面只按实际可读高度切分连续内容，不选择观点或改写论证。

## 语义组件

| 家族 | 组件 |
| --- | --- |
| identity | cover |
| flow | heading、paragraph、list、quote、code、hr |
| data-evidence | metric、chart、table |
| relation | sequence、relationship、受控 Mermaid flowchart |
| media-evidence | image、screenshot、motion |

语义组件来自 `content.md` 的实际 Markdown。runtime 不把普通正文擅自转成 cards、流程或数据图。

## 设计语言

- `precision-modern`：严格网格、锐利轮廓与精密层级。
- `editorial-archive`：暖纸、编辑栏栅格与细规则线。
- `soft-product`：舒展模块、人文层级与柔和状态色。
- `warm-narrative`：非对称节奏、暖色与纸面叙事感。
- `research-organic`：研究型层级、克制自然色与低装饰。
- `bold-statement`：黑白高对比、粗规则线与单一红色强调。

一组只使用一种基础语言。色彩行为、轮廓、层次与间距由语言统一决定。设计语言是可被多套外观复用的底层语法，不等于用户看到的一套完整样式，也不再暗中替换具体字体。

## 字体与字符占用宽度

| ID | 界面名称 | 本地文件 | 许可证 | 默认角色 |
| --- | --- | --- | --- | --- |
| `source-han-sans` | 思源黑体 | `SourceHanSansCN-VF.otf.woff2` | SIL OFL 1.1 | 默认连续阅读 |
| `source-han-serif` | 思源宋体 | `SourceHanSerifCN-VF.otf.woff2` | SIL OFL 1.1 | 可选编辑阅读 |

字体选择独立于 preset；同一字体、字号、行距、字符占用宽度和组件内宽成立时，切换只改变颜色/表面效果的 preset 不应因系统字体 fallback 产生额外换行。正文、引语和列表共同使用 `bodySize` 与 `lineHeight` 决定其字号和行距。

`characterWidth` 取 0.94～1.08，runtime 将它换算成 -0.06em～0.08em 的 `letter-spacing`，因此真实改变字符占用的横向空间并进入 DOM 分页。它不是字形横向拉伸；当前两套字体只有 weight 轴，不伪造不存在的 width 轴。

## 视觉呈现

| 组件 | 推荐呈现 |
| --- | --- |
| cover | type-led、panel-led、editorial-print-led、illustration-led |
| heading / paragraph | type-led、editorial-print-led |
| list / code | type-led、panel-led、editorial-print-led |
| table / chart | data-led、panel-led、editorial-print-led |
| sequence / relationship | schematic-led、hand-drawn-explainer |
| image / screenshot | photo-led、ui-product-led |

组件已有强组织手段时抑制重复装饰，例如 table 保留自己的行列规则，不叠加背景网格。

## Treatment 与 preset

`default / inverse / section-emphasis / dense` 是受控 treatment，不是第四轴。`preset` 保存经过真实内容验证的设计语言、具体 palette、组件呈现和 treatment 组合；它是用户一键选择的完整成品外观，但 runtime 仍保存完整三轴状态。多套 preset 可以共用一种设计语言，例如“当前编辑红”“深夜暗色”“新野蛮主义”都使用 `bold-statement`，但具体配色和表面效果不同。

当前工作台提供 19 套可选 preset：当前编辑红、复古怀旧、报纸、极简黑白、自然森系、蓝色信号、秋日暖阳、深夜暗色、莫兰迪、赛博朋克、新野蛮主义、胶片复古、孟菲斯、杂志排版、磨砂柔光、格子布局、千禧复古、粉色层次和田野笔记。六种设计语言只出现在高级设置中，不构成“只有六个视觉方向”的上限；高级设置还允许逐组件调整第三轴，调整后 `presetId` 为空并保存为当前自定义组合。同一语言下的 preset 必须在具体配色之外至少改变一项组件呈现或 treatment，不能只换名称。每套 preset 必须同时在封面、最密正文页、首个表格/流程图/图片页和整组联系表中成立后，才能标记为已验证。

## Page chrome

页码、日期和作者识别是可关闭的载体装饰，独立于三轴和正文覆盖。它们可以改变正文可用高度，因此变化后必须重新分页。

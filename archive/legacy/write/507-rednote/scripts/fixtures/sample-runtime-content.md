# 真实 DOM 分页测试

这是一段用于验证连续文章分页的正文。文字必须完整显示，不能依赖字符数估页，也不能在页面底部裁掉半行。

## 标题可以出现在页面中部

- 第一条列表需要保持完整。
- 第二条列表会跟随正文自然流动。
- 第三条列表用于验证条目之间可以续页。

```text
content.md
  → semantic components
  → final DOM
  → paged-content.json
```

| 输入 | 职责 | 输出 |
| --- | --- | --- |
| content.md | 可见平台稿 | 语义组件 |
| visual-plan.json | 三轴视觉 | 最终 DOM |
| paged-content.json | 实测分页 | 预览与导出 |

```mermaid
flowchart LR
  A[Markdown] --> B[语义组件]
  B --> C[最终 DOM]
  C --> D[3:4 页面]
```

![本地测试图片](assets/sample.svg)

<!-- rednote:page-break -->

## 强制分页后的标题

链接必须显示完整地址：[示例来源](https://example.com/reference)。

最后一段用于证明强制分页指令本身不显示，但后面的所有文字仍然进入图片。

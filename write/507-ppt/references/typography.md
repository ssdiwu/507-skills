# 中文排版与语义换行合同

只在制作标题、短段、列表、表格或检查最终截图时读取。本合同保护可见文本的语义完整性；不负责改写内容。

## 语义单位

visual-plan 可用零基 JSON Pointer 为任意可见文字字段提供 `textFlow.units`：按顺序连接后必须与原文逐字一致。每个 unit 是不可拆词语或语义短语，术语、专名、英文词、数字与单位必须处于同一 unit。`/notes`、`/goal` 等不可见字段不能进入 textFlow。

```json
{
  "/title": {
    "units": ["六个方向，", "两种成熟度"],
    "preferSingleLine": true,
    "maxLines": 2,
    "lines": ["六个方向，", "两种成熟度"]
  }
}
```

嵌套字段沿用同一合同，例如 `/items/0/label`、`/nodes/2/label`、`/assets/0/caption`、`/data/categories/1`、`/data/columns/2` 与 `/data/rows/0/2`。内容顺序变化会使 content hash 变化，旧 plan 随即失效。

`lines` 是 PPTX 或其它必须显式断行的载体选择：每一行只能由完整、连续的 units 组成。HTML 可以在 units 边界动态换行；两种载体的换行位置可以不同，可见文字不能不同。

## 硬规则

1. 先在最终字号和容器宽度下尝试单行；能一行时不主动换成两行。
2. 必须换行时只在 units 边界换行，不能拆开一个词语或语义短语。
3. 闭标点不出现在行首，开标点不留在行末；避免只剩一两个字的尾行。
4. 单个 unit 在最小字号下仍放不进容器时，扩大容器、调整构图或失败；不无限缩字、不拆词掩盖 overflow。
5. 表格单元格也遵循词语完整性；必要时增加行高或列宽，不把术语拆成上下两段。

## 载体实现

### HTML

- 每个 unit 使用 `white-space: nowrap` 的 `.phrase` 包裹；unit 之间提供 `<wbr>`；对应元素保留 `data-text-path` 供浏览器逐路径核验。
- 标题可用 `text-wrap: balance`，正文可用 `text-wrap: pretty`，两者只优化已允许的换行点。
- `preferSingleLine` 先使用单行；真实测量溢出后才释放 unit 边界换行。
- 截图与 DOM 检查都要确认每个 `.phrase` 只占一行且没有越界。

### PPTX

- `lines` 存在时用 PowerPoint 软换行写入；提供 textFlow 但没有显式 lines 时关闭 Office 自动换行，放不下即调整容器或失败。
- 原生 table 建立后逐 cell 回写 text 与 `wrap=false`，因此显式软换行可保留，同时不允许 Office 再把一个 unit 自动拆开。
- `view issues` 报 overflow 时，Agent 回到 phrase units 重新安排 lines，不能让 PowerPoint 自动在中文词语内部断行。
- 最终逐页截图检查标题、正文、表格、caption 和 metadata；自动问题为零只证明结构没有报告错误，不证明排版自然。

## 验收

- `"".join(units) == 原文`，`"".join(lines) == 原文`；
- 每行都能由连续完整 units 拼成；
- 宽度足够的测试句保持一行；
- 宽度不足时只在指定短语边界换行；
- HTML 与 PPTX 的可见文本、术语和数字单位一致；
- 逐页截图没有拆词、孤立标点或短尾行。

# 分层验证与样例计划

验证按输入、载体、视觉和来源分层执行。任何层失败都保留证据并停止宣称完成；修复后从失败层重跑，不以放宽阈值替代修复。

## 共享 fixture

使用一个公开、无版权争议的成熟逐页内容包，至少含：

1. 封面/问题；
2. 图文解释；
3. 数据或三项结构；
4. 引用或收束；
5. 每页 speaker notes；
6. 一张有替代文本的本地图片或原创几何图。

`collaboration-baseline.json` 必须输出四份成品：瑞士 HTML、瑞士 `.pptx`、杂志 HTML、杂志 `.pptx`。`system-showcase.json` 必须覆盖每个公开页面组件；`test_design_system.py` 必须覆盖每个公开设计方向的令牌完整性与 HTML 映射。公开方向在 `.pptx` 的方向映射由 `validate_pptx.py --style` 与 `check_style_content.py` 定向复验。

fixture 放在 `scripts/fixtures/`，不得使用私密项目、未经授权截图或外部 AGPL 资产。

## 产物 manifest

每次生成写入 JSON manifest，至少包含：

- `inputId`、输入内容哈希、风格、载体、生成时间；
- 页数、每页内容 ID、notes 状态、图片 alt 状态；
- 本地素材哈希、第三方 notice 引用；
- 执行的验证、版本/浏览器/officecli 能力、结果和已知降级；
- 逐页截图或联系表的相对路径。

manifest 不是内容真相源；它只证明给定输入到给定产物的可复验链路。

## HTML 验证矩阵

| 层 | 断言 | 证据 |
| --- | --- | --- |
| 结构 | slide ID 唯一、索引连续、标题/语义/alt 完整、无未声明远程资源 | 结构检查 JSON |
| 交互 | 键盘、按钮、滚轮、触控、页码状态与边界一致 | 浏览器自动测试 |
| 视觉 | 固定桌面、平板、移动视口无裁切/重叠/空白异常 | 截图、联系表、必要 diff |
| 退化 | 静态、无 WebGL、JS 失败、减少动态仍可读可导航 | 四组截图和断言 |
| 无障碍 | 键盘焦点、ARIA 标签/当前页通知、文字对比度达到 AA | a11y/contrast 报告 |
| 来源 | 无受限代码/资产、依赖均有宽松许可证 notice | 来源扫描和 `third-party-notices.md` |

动态截图必须使用固定种子或固定时间步，避免视觉回归因随机帧抖动。

## PPTX 验证矩阵

| 层 | 断言 | 证据 |
| --- | --- | --- |
| 结构 | 文件可重新打开，OpenXML schema 有效 | `officecli validate` |
| 格式 | 无未豁免 overflow、裁切或格式 issue | `officecli view issues` |
| 内容 | 页面文本/映射与输入一致 | outline/text 对照 |
| 讲者与素材 | 每页 notes；图片有有意义 alt text | notes/picture 查询 |
| 可读性 | 字体角色、最小字号、图片比例与风格合同成立 | annotated 输出和逐页截图 |
| 可编辑性 | shape/picture/text 可由 officecli 读回 | DOM 查询与 fresh read-back |

## 执行顺序

1. 运行静态结构/来源检查；
2. 分别生成 HTML 与 `.pptx`；
3. 运行各载体自动验证；
4. 生成固定视口/逐页截图与四象限联系表；
5. fresh T3 重跑定向测试、检查 diff 与产物；
6. 由 T1 对高风险来源、交付边界和视觉收敛做独立审核。

## 停用 guizang 的门槛

仅当四象限样例全部通过上述检查、来源审核没有 AGPL 污染、phase_check 批准且恢复演练已写入 manifest 时，才可把它移动到不被技能发现的可逆备份位置。
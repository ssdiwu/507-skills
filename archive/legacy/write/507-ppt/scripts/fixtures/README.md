# 共享 fixture

`collaboration-baseline.json` 保留 content v1，专门验证旧 `kind + style` 输入可迁移到新系统：封面、图文、三项结构和收束页，以及每页 notes 与一项抽象工作台素材说明。

`system-showcase.json` 是 content v3 基线，覆盖 13 个公开语义叶组件；`system-showcase.visual-plan.json` 独立声明设计语言、逐页视觉呈现、treatment、原型状态和中文短语换行提示。两者配对验证三轴解析、组件专属抑制、原生 chart/table、双载体内容映射与换行合同。

`presentation-pairwise.json` 与配套 visual-plan 用八页分别展示八类视觉呈现，并分布四种 treatment；data 页含两个 series，UI 页含三个带 alt/caption 的 picture，用于真实 HTML/PPTX 渲染压测，不冒充用户内容原型。六个基础设计语言的 token 与组合解析另由单元测试全矩阵覆盖。

fixture 只检查代表性输入，不负责证明所有笛卡尔积均可用。注册表中的 `core / adapted / unsupported` 才是载体支持权威，样例只覆盖代表性组合和兼容路径。

正式 fixture 必须附带内容来源、素材授权、输入哈希和页面映射；任何素材文件还必须进入 `../../third-party-notices.md` 与产物 manifest。

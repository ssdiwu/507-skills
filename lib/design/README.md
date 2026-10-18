# 设计参考

本目录保存可按需使用的呈现提示、交互模式与来源。它属于[共有资源库](../README.md)，没有独立技能入口；参考资料不表示已经实现对应产品组件或取得实际效果。

## 已按清单随包采用的设计提示

| 文件 | 关注内容 |
| --- | --- |
| [artifact-prompts.md](artifact-prompts.md) | 从成熟内容与阅读任务选择呈现方式 |
| [target-design.md](target-design.md) | 中文密页、图表及视觉语义 |
| [apple-interaction.md](apple-interaction.md) | 交互与平台相关参考 |
| [containers-and-motion.md](containers-and-motion.md) | 容器、层次与动效关系 |
| [interaction-detail.md](interaction-detail.md) | 操作、反馈及交互细节 |

具体消费者和携带范围见[packages](../../next/packages.json)。只按当前任务使用相关提示，不能由随包存在推断已执行或已验证。

## 模式与来源资料

| 文件 | 当前身份 |
| --- | --- |
| [patterns.json](patterns.json) | 16 条设计模式，均明确标为仅设计参考、运行未验证 |
| [prompts.md](prompts.md) | 交互合同、阅读比较、动效连续性、预览采用和目标路径的提示资料 |
| [references.md](references.md) | 原始来源、实际观察范围及未覆盖内容 |

模式以 `patterns.json` 维护，参考站可从它生成展示；原 5 提示和模式主要用于对照参考。它们不因位于本目录就全部进入当前安装包。看见外站 Preview 或 Code 不等于代码已采用、运行通过或许可已核对。

实际键盘、触摸、失败、中断、减少动效和目标设备仍在具体消费者环境核验。先复用现有能力，参数服从内容与项目方向，不把参考示例数值固定为全库约束。私人灵感与素材保留原权限，来源研究不自动导入公开资源。

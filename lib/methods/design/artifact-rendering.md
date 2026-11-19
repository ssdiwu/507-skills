# 离线 React 呈现合同

已有作品使用共有 React 导出器、产品演示选用共有场景，或数据工具生成任务页与产品地图时采用。共有组件的字段、安全与示例见[共有图解](../../components/visual/visual-components.md)，运行与写入见[运行合同](../../components/visual/visual-runtime.md)。新建独立阅读页的内容组织与验收见[阅读页方法](reading-page.md)。

制作前读取[视觉方向](visual-direction.md)，选与内容关系相符的结构。已有明确设计直接沿用。打开实际页面检查阅读、布局和操作，发现问题时定位到该页面使用的组件，修正后从同一入口复验。

修改已有页面时，优先复用项目组件、样式和构建入口，在原页面验证。调用共有库 `components/visual/scripts/render-artifact.mjs` 时核对安装依赖，直接引用共有实现。PNG、PPTX、音视频按实际工具核对目标实物。

保全内容、来源、条件与数字单位。使用共有工具时，预渲染和交互使用同一 React 组件，输出可离线打开。共有导出器拒绝覆盖旧输出。记录实际阅读结果、错误和未覆盖项。demo 和 work/coordinate/product-map 的数据工具也使用该呈现层。

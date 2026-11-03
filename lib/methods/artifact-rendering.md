# 离线 React 呈现合同

成熟内容需要离线网页、图卡阅读或幻灯片阅读视图时采用。先辨认时间、步骤、比较、版面与状态关系，直接使用共有 React 对应块；普通文字也由同一入口呈现。组件选择、字段、安全与示例见[共有图解](../components/visual-components.md)，运行与写入见[运行合同](../components/visual-runtime.md)。

制作前读取[视觉方向](visual-direction.md)，选与内容关系相符的结构；实际打开后按其阅读、布局和操作要求检查，发现问题回到共有组件修正，再生成候选。不要把导出成功或结构检查当作阅读完成。已有明确设计直接沿用，不重新向用户索要风格偏好。

唯一入口位于共有库 components/visual-runtime/scripts/render-artifact.mjs。所有技能直接引用，禁止向技能包复制脚本、组件或运行库。依赖需显式可得；缺失不临时复制另一份。PNG、PPTX、音视频仍按实际工具核目标实物，离线 HTML 不冒称这些成品。

内容、来源、条件与数字单位保全。预渲染和交互使用同一 React 组件，输出可离线打开；生成、实际阅读、用户接受与发布分别成立。旧输出拒绝覆盖，错误与未覆盖保留。create/adapt/visualize/demo 直接使用；work/coordinate/product-map 的数据工具也接入相同呈现层。

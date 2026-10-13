# 共有方法、做法与设计资料

lib是当前非Skill资源的唯一维护源，不自行路由或获得写入权。当前28方法源、9脚本源，以及按需组件说明与设计资料；实际消费者、采用条件见[catalog](catalog.json)，随包路径见[next/packages](../next/packages.json)。源改后统一生成普通副本，不手改副本。

## 方法与消费者

原七份来源、决定归属、缺口、反证、验收、权威返回、清晰表达继续使用。新增author-and-source由create/material/compose/adapt消费；artifact-contract由create/compose/adapt消费；artifact-rendering由compose/adapt消费；engineering-evidence由spec/implement/fix/review消费。主入口保留触发、权限、产物和结束。

本轮原位校准authority-and-return、evidence、validation与engineering-evidence，直接消费者仍按具体条件采用；完成回报不替代实际目标验收，不要求新日志、总控或全量必读。

## 具体组件

[components](components/README.md)提供state_diff、work_view、check_run、render_artifact以及原样复用的check_prose/check_spoken。状态/检查/呈现分别完成其局部确定性工作，不代替许可、语义、作者或业务验收；PNG/PPTX/视频未因HTML呈现而完成。

[design](design/README.md)保留16模式、原5提示与来源，并增加成稿适配提示；资料不是技能或通用产品组件。当前技能只携带声明采用的文档，其他资料不成为隐式安装依赖。

工作专用接续方法保留在work-update包内；其余次要方法和48组件接口继续按真实任务取舍，不为了候选数量预造文件。当前范围与未覆盖见[整体覆盖](../doc/10-架构与运行/新体系实现覆盖.md)。

[task-coordination](methods/task-coordination.md)由coordinate/create/work-update按需消费，承载跨领域局部协作、任务图推进和持续协调；[task_view](components/task-view.md)由coordinate/work-update携带，读取已有记录生成临时网页。记录更新重跑组件，呈现不足先扩组件；不直接手改生成网页，不建另一套人工状态或日志。

2026-10-13按旧30实际消费者补齐研究、原型、架构、行为不变、交互、作者采访、知识入口、媒体、视觉与真实接续方法；共有源28份，脚本9段。资料不自行路由。当前清单投影与实物回执见[组件](components/README.md)，逐项来源与退出见[处置记录](../doc/40-版本实施方案/2026-10-13-旧30能力处置.json)。

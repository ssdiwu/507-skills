# 真实交互基础组件

这是共有 React 运行库的一部分，不需要新技能或另一套前端工程。现有产品组件适用时优先使用；没有对应能力时，直接引用这里的控件。源码只维护在当前目录，消费者不复制组件或 node_modules。React 18.3.1、原生 CSS、lucide 图标沿用现有运行库；复杂键盘与焦点行为采用锁定的 Radix UI，未引入 Tailwind 或 Motion。

## 选择与接入

从当前共有库解析绝对路径或项目依赖别名，导入 `ui/index.tsx` 与 `ui/ui.css`。样式只使用 `ui-` 类和 `--ui-` 变量，不重置产品 body。按项目主题覆盖变量。不要指向作者电脑路径，也不要将源码复制进技能或业务项目。

| 任务 | 组件与责任 |
| --- | --- |
| 操作与等待 | Button：primary、secondary、ghost、danger；busy 会禁用重复触发，调用方提供明确文案 |
| 原生表单 | Input、Textarea、Select、Field、Checkbox；Field 自动关联一个原生字段的标签、说明与错误；校验、草稿及正式提交由调用方拥有 |
| 开关与选择 | Switch；Tabs / TabsList / TabsTrigger / TabsContent，列表须有名称、每项与面板 value 对应 |
| 需要阻断的编辑 | Dialog / DialogTrigger / DialogContent / DialogClose；Content 必填标题、说明，非英文场景传 closeLabel；Trigger/Close 用 asChild 包 Button |
| 单步命令 | DropdownMenu / DropdownTrigger / DropdownContent / DropdownItem / DropdownCheckboxItem；选择不等于正式业务成功 |
| 辅助说明 | Tooltip，必要条件仍放正文；Accordion / AccordionItem / AccordionTrigger / AccordionContent，逐步展开补充信息 |
| 结果和缺口 | Badge、Alert、EmptyState、Skeleton、Progress；调用方提供真实状态、结果和恢复操作，不把未知显示为成功 |

DialogContent、Switch、DropdownCheckboxItem 和 AccordionTrigger 自持内部结构，不接受 `asChild`；仅 Trigger/Close 等原样代理支持该组合方式。

`kit/controls` 与 `kit/parts` 是已有演示编排，部分控件使用状态驱动画面，不承担真实输入与键盘保证。真实可操作界面采用本目录；光标、窗口和时间线仍使用 kit。Artifact、TaskView、ProductMap 已直接使用本目录的 Button/Input/Select；产品页面可以组合更多控件，业务内容留在页面，不新增私有通用实现。

## 查看与验证

共有运行库 `npm run dev` 后打开 `/?components`，或用唯一导出器 `node scripts/render-artifact.mjs --components --out-dir <新目录>` 得到单文件离线目录。目录场景也在共有库，只消费本目录控件，不维护另一套实现。导出不会覆盖旧产物。

检查实际填写、错误保留、键盘页签、菜单选择、对话框焦点限制与 Escape/返回、窄屏、长标签和减少动效。目录只改变本页示例状态，刷新即恢复；不连接服务或发送通知。项目正式功能仍须验证自己的权限、数据与失败路径。

接入环境和指定浏览器范围先读[运行合同](../../visual-runtime.md)。需要导出自行组合的离线 React 场景时，入口模块默认导出一个组件并导入当前场景 CSS；挂载、HTML、离线打包、来源指纹与许可由同一个[共有导出器](../scripts/render-artifact.mjs)处理：`node scripts/render-artifact.mjs --scene <入口.jsx或tsx> --title <页面名称> --out-dir <新目录>`。不要各自拼 HTML 或只保留打包器的简短版权头注。场景源码不会在 Node 中执行，只编译给浏览器；组件使用共有 React 版本。输出是含脚本和样式的单文件页面、scene.json 来源图及 manifest.json，拒绝外部导入与覆盖旧输出。可编辑代码仍在原入口，不能把编译文件冒称可编辑场景。正式产品沿其已有构建系统，并按实际依赖交付许可。

## 来源

shadcn/ui 的 MIT Radix 组合已适配为原生 CSS、统一图标和明确标签，固定版本、文件哈希与许可见 [SOURCES.json](SOURCES.json) 和 [许可](licenses/shadcn-ui.txt)。Radix 依赖由共享 package-lock 锁定，导出根据实际编译输入携带依赖许可。Motion Primitives 和 Bencho 仅作交互参考，不捆绑其动效引擎或付费组件。AI Elements 书签页已经提示迁往 shadcn/ui，不安装其将退役的旧注册表。

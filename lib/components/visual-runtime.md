# 共有 React 运行与接入

所有视觉消费者采用同一个 `visual-runtime/`；技能不携带副本。共有库根的定位、组件选择、字段与边界见[组件合同](visual-components.md)。来源与许可见 [NOTICE](visual-runtime/NOTICE.md)、[LICENSE](visual-runtime/LICENSE)、[固定来源](visual-runtime/UPSTREAM.json)。

## 一次依赖安装

要求 Node.js 20.19+、npm。在实际共有库的 components/visual-runtime 中执行 `npm ci --ignore-scripts`，依据锁文件安装一次。无需全局安装或复制依赖到技能。`npm run typecheck`、`npm test`、`npm run test:library`、`npm run test:visuals` 检查类型及共有行为；`npm run dev` 启动仅本机预览，`npm run build` 构建预览。依赖、端口或浏览器不可得时保留具体失败，不改全局配置或结束其他进程。

## 本地发现与接口读取

在实际共有运行库中调用同一个本地脚本，无网络、安装或宿主配置副作用：

```sh
node scripts/component-library.mjs search '表单错误修正'
node scripts/component-library.mjs search '列表详情空状态'
node scripts/component-library.mjs inspect ui:Field
node scripts/component-library.mjs inspect kit:Stage
node scripts/component-library.mjs inspect diagram:queue
node scripts/component-library.mjs inspect example:record-browser
node scripts/component-library.mjs check /absolute/path/scene.tsx
node scripts/component-library.mjs check /absolute/path/scene.tsx --project /absolute/path/tsconfig.json
```

`list`列当前ui与kit的真实值导出、范例和五类图解；`search`按本地中英文关键词匹配，并返回命中词、用途、状态、模拟／真实身份、实际源码和预览相对地址。它不是语义搜索或自动设计判断；无匹配返回NO_MATCH，不能强套第一项。预览地址接到已运行的共有预览服务，命令不启动服务。范例metadata唯一维护在运行库catalog.json，播放器消费同一份；组件导出和接口从当前TypeScript源码及安装声明解析，不另维护属性字典。

`inspect`读取当前接口、必要参数和声明源码，并给出范例与样式路径。属性默认最多返回30项，优先必填与本地声明，其余名称列在omittedProps；声明正文和实际场景检查继续提供完整依据。真实控件用ui，模拟编排用kit，两者的同名Field等通过前缀区分；同名不能互换。

`check`只读取场景及可达依赖，不执行用户代码、不写产物。TSX及JSX均检查；可提供项目tsconfig的路径映射与编译上下文，检查选项保持strict、checkJs与noEmit，并覆盖项目noCheck以确保语义检查实际启用，React类型与导出器使用同一共有版本。检查和导出共用浏览器解析配置，在内存中解析实际依赖图；浏览器条件选择的源码及其调用处均检查，已安装JavaScript依赖以类型声明为边界，不验证其运行时实现。检查仅覆盖入口可达代码，不等于整个调用方项目通过。未知属性、缺必填参数、错误导出或可达文件错误返回INVALID及文件／行／列；any、类型抑制和动态数据仍可能绕过静态约束。CHECKED不代表画面、交互或业务通过。list/search/inspect/check正常成功退出0，未找到或类型错误退出1，输入或依赖错误退出2。

## 单一导出路径

`node scripts/render-artifact.mjs --example --out-dir <新目录>` 生成包含五类图解的虚构示例；`--input <JSON>` 使用当前内容。输出单文件离线 index.html、原输入 content.json 与文件身份清单。服务端预渲染和客户端交互都直接引用 visuals/ 中的 React 组件，不再生成手写交互脚本。

内部数据工具通过共有 `react_export.py` 的 render_document 调同一个 Node 入口。它们继续负责模型验证、来源、版本与文件发布，不拥有界面模板。`--document` 是内部完整模型输入到 HTML 的入口，不写目标文件；外部图解按上述公开输入合同执行。

自行组合的 React 离线场景用同一入口的 `--scene <默认导出组件的jsx或tsx> --title <名称> --out-dir <新目录>`；具体接入见下述 ui 合同。导出前对实际场景调用同一类型检查，失败返回ERROR／退出2和诊断，不创建输出；支持相同的`--project <tsconfig.json>`路径映射。编译后再次核对已检查源码、声明、配置和实际打包文件的指纹及依赖路径未变化，manifest记录类型检查身份与限制。它只在浏览器执行场景，不对输入源码做Node服务端执行，统一处理挂载、样式、依赖许可、来源图和旧产物保护。场景内容与业务状态仍归调用方，不在业务目录另维护通用构建实现。

真实交互的基础控件从 [ui 接入合同](visual-runtime/ui/README.md) 直接引用，包括表单、页签、对话框、菜单和状态反馈。`--components --out-dir <新目录>` 用同一导出入口生成可离线操作的组件目录。现有项目组件适用时继续优先使用；不要为了使用共有控件重写项目设计系统。

编排演示从共有 examples/、kit/ 与播放器开始，当前产品已有组件优先使用。品牌、许可、窗口几何和动画目标按产品与当前内容核对，不只改示例名称。真实业务表单、外部提交、录制与完整成片仍沿原任务。

## 写入与检查边界

安装写共有运行库 node_modules；预览构建写该运行库 playground/dist。两者不是源文件，不进集合清单。导出在系统临时目录编译，完成或失败均回收本次临时文件；原共享源码和技能目录不写入。目标目录通过独占创建拒绝覆盖；写入失败只回收本次创建的文件，保留错误。Node、依赖与实际单文件输出分别检查。

浏览器等宿主工具独立于本技能集合。集合没有同名技能目录，不代表该工具不可用或禁止读取其使用说明。任务或宿主已提供工具时，先用该工具的入口、帮助与实际回执核可用性，再按其说明执行；只有实际失败才记录环境阻塞。不要因目录搜索为空而提前结束必要检查，也不要为补依赖修改全局配置。用户或当前任务已指定浏览器、工作空间或页面时，沿该入口和已读取的工具合同继续；不能为运行方便另起浏览器或绕过指定范围。确实失败时保留回执，独立检查仍可继续。

共有检查工具读取受控页面并写指定新证据目录。不要用真实提交页面作模拟对象；运行器有能力不代表获得外部动作权限。截图与自动报告不代替逐图、完整动作及用户接受。减少动效、窄屏、键盘和失败恢复按本次场景检查。

## 布局工具反馈

已有 `scripts/layout.mjs` 可对受控页面核可见控件和容器的盒尺寸。`--scroll` 将每个匹配区域滚入视口再检查，报告每块边界；区域比视口更大时报告未完整覆盖，不把局部结果写成整块通过。`--screenshot` 只捕获最后一个检查区域所在的视口，其余画面需逐块指定路径取得。

```sh
node scripts/layout.mjs <受控页面URL> --select .viz --scroll --width 390 --report <允许的新报告路径> --strict
```

无此参数仍保持原来的一次视口检查。退出0只代表有覆盖且未发现相应几何问题，1为 strict 下的发现，2为覆盖不全或运行失败；工具不判断审美或业务语义，须按共有视觉方法继续实际看图与核操作。不为通过而忽略区块、缩小内容或修改断言。

`npm run test:ui` 对实际离线目录和图解检查表单、焦点、键盘、窄屏、减少动效及选中样式。

`npm run test:layout` 独立运行布局工具的真实浏览器回归，使用与 layout 相同的已安装 Chrome；没有浏览器时明确失败，不静默跳过。覆盖正常区域、首屏正常但后段裁切、超出视口不完整。它与无需浏览器的运行检查分开，不等同于审美验收。

本地目录、接口读取和场景检查只服务自有共有库；不接入ReUI、MCP或其他远端组件服务。

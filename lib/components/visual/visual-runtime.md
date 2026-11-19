# 共有 React 运行与接入

所有视觉消费者采用同一个 `visual/`；技能不携带副本。共有库根的定位、组件选择、字段与边界见[组件合同](visual-components.md)。来源与许可见 [NOTICE](NOTICE.md)、[LICENSE](LICENSE)、[固定来源](UPSTREAM.json)。

## 一次依赖安装

要求 Node.js 20.19+、npm。使用构建集合时，先将不可变构建包整体复制到安装版本目录，node_modules 和集合内的预览构建输出写入安装目录；对已经安装依赖的目录重新执行不可变构建校验会因新增文件而失败。在实际安装共有库的 components/visual 中执行 `npm ci --ignore-scripts`，依据锁文件安装一次。无需全局安装或复制依赖到技能。`npm run typecheck`、`npm test`、`npm run test:library`、`npm run test:visuals` 检查类型及共有行为；`npm run dev` 启动仅本机预览，`npm run build` 构建预览。依赖、端口或浏览器不可得时保留具体失败，不改全局配置或结束其他进程。

## 本地发现与接口读取

在实际共有运行库中调用同一个本地脚本，无网络、安装或宿主配置副作用：

```sh
node scripts/component-library.mjs search '表单错误修正'
node scripts/component-library.mjs search '列表详情空状态'
node scripts/component-library.mjs inspect kit:Stage
node scripts/component-library.mjs inspect diagram:queue
node scripts/component-library.mjs inspect example:record-browser
node scripts/component-library.mjs check /absolute/path/scene.tsx
node scripts/component-library.mjs check /absolute/path/scene.tsx --project /absolute/path/tsconfig.json
```

`list` 列出演示场景导出、范例和五类图解。`search` 按关键词匹配并返回用途、源码和预览地址，无匹配时返回 `NO_MATCH`。预览地址使用已运行的本地服务。播放器和查找工具共用 `catalog.json`。

`inspect` 读取当前接口、必要参数和声明源码，并给出范例与样式路径。属性默认最多返回 30 项，优先必填与本地声明，其余名称列在 `omittedProps`。

`check`只读取场景及可达依赖，不执行用户代码、不写产物。TSX及JSX均检查；可提供项目tsconfig的路径映射与编译上下文，检查选项保持strict、checkJs与noEmit，并覆盖项目noCheck以确保语义检查实际启用，React类型与导出器使用同一共有版本。检查和导出共用浏览器解析配置，在内存中解析实际依赖图；浏览器条件选择的源码及其调用处均检查，已安装JavaScript依赖以类型声明为边界，不验证其运行时实现。检查仅覆盖入口可达代码，不等于整个调用方项目通过。未知属性、缺必填参数、错误导出或可达文件错误返回INVALID及文件／行／列；any、类型抑制和动态数据仍可能绕过静态约束。CHECKED不代表画面、交互或业务通过。list/search/inspect/check正常成功退出0，未找到或类型错误退出1，输入或依赖错误退出2。

## 单一导出路径

`node scripts/render-artifact.mjs --example --out-dir <新目录>` 生成包含五类图解的虚构示例；`--input <JSON>` 使用当前内容。输出单文件离线 index.html、原输入 content.json 与文件身份清单。服务端预渲染和客户端交互都直接引用 views/ 中的 React 组件，不再生成手写交互脚本。

内部数据工具通过共有 `react_export.py` 的 render_document 调同一个 Node 入口。它们继续负责模型验证、来源、版本与文件发布，不拥有界面模板。`--document` 是内部完整模型输入到 HTML 的入口，不写目标文件；外部图解按上述公开输入合同执行。

React 离线场景用 `--scene <默认导出组件的jsx或tsx> --title <名称> --out-dir <新目录>` 导出。导出前检查实际场景，支持 `--project <tsconfig.json>` 路径映射。检查失败时返回诊断和退出码 2。打包后核对已检查源码、声明、配置和实际打包文件的指纹及依赖路径。场景只在浏览器执行，导出器处理挂载、样式、依赖许可、来源图和旧产物保护。

产品界面的控件沿项目技术与交互方法实现。旧版离线页面从既有导出入口维护，场景发现只提供图解与演示资源。

编排演示从共有 scenes/examples/、scenes/ 与播放器开始，当前产品已有组件优先使用。品牌、许可、窗口几何和动画目标按产品与当前内容核对，不只改示例名称。真实业务表单、外部提交、录制与完整成片仍沿原任务。

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

`npm run test:ui` 检查现有离线页面的导航、状态、键盘焦点和窄屏表现。

`npm run test:layout` 独立运行布局工具的真实浏览器回归，使用与 layout 相同的已安装 Chrome；没有浏览器时明确失败，不静默跳过。覆盖正常区域、首屏正常但后段裁切、超出视口不完整。它与无需浏览器的运行检查分开，不等同于审美验收。

仓库远端自动检查在Python 3.10与3.12两个任务中执行现有类型、发现／调用和导出测试，并执行`npm test`的检查器回归；Chrome与字体环境准备后分别执行`test:ui`和`test:layout`。失败正常阻断，缺浏览器不跳过。它们覆盖固定输入及断言，不替代实际任务的视觉判断、技能自然采用或用户接受。

本地目录、接口读取和场景检查只服务自有共有库；不接入ReUI、MCP或其他远端组件服务。

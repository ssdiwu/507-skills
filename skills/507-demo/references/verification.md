# 检查与回交

用于最终画面及变更后的相关复查。先读[运行说明](../../../lib/components/visual-runtime.md)核依赖、输出位置和副作用；只检查当前版本，不借其他版本的截图验收。

## 运行检查

在运行中的配套资源目录执行，URL 与输出目录使用本次实际值：

```sh
npm run typecheck
npm test
npm run check:css
node scripts/film.mjs 'http://127.0.0.1:5173/?capture=review-card' --still --out <新的证据目录>/card.png --report <新的证据目录>/card.json --gate
node scripts/film.mjs 'http://127.0.0.1:5173/?capture=review-flow' --out <新的证据目录>/flow.png --report <新的证据目录>/flow.json --every 500 --count 24 --gate
node scripts/film.mjs 'http://127.0.0.1:5173/?capture=review-flow' --width 390 --states --states-for 12000 --out <新的证据目录>/states.png --report <新的证据目录>/states.json --gate
node scripts/film.mjs 'http://127.0.0.1:5173/?capture=review-flow' --width 390 --reduced --still --out <新的证据目录>/poster.png --gate
```

命令中的地址与场景只是本包示例，真实交付须检查实际宿主页及其宽度。静态作品不跑无关的运动采样；动画看完整动作和循环／停留，不用一张静帧替代。普通预览有 iframe，film 应直接访问 `capture` 路径。

报告 `no-issues-detected` 表示覆盖内未检出候选问题，`issues` 表示有候选，`inconclusive` 表示采样或环境不足。本地修订将 gate 状态一并写入 JSON：覆盖完整但 gate 失败退出 1，采样不足保留退出 2 且不显示 passed。退出 0 不表示画面、语义或业务通过；`--gate` 的 `rehearsal passed` 同样只覆盖已执行规则。上游检查含营销展示的固定几何偏好，发现后对照目标画面判断适用性，不能为通过而隐藏必要内容或大范围标注忽略。覆盖不完整时保留未定结果，不能通过降低采样要求宣称通过。详细信号见 [Rehearse](../../../lib/components/visual-runtime/references/rehearse.md)。

## 看当前画面与操作

核开场、结果、最密状态和动作中间帧：焦点、中文、单位、裁切、图标、浮层、光标落点及循环衔接。按实际交付检查宽度、减少动态效果、播放／暂停／恢复／重播和离屏返回；同页多场景要检查两个场景是否互相操作或错用目标。真实触摸和目标设备未验时单列，390px 截图只证明该视口。

独立审查者取得当前要求、场景、实物和实际检查证据，核完整需求与画面，不只依据制作人的解释或自动结论。可采用上游 [Review](../../../lib/components/visual-runtime/references/review.md) 的按帧定位问题方法，但它“仅提供一句简报”的限制不取代本次已确认要求；行为、数据、接口或正式需求变化按原项目的独审合同处理。

## 交回

交回内容和场景版本、可编辑文件、目标实物、实际检查的宽度／状态／工具、发现及未覆盖。源码、HTML、PNG、联系表和视频各自命名；需要视频时继续原媒体流程取得可播放文件。人的接受和公开发布不由技术检查代替。

记录放在本次交付约定的位置，不把客户数据、用户本机绝对路径、会话凭据或私有原始回执带入公开技能包。

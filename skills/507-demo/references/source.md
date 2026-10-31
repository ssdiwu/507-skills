# 来源与取舍

本包参考 Benji Taylor 的 [Stageshow](https://github.com/benjitaylor/skills/tree/802057409787133703c56001080169e347305572/stageshow)，固定提交 `802057409787133703c56001080169e347305572`。上游源码采用 MIT；携带原许可位于 [runtime/LICENSE](../runtime/LICENSE)，逐文件上游路径与指纹见 [UPSTREAM.json](../runtime/UPSTREAM.json)。

采用的是“产品识别、画面构图、动作因果、范例起步、实际画面检查”的方法，以及通用 React kit、检查脚本、三个完整范例和隔离播放器。技能入口以本包中文合同为准，上游 `SKILL.md` 不作为第二入口携带。

为减少不必要的素材与使用条件，本包排除品牌注册表、BrandMark、应用图标及真实产品研究。随包 NOTICE 说明这一范围；上游的商标与素材许可不因 MIT 自动转为通用授权。kit 的三个聚合入口删除 BrandMark 导出／样式引用，其余采用文件的原版指纹与改造说明在 UPSTREAM.json 中保留。

三份上游范例为 static-card、form-error、payout-flow。review-card 和 review-flow 从前两者改成中文虚构项目展示，dual 用两个中文反馈场景检查共存；它们不表述任何客户或已上线产品能力。播放器目录清单与文字作相应调整，预览依赖改为锁定本地版本、移除自动 portless 安装。

上游引用中未携带的范例和 BrandMark 条目保留其研究语境，不表示本包可调用；当前可用目录由 runtime/playground/catalog.ts 与精确包清单声明。它不是完整镜像，更新时核采用文件、局部修改及依赖，不覆盖本地适配后直接宣称同版。

上游 film 的 gate 失败退出码原会被普通报告覆盖；本地在 film.mjs 和 verification.mjs 合并最终 gate 状态、JSON 与退出码，保留采样不足为 inconclusive／2，避免仍显示 passed。配套 verification.test.mjs 覆盖非 strict 失败、采样不足、成功及旧 strict 行为。

## 维护归属

当前只有本技能直接使用 runtime，因此组件、范例和检查工具随包维护；没有先建共有组件入口或单独发布库。未来有第二个真实直接使用方时，再依据公共 API、依赖、版本和验证决定抽取，保留单项可独立运行。创作、适配或工程采用本技能不自动算作组件的直接使用方。

构图方法不替代实际产品设计；模拟点击不证明业务可用；有限示例不证明自然触发或长期制作收益。目标文件、真实目标宿主和独立审查分别保留证据。

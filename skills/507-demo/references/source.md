# 来源与取舍

本包参考 Benji Taylor 的 [Stageshow](https://github.com/benjitaylor/skills/tree/802057409787133703c56001080169e347305572/stageshow)，固定提交 `802057409787133703c56001080169e347305572`。上游源码采用 MIT；原许可位于[共有运行库 LICENSE](../../../lib/components/visual-runtime/LICENSE)，逐文件上游路径与指纹见 [UPSTREAM.json](../../../lib/components/visual-runtime/UPSTREAM.json)。

采用的是“产品识别、画面构图、动作因果、范例起步、实际画面检查”的方法，以及通用 React kit、检查脚本、三个完整范例和隔离播放器。技能入口以本包中文合同为准，上游 `SKILL.md` 不作为第二入口携带。

为减少不必要的素材与使用条件，本包排除品牌注册表、BrandMark、应用图标及真实产品研究。随包 NOTICE 说明这一范围；上游的商标与素材许可不因 MIT 自动转为通用授权。kit 的三个聚合入口删除 BrandMark 导出／样式引用，其余采用文件的原版指纹与改造说明在 UPSTREAM.json 中保留。

三份上游范例为 static-card、form-error、payout-flow。review-card 和 review-flow 从前两者改成中文虚构项目展示，dual 用两个中文反馈场景检查共存；它们不表述任何客户或已上线产品能力。播放器目录清单与文字作相应调整，预览依赖改为锁定本地版本、移除自动 portless 安装。

上游引用中未携带的范例和 BrandMark 条目保留其研究语境，不表示本包可调用；当前可用目录由 `<共有库>/components/visual-runtime/playground/catalog.ts` 与精确包清单声明，`<共有库>` 指当前技能所在集合的 `lib/`。它不是完整镜像，更新时核采用文件、局部修改及依赖，不覆盖本地适配后直接宣称同版。

上游 film 的 gate 失败退出码原会被普通报告覆盖；本地在 film.mjs 和 verification.mjs 合并最终 gate 状态、JSON 与退出码，保留采样不足为 inconclusive／2，避免仍显示 passed。配套 verification.test.mjs 覆盖非 strict 失败、采样不足、成功及旧 strict 行为。

## 维护归属

组件、范例、播放器与检查工具只在共有库 `lib/components/visual-runtime/` 一份。所有消费者直接引用，同一集合显式提供依赖；技能不携带运行库、脚本或共有说明副本。所有视觉组件统一 React，来源提交、原版指纹、许可和原有改造保留。

构图方法不替代实际产品设计；模拟点击不证明业务可用；有限示例不证明自然触发或长期制作收益。目标文件、真实目标宿主和独立审查分别保留证据。

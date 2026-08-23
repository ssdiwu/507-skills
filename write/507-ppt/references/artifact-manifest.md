# 产物 manifest v2

新产物使用 manifest v2；旧 v1 只作兼容读回。Manifest 证明给定内容与 visual-plan 产生了某个经验证产物，不是内容或设计的第二事实源。

```json
{
  "version": 2,
  "inputId": "system-showcase",
  "inputSha256": "hex",
  "carrier": "pptx",
  "artifact": "system-showcase.pptx",
  "sha256": "hex",
  "visualPlan": "system-showcase.visual-plan.json",
  "visualPlanSha256": "hex",
  "language": {"id": "precision-modern", "variant": "default"},
  "prototypeStatus": "approved",
  "prototypeEvidence": [{"kind": "prototype-manifest", "path": "system-prototypes/approved-prototype-manifest.json", "sha256": "hex"}],
  "pages": [{
    "id": "chart",
    "component": "chart",
    "presentation": "data-led",
    "treatment": "default",
    "carrierSupport": "native",
    "suppressedDecorations": [],
    "textFlowStatus": "screenshot-verified",
    "notesStatus": "provided",
    "altStatus": "not-applicable",
    "assets": [],
    "screenshot": "system-showcase-pptx-evidence/slide-12.png",
    "screenshotSha256": "hex"
  }],
  "assets": [],
  "notices": ["../third-party-notices.md"],
  "verification": [{"name": "pptx-axis-content", "kind": "axis-content", "status": "passed", "evidence": "system-showcase-pptx-axis-content.json", "evidenceSha256": "hex"}],
  "screenshots": ["system-showcase-pptx-evidence/slide-12.png"],
  "degradations": [],
  "capabilities": {"supportMatrix": "system-showcase-support-matrix.json", "supportMatrixSha256": "hex"}
}
```

## 必须成立

- 内容与 visual-plan 文件及哈希都可复验；
- page ID、组件、presentation、treatment、carrier support、suppression、notes、alt 与资产映射都由内容和 resolver 重新计算；
- degradation 必须与全部 adapted 页的预期列表精确相等，不能缺失、伪造或多写；
- approved prototype 回链 approved manifest、选中候选、候选 artifact/plan 与联系表哈希；混合候选回链合并原型；
- 资产、notice、截图和 verification evidence 均为相对路径并存在；
- page 记录 suppression，并以逐页真实截图把 textFlow 标为 `screenshot-verified`；只通过 plan 静态校验不能建最终 manifest；
- verification report 绑定 input/plan/artifact hash，checks 必须全部 passed；HTML 还必须有逐页 `html-browser` 报告；
- support matrix 逐页记录 HTML/PPTX 的 native/adapted 状态与抑制项，并以哈希绑定；
- HTML/PPTX 可有独立 manifest，但必须引用同一内容与 visual-plan。

生成入口为 `scripts/build_manifest.py`，验证入口为 `scripts/validate_manifest.py`。

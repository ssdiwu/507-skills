# 产物 manifest 合同

每个生成结果配套一个 JSON manifest。最低字段：

```json
{
  "version": 1,
  "inputId": "string",
  "inputSha256": "hex",
  "style": "swiss | magazine",
  "carrier": "html | pptx",
  "pages": [{"id": "string", "notes": true, "assets": []}],
  "assets": [{"path": "relative", "alt": "string", "sha256": "hex"}],
  "notices": ["relative notice path"],
  "verification": [{"name": "string", "status": "passed | failed", "evidence": "relative path"}],
  "degradations": [],
  "screenshots": []
}
```

`scripts/validate_manifest.py` 拒绝缺失必须字段、非相对路径、未知风格/载体、产物/素材哈希不匹配、页面映射不完整或 `passed` 却没有证据路径的 manifest。
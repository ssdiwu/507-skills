# 交互点地图组件

`product_map.py`只用Python标准库，读取一份明确的地图JSON，生成离线HTML、原记录、投影与指纹清单。自身不联网、运行产品、扫描源码、采集证据或编辑业务；独立包携带此合同与脚本，不依赖作者仓库。

```sh
python3 product_map.py --record map.json --check
python3 product_map.py --record map.json --out-dir map-view-r1
```

退出0只表示模型校验或生成成功，2为输入／运行错误。`--check`只读；生成只写新的输出目录，已有目录（包括手改网页）拒绝覆盖，错误保留旧产物。更新同一记录后指定新输出目录，调用方网站从回执引用新版本；不直接改HTML。输出阶段失败清理自身临时目录。最多读取2MiB普通文件，拒绝重复JSON键、重复身份、无效类型／来源／边／路径、包含循环、非有限数字与非法UTF-8。

## 输入模型（schema 1）

顶层为`schema/title/scope/sources/nodes/edges/paths`，不接受其它字段。scope含`goal/boundary/version/conditions/limitations/coverage`，其中conditions和limitations为字符串数组，coverage为`partial`或`claimed-complete`；后者是作者声明，组件不核完备性。

sources是`id/kind/label/locator`，kind为design/code/runtime/other；可加revision。locator保留原路径、行号、URL或日志身份作为纯文本，不执行也不自动验证引用文件。节点为`id/kind/label/purpose/conditions/outcomes/evidence`；kind为page/tab/button/form/field/drawer/dialog/link/toggle/menu。静态分组不在节点类型中。

每个evidence对象须有design、implementation、runtime三个数组，可以为空。每条记录必有`state/sourceIds/scope/note`。状态：design支持confirmed/proposed/not-required/unknown；implementation支持declared/wired/partial/missing/unknown；runtime支持passed/failed/partial/not-observed。非unknown／not-observed记录必须引用对应种类的来源；运行记录的passed/failed/partial另外要求action/role/input/environment/version/observed六个非空字段。未观察可写同样字段，但不据字段存在改为已观察。来源引用是否真实以及范围是否匹配由Agent与独立审读者核对。

边含`id/from/to/kind/condition/evidence`，kind为contains/enter/open/switch/return/trigger；from/to引用节点。包含不能形成循环，多父级允许；操作返回和循环允许。paths含`id/label/edgeIds/conditions/evidence`，edgeIds至少一条并须连续，表达指定条件下的路径；路径运行证据独立记录，不由节点状态推导。

网页提供包含树、节点筛选／搜索、三维证据详情、入出关系点击与路径查看。筛选只改变显示，详情仍可访问筛选外的关联节点；多父级下同一ID显示引用。选定节点写入地址，后退、前进或重载从地址恢复同一详情。每维显示原证据条数与未知，不汇总成一个绿灯。sources、record SHA及原模型保留；manifest的meaningVerified和acceptanceVerified始终false。

示例和坏输入覆盖见`tests/test_product_map.py`。source为本目录，运行副本由packages登记生成；结构PASS不是需求确认、证据真实或产品接受。

## 最小有效结构示例

以下只是写记录的格式起点，不是产品事实或已采证结果。把示意身份替换成真实交互点后按实际证据填写；空数组保留未知，不为了填满而造来源。action、role、input、environment、version、observed六字段只属于运行条目，不能加进设计／实现条目。

```json
{
  "schema": 1,
  "title": "格式示例，非产品验收",
  "scope": {
    "goal": "示意目标", "boundary": "一个示意按钮", "version": "待替换真实版本",
    "conditions": [], "limitations": ["没有实际采证"], "coverage": "partial"
  },
  "sources": [],
  "nodes": [{
    "id": "sample.button", "kind": "button", "label": "示意按钮", "purpose": "待替换实际用途",
    "conditions": [], "outcomes": [],
    "evidence": {"design": [], "implementation": [], "runtime": []}
  }],
  "edges": [], "paths": []
}
```

证据条目的缺失或多余字段会定位到节点／边／路径身份、证据维度及条目索引，并列出缺失和未支持字段；修具体位置后重新检查，不需要盲扫整份记录或删除其它有效证据。

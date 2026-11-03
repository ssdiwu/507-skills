#!/usr/bin/env python3
"""Generate the current skill responsibilities and direct shared dependencies."""
import argparse
import json
import importlib.util
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'lib/skill-resource-map.md'
def render():
 d=json.loads((ROOT/'packages.json').read_text());spec=importlib.util.spec_from_file_location('resource_library',ROOT/'lib/components/library_view.py');library=importlib.util.module_from_spec(spec);spec.loader.exec_module(library);d['skills']=library.resource_entries(ROOT,d);lines=['# 技能职责与共有库直接依赖','','本表由现行入口合同、packages.json 身份登记和每技能 RESOURCES.md 资源声明生成。所有技能目录只保留职责、采用条件、交付标准、专用文字方法和元数据；执行代码、共有方法、React 组件、范例与运行工具只在 lib 存在一份。技能集合按 skills/ 与 lib/ 并列布局使用，禁止生成共有资源副本。','','| 技能 | 独有职责 | 直接执行入口／运行依赖 | 共有方法 |','| --- | --- | --- | --- |'];details=[]
 for e in d['skills']:
  raw=(ROOT/e['source']/'SKILL.md').read_text();purpose=re.search(r'^description:\s*(.+)$',raw,re.M).group(1).strip('"').split('。')[0]+'。';uses=e['uses'];methods=[s for s in uses if s.startswith('lib/methods/')];code=[s for s in uses if s.endswith(('.py','.mjs'))];label='、'.join('['+Path(s).name+']('+s.removeprefix('lib/')+')' for s in code) or '按条件读取共有方法，无执行工具'
  lines.append('| ['+e['name']+'](../'+e['source']+'/SKILL.md) | '+purpose.replace('|','／')+' | '+label+' | '+str(len(methods))+' 份 |')
  details+=['','## '+e['name'],'','[资源声明](../'+e['source']+'/RESOURCES.md)','',*['- ['+s.removeprefix('lib/')+']('+s.removeprefix('lib/')+')' for s in uses]]
 lines+=['','## 统一分工','','- create：负责作品内容和作者表达；呈现直接调用共有 React，复杂产品演示可按需采用 demo 的工作方法。','- adapt：负责受众、阅读关系和载体；直接调用共有 React，不读取或复制 demo 的运行资源。','- visualize：负责图的关系、单位、来源、未知与理解路径；图解组件直接调用共有 React。','- demo：负责产品识别、构图和动作编排；不拥有专属 kit、运行库或通用组件。','- work、coordinate、product-map：负责各自记录、关系与证据模型，展示层同样直接使用共有 React。','- do：负责真实产品行为，先复用目标产品组件；React依赖与构建适用且缺少对应控件时直接采用共有 ui，离线React场景也由共有入口导出。模拟展示不作为业务实现或验收。','- review：独立核职责、直接依赖、复制回归、实际效果与未覆盖；不修改受审内容。','',*details]
 return '\n'.join(lines)+'\n'
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();content=render()
 if args.check:
  if not TARGET.is_file() or TARGET.read_text()!=content:raise SystemExit('Stale skill resource map')
 else:TARGET.write_text(content)
 print('Skill resource map checked' if args.check else 'Skill resource map generated')

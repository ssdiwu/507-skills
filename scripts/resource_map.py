#!/usr/bin/env python3
"""Generate the current skill responsibilities and direct shared dependencies."""
import argparse
import json
import importlib.util
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'lib/catalog/skill-resource-map.md'
CATEGORIES = ('方法', '工具', '界面组件', '库务资料', '库维护测试')

def dependency_role(source):
 path = Path(source).relative_to('lib')
 name = path.name
 location = path.as_posix()
 if location.startswith(('methods/', 'components/visual/references/')):
  return '方法', '指引'
 if location.startswith('catalog/registry/') or name in {'LICENSE', 'UPSTREAM.json', 'SOURCES.json'}:
  return '库务资料', '登记与溯源'
 if location in {'README.md', 'components/visual/catalog.json'}:
  return '库务资料', '导航'
 if name.endswith('.test.mjs'):
  return '库维护测试', '回归测试'
 if name == 'package.json':
  return '工具', '运行配置'
 if location.startswith('components/visual/scenes/examples/'):
  return '界面组件', '示例'
 if location.startswith('components/visual/ui/') or name in {'visual-components.md', 'visual-runtime.md'}:
  return '界面组件', '接入说明' if path.suffix == '.md' else '实现与样式'
 if location.startswith('components/tools/') and path.suffix == '.md':
  return '工具', '使用说明'
 if location.startswith('components/') and path.suffix in {'.py', '.mjs'}:
  return '工具', '执行文件'
 raise ValueError(f'请核对新增直接依赖的用途分类：{source}')

def render():
 d=json.loads((ROOT/'packages.json').read_text());spec=importlib.util.spec_from_file_location('resource_library',ROOT/'lib/components/tools/projections/library_view.py');library=importlib.util.module_from_spec(spec);spec.loader.exec_module(library);d['skills']=library.resource_entries(ROOT,d);lines=['# 技能职责与共有库直接依赖','','本表由现行入口合同、packages.json 身份登记和每技能 RESOURCES.md 资源声明生成。所有技能目录只保留职责、采用条件、交付标准、专用文字方法和元数据；执行代码、共有方法、React 组件、范例与运行工具只在 lib 存在一份。技能集合按 skills/ 与 lib/ 并列布局使用，禁止生成共有资源副本。','','| 技能 | 独有职责 | 直接执行入口／运行依赖 | 共有方法 |','| --- | --- | --- | --- |'];details=[]
 lines[-2:] = [
  '各列按用途统计声明文件。工具列统计交付工具，库维护测试列标明维护共有库时需要回归的技能。每项声明在合计中只计一次。点击技能名查看明细。',
  '', '| 技能 | 独有职责 | ' + ' | '.join(CATEGORIES) + ' | 合计 |',
  '| --- | --- | ' + ' ---: |' * (len(CATEGORIES) + 1)]
 for entry in d['skills']:
  raw = (ROOT / entry['source'] / 'SKILL.md').read_text()
  purpose = re.search(r'^description:\s*(.+)$', raw, re.M).group(1).strip('"').split('。')[0].replace('|', '／')
  groups = {category: [] for category in CATEGORIES}
  for source in entry['uses']:
   category, role = dependency_role(source)
   relative = source.removeprefix('lib/')
   groups[category].append(f'- {role} · [{relative}](../{relative})')
  name = entry['name']
  counts = ' | '.join(str(len(group)) for group in groups.values())
  lines.append(f'| [{name}](#{name}) | {purpose}。 | {counts} | {len(entry["uses"])} |')
  details.extend(['', f'## {name}', '', f'[技能说明](../../{entry["source"]}/SKILL.md) · [资源声明](../../{entry["source"]}/RESOURCES.md)'])
  for category, items in groups.items():
   if items:
    details.extend(['', f'### {category}（{len(items)}）', '', *items])
 lines+=['','## 统一分工','','- create 负责作品内容和作者表达，adapt 负责受众与载体，visualize 负责图解关系与理解路径。新建独立阅读页采用[阅读页方法](../methods/design/reading-page.md)，修改已有页面优先复用项目组件。','- demo：负责产品识别、构图和动作编排；不拥有专属 kit、运行库或通用组件。','- work 和 coordinate 校验过程记录，再按[任务页方法](../methods/design/task-page.md)组织页面。product-map 校验交互与证据记录，再按[地图页方法](../methods/design/product-map-page.md)组织页面。共有 React 渲染器继续承接已有生成页。','- do：负责真实产品行为，先复用目标产品组件；React依赖与构建适用且缺少对应控件时直接采用共有 ui，离线React场景也由共有入口导出。模拟展示不作为业务实现或验收。','- review：独立核职责、直接依赖、复制回归、实际效果与未覆盖；不修改受审内容。','',*details]
 return '\n'.join(lines)+'\n'
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();content=render()
 if args.check:
  if not TARGET.is_file() or TARGET.read_text()!=content:raise SystemExit('Stale skill resource map')
 else:TARGET.write_text(content)
 print('Skill resource map checked' if args.check else 'Skill resource map generated')

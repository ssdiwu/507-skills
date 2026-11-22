# 共有资源合同

lib 是所有技能共同使用的一份资源库，不是技能入口，也不自行启动任务或取得操作授权。各技能仅保留任务职责、采用条件、权限、交付与专用文字方法；通用方法、执行代码、视觉组件、范例、播放器和检查工具只在 lib 存在一份。禁止往技能目录复制、生成或维护对应实现。

## 明确的分工

技能决定当前任务采用什么方法、保护什么、怎样判断交付。独立页面按读者任务与参考组织，见[阅读页方法](methods/design/reading-page.md)。React 运行库服务于既有图解、演示、任务视图和产品地图的重导。Python 工具负责校验、投影、比较、文件与检查。详情见[技能资源关系](catalog/skill-resource-map.md)与[React 导出合同](components/visual/visual-components.md)。

## 定位和依赖

### 查定义与决定

按技能给定的条件执行时直接继续。两个名称容易混淆时先查定义。准备合并对象、更改默认行为或撤销规则时，再核原决定的取舍及后继记录。有同版源码时从仓库的 `doc/README.md` 进入。仅持有安装集合时，可按下表打开已核对版本的仓库原文。离线且缺少原文时，沿已知合同执行，待能核实理由后再评议变更。

| 要核对的内容 | 仓库原文 |
| --- | --- |
| 对象定义、当前职责及验收要求 | [术语表](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/GLOSSARY.md) · [规格入口](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/spec/README.md) |
| 连续文章与逐页摘要的内容单位 | [0015 图文取舍](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/doc/决策档案/0015-小红书图文区分连续文章与视觉摘要.md) |
| 本地提交与外部发布的权限 | [0010 可逆性](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/doc/决策档案/0010-commit与release按可逆性边界拆分.md) · [0021 入口整合](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/doc/决策档案/0021-同职责入口按权限与产物分流.md) |
| 技能分层、验收分工与资源归属 | [分层依据](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/doc/10-架构与运行/技能分层设计依据.md) · [0025 共有资源归属](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/doc/决策档案/0025-按用途组织共有资源库.md) |
| 存量规格应保留在哪里 | [0020 规格归属与迁移取舍](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/doc/决策档案/0020-现行规格独立维护与存量项目迁移.md) |

查完理由后，回到这份安装集合的执行合同：

| 要判断的工作 | 本版技能 | 对应定义或规格 |
| --- | --- | --- |
| 全文排版或提炼摘要 | [成稿适配](../skills/507-adapt/SKILL.md) | [作品术语](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/GLOSSARY.md#跨任务与作品术语) · [图文内容模式与验收](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/spec/507-rednote.md) |
| 提交或对外发布 | [软件交付](../skills/507-deliver/SKILL.md) | [操作授权](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/GLOSSARY.md#分层与共有资源) |
| 合并入口或转移共有方法 | [技能设计](../skills/skill-design/SKILL.md) | [分层与共有资源规格](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/spec/技能分层与共有资源.md) |
| 自查或独立验收 | [独立审查](../skills/507-review/SKILL.md) | [验收职责](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/GLOSSARY.md#会话分层与验收职责) |
| 从旧方案中辨认仍有效的要求并迁入规格 | [规格整理](../skills/507-spec/SKILL.md) · [项目依据维护](../skills/507-setup/SKILL.md) | [规格入口](https://github.com/ssdiwu/507-skills/blob/b119782d741521d5cdce5dd969a873758b21a8e3/spec/README.md) |

### 阶段返回

持有原任务的执行者在局部修订、提交或审查完成，准备切回已约定的下一阶段时，若当前任务已指定交接文档，重新打开其现行版本，核对本轮用户修订、实际产物、剩余交付及授权。已完成项以产物为据，条件已满足的事项直接继续，待用户决定的事项保留到相应步骤。交接中的新增动作沿用本轮授权边界。没有指定交接时沿用当前请求、上下文和实际产物；单项任务完成即可结束。交接无法读取时说明影响并继续独立可做的事项。

集合固定为 skills/ 与 lib/ 并列。安装时保留完整集合层级，入口软链接指向准备好的集合根目录，使可见路径中的相对引用与集合内关系一致。历史安装入口可能只链接 skills/，其可见层级与源码层级不同；以下真实路径解析继续支持这种安装及嵌套参考。需要读取参考时，先解析**链接所在文档文件**的软链接，再以其真实文件所在目录解析原相对链接。进入嵌套参考后，以该参考自己的位置为基准；不沿用最初 SKILL.md 的目录，不从业务工作目录或安装入口的字符串猜父目录。

读取工具未自动处理时，用标准库取得当前引用的真实位置，再读取文件。第一个参数是当前文档路径，第二个参数是原相对文件链接（可含章节锚点）；命令去掉章节锚点并解码链接中的路径转义，仅含锚点时保留当前文档，目标缺失时以错误退出：

```sh
python3 -c 'from pathlib import Path; from urllib.parse import unquote; import sys; document = Path(sys.argv[1]).resolve(strict=True); reference = unquote(sys.argv[2].split("#", 1)[0]); print((document.parent / reference).resolve(strict=True) if reference else document)' '<当前文档路径>' '<原相对文件链接>'
```

只定位当前任务需要的资源，已确认位置在本次任务中复用；定位不扩大读取、执行或写入许可。解析后仍缺失时报告具体文档、引用和影响，不逐级猜目录、写私人绝对路径、让用户配置内部路径或复制资源兜底；不依赖该资源的工作继续。技能执行需要已声明共有依赖，React 工具在共有运行库按锁文件安装一次依赖。

## 唯一事实与更新

每个技能的 `RESOURCES.md` 独立声明自有 files 与直接共有 uses，是这两项的唯一维护源；路径分别相对技能目录与集合根。[packages.json](../packages.json)只登记身份、角色、目录、声明位置和共有文件精确集合，不重复保存 files/uses。正文与专用参考实际链接的共有文件须登记；[catalog.json](catalog/catalog.json)保留共有资源采用条件与消费者对账；[逐技能关系](catalog/skill-resource-map.md)由现行合同和清单生成。调用条件变化改拥有该任务的技能及共有合同，代码变化改 lib 唯一源，受影响消费者共同验证。数据投影不是新的业务权威。

检查会拒绝技能中的执行代码、runtime、共有副本标记、未知文件、越界引用、软链接、缺失依赖和失效索引；构建只包含一份 lib。新增技能或滚动更新须沿同一规则，不能另建专属组件体系。历史副本与原验证证据仅留历史／恢复范围，不纳入活动技能发现和交付。

导航：[共有方法](methods/README.md) · [执行组件](components/README.md) · [设计参考](methods/design/README.md)；技能入口位于同一集合的 skills/。结构、检查、实际运行、自然采用、用户接受与发布分别判断。

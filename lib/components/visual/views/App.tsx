import React from 'react'
import {Showcase} from '../ui/Showcase'
import {Artifact} from './Artifact'
import {TaskView,ProductMap} from './Views'
import {DocumentModel} from './model'
export function App({model}:{model:DocumentModel}){switch(model.kind){case 'components':return <Showcase/>;case 'artifact':return <Artifact data={model.data}/>;case 'task-view':return <TaskView data={model.data}/>;case 'product-map':return <ProductMap data={model.data}/>;case 'entry':return <main><p><a href={model.data.href}>打开当前任务视图</a></p><p>生成产物；更新原过程记录后重跑共有组件。</p></main>}}

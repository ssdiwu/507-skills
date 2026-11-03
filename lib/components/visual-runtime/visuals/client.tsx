import React,{useEffect} from 'react'
import {hydrateRoot} from 'react-dom/client'
import {App} from './App'
const model=JSON.parse(document.getElementById('visual-model')!.textContent!)
function Mounted(){useEffect(()=>{document.documentElement.dataset.reactReady='true'},[]);return <App model={model}/>}
hydrateRoot(document.getElementById('app')!,<Mounted/>)

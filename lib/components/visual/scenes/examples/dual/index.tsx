import ReviewFlow from '../review-flow'
import './dual.css'

export default function Dual() {
  return <div className="demo-dual"><section aria-label="第一个界面演示"><ReviewFlow /></section><section aria-label="第二个界面演示"><ReviewFlow /></section></div>
}

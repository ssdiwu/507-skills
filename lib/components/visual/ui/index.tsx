import React, {forwardRef, useId} from 'react'
import {Dialog as D, Tabs as T, DropdownMenu as M, Tooltip as H, Switch as S, Accordion as A} from 'radix-ui'
import {Check, ChevronDown, LoaderCircle, X, Inbox, CircleAlert} from 'lucide-react'

const cx = (...parts:(string|false|undefined)[]) => parts.filter(Boolean).join(' ')
type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {variant?:'primary'|'secondary'|'ghost'|'danger';busy?:boolean}
export const Button = forwardRef<HTMLButtonElement,ButtonProps>(function Button({variant='secondary',busy=false,disabled,className,children,type='button',...props},ref){
 return <button {...props} ref={ref} type={type} className={cx('ui-button',`ui-button-${variant}`,className)} disabled={disabled||busy} aria-busy={busy||undefined}>{busy&&<LoaderCircle className="ui-spin" size={16} aria-hidden="true"/>}{children}</button>
})
export const Input = forwardRef<HTMLInputElement,React.InputHTMLAttributes<HTMLInputElement>>(function Input({className,...props},ref){return <input {...props} ref={ref} className={cx('ui-input',className)}/>})
export const Textarea = forwardRef<HTMLTextAreaElement,React.TextareaHTMLAttributes<HTMLTextAreaElement>>(function Textarea({className,...props},ref){return <textarea {...props} ref={ref} className={cx('ui-input','ui-textarea',className)}/>})
export const Select = forwardRef<HTMLSelectElement,React.SelectHTMLAttributes<HTMLSelectElement>>(function Select({className,...props},ref){return <select {...props} ref={ref} className={cx('ui-input','ui-select',className)}/>})
/** Owns the label/error association for one native input, textarea or select. */
export function Field({label,hint,error,children}:{label:React.ReactNode;hint?:React.ReactNode;error?:React.ReactNode;children:React.ReactElement}){
 const generated=useId(),id=children.props.id??generated,hintId=id+'-hint',errorId=id+'-error'
 const described=[children.props['aria-describedby'],hint&&hintId,error&&errorId].filter(Boolean).join(' ')||undefined
 return <div className="ui-field"><label htmlFor={id}>{label}</label>{React.cloneElement(children,{id,'aria-describedby':described,'aria-invalid':error?true:children.props['aria-invalid']})}{hint&&<p id={hintId} className="ui-hint">{hint}</p>}{error&&<p id={errorId} className="ui-error">{error}</p>}</div>
}
export function Checkbox({label,hint,...props}:React.InputHTMLAttributes<HTMLInputElement>&{label:React.ReactNode;hint?:React.ReactNode}){
 const id=useId();return <label className="ui-choice"><input {...props} type="checkbox" aria-describedby={[props['aria-describedby'],hint&&id].filter(Boolean).join(' ')||undefined}/><span><span>{label}</span>{hint&&<small id={id}>{hint}</small>}</span></label>
}
export function Switch({label,hint,...props}:Omit<React.ComponentPropsWithoutRef<typeof S.Root>,'asChild'|'children'>&{label:React.ReactNode;hint?:React.ReactNode}){
 const id=useId();return <div className="ui-choice"><S.Root {...props} asChild={false} id={props.id??id} className={cx('ui-switch',props.className)} aria-describedby={[props['aria-describedby'],hint&&id+'-hint'].filter(Boolean).join(' ')||undefined}><S.Thumb className="ui-switch-thumb"/></S.Root><label htmlFor={props.id??id}>{label}{hint&&<small id={id+'-hint'}>{hint}</small>}</label></div>
}
export function Badge({tone='neutral',children}:{tone?:'neutral'|'success'|'warning'|'danger';children:React.ReactNode}){return <span className={'ui-badge ui-tone-'+tone}>{children}</span>}
export function Alert({title,children,tone='neutral'}:{title:string;children?:React.ReactNode;tone?:'neutral'|'success'|'warning'|'danger'}){return <div className={'ui-alert ui-tone-'+tone} role={tone==='danger'?'alert':'status'}><CircleAlert size={18} aria-hidden="true"/><div><strong>{title}</strong>{children&&<div>{children}</div>}</div></div>}
export function EmptyState({title,children,action}:{title:string;children?:React.ReactNode;action?:React.ReactNode}){return <div className="ui-empty"><Inbox size={28} strokeWidth={1.4} aria-hidden="true"/><h3>{title}</h3>{children&&<p>{children}</p>}{action}</div>}
export function Skeleton({label='Loading',lines=3}:{label?:string;lines?:number}){return <div className="ui-skeleton" role="status"><span className="ui-sr-only">{label}</span>{Array.from({length:Math.min(10,Math.max(1,lines))},(_,i)=><span key={i} aria-hidden="true"/>)}</div>}
export function Progress({value,max=100,label}:{value:number;max?:number;label:string}){const total=Number.isFinite(max)&&max>0?max:100,actual=Number.isFinite(value)?Math.min(total,Math.max(0,value)):0;return <div className="ui-progress"><div><span>{label}</span><span>{Math.round(actual/total*100)}%</span></div><progress aria-label={label} value={actual} max={total}/></div>}

// Adapted from the MIT shadcn/ui Radix composition; see SOURCES.json and licenses/.
export const Dialog = D.Root
export const DialogTrigger = D.Trigger
export const DialogClose = D.Close
export function DialogContent({title,description,closeLabel='Close',children,...props}:Omit<React.ComponentPropsWithoutRef<typeof D.Content>,'asChild'>&{title:string;description:string;closeLabel?:string}){return <D.Portal><D.Overlay className="ui-overlay"/><D.Content {...props} asChild={false} className={cx('ui-dialog',props.className)}><div className="ui-dialog-heading"><D.Title>{title}</D.Title><D.Description>{description}</D.Description></div>{children}<D.Close asChild><Button className="ui-dialog-close" variant="ghost" aria-label={closeLabel}><X size={18} aria-hidden="true"/></Button></D.Close></D.Content></D.Portal>}
export const Tabs = T.Root
export function TabsList(props:React.ComponentPropsWithoutRef<typeof T.List>){return <T.List {...props} className={cx('ui-tabs',props.className)}/>}
export function TabsTrigger(props:React.ComponentPropsWithoutRef<typeof T.Trigger>){return <T.Trigger {...props} className={cx('ui-tab',props.className)}/>}
export function TabsContent(props:React.ComponentPropsWithoutRef<typeof T.Content>){return <T.Content {...props} className={cx('ui-tab-panel',props.className)}/>}
export const DropdownMenu = M.Root
export const DropdownTrigger = M.Trigger
export function DropdownContent(props:React.ComponentPropsWithoutRef<typeof M.Content>){return <M.Portal><M.Content sideOffset={6} {...props} className={cx('ui-menu',props.className)}/></M.Portal>}
export function DropdownItem(props:React.ComponentPropsWithoutRef<typeof M.Item>){return <M.Item {...props} className={cx('ui-menu-item',props.className)}/>}
export function DropdownCheckboxItem({children,...props}:Omit<React.ComponentPropsWithoutRef<typeof M.CheckboxItem>,'asChild'>){return <M.CheckboxItem {...props} asChild={false} className={cx('ui-menu-item','ui-menu-choice',props.className)}><M.ItemIndicator className="ui-menu-check"><Check size={14}/></M.ItemIndicator>{children}</M.CheckboxItem>}
export function Tooltip({content,children}:{content:React.ReactNode;children:React.ReactElement}){return <H.Provider delayDuration={350}><H.Root><H.Trigger asChild>{children}</H.Trigger><H.Portal><H.Content className="ui-tooltip" sideOffset={6}>{content}<H.Arrow className="ui-tooltip-arrow"/></H.Content></H.Portal></H.Root></H.Provider>}
export const Accordion = A.Root
export const AccordionItem = A.Item
export function AccordionTrigger({children,...props}:Omit<React.ComponentPropsWithoutRef<typeof A.Trigger>,'asChild'>){return <A.Header className="ui-accordion-heading"><A.Trigger {...props} asChild={false} className={cx('ui-accordion-trigger',props.className)}>{children}<ChevronDown size={16} aria-hidden="true"/></A.Trigger></A.Header>}
export function AccordionContent(props:React.ComponentPropsWithoutRef<typeof A.Content>){return <A.Content {...props} className={cx('ui-accordion-content',props.className)}/>}

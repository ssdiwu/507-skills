import { Check, Field, Stage, States, Text, Window, type Act } from '../../kit'
import './form.css'

// A sign-up form catching a mistake. Beats: an email is typed without its
// ending; the field turns to error and the line under it says why; the
// ending is typed and the field turns valid; 创建工作区 sends, and the
// button settles on done. Plays once; the still is the payoff.
//
// What makes validation read:
// - The message has a lane of its own under the field from the start: the
//   hint and the error swap in it (States), so the form never grows or
//   shifts when the error arrives.
// - The error is said by the ring and the line together, in the danger ink,
//   and it leaves the moment the value is fixed: the ring turns calm with a
//   check, the line goes back to the hint.
// - Nothing in the button moves sideways. It is full width, so every state
//   fits where it is: the idle label and the busy group (check and label)
//   are two layers in one place that crossfade, and inside the group the
//   check holds still while "正在创建" crossfades to "Account
//   created" beside it. Re-centering a group as its width eases slides the
//   icon and the words across the button for no reason.
//
// Real strings: the title, the labels, the typed email, the hint and the
// error, the button.

type S = { email: string; field: 'email' | 'none'; status: 'none' | 'error' | 'valid'; sending: boolean; done: boolean }

const initial: S = { email: '', field: 'email', status: 'none', sending: false, done: false }
const poster: S = { email: 'maya@northwind.co', field: 'none', status: 'valid', sending: true, done: true }

async function script(a: Act<S>) {
  await a.wait(700)
  a.mark('type')
  await a.type('email', 'maya@northwind', { interval: 55 })
  await a.wait(300)
  a.mark('error')
  a.put({ status: 'error' })
  await a.wait(1400)
  a.mark('fix')
  // Only the ending is typed: a.type would clear the field and start over
  for (const end of ['maya@northwind.', 'maya@northwind.c', 'maya@northwind.co']) {
    a.put({ email: end })
    await a.wait(110)
  }
  a.put({ status: 'valid' })
  await a.wait(700)
  a.mark('send')
  await a.click({ at: 'create', x: 0.5, y: 0.5 })
  a.put({ field: 'none', sending: true })
  await a.wait(1200)
  a.put({ done: true })
  await a.move({ at: 'create', x: 0.75, y: 1.9 })
  await a.wait(2400)
}

export default function ReviewFlow() {
  return (
    <Stage width={560} height={400} compact={{ below: 560, width: 358, height: 420 }} initial={initial} poster={poster} script={script} play="once" cursor={{ at: { x: 520, y: 370 } }} className="rf">
      {(s) => (
        <Window url="workspace.example.invalid/new" className="rf-win">
          <div className="rf-card">
            <Text className="rf-title">创建项目工作区</Text>
            <div className="rf-group">
              <Field label="工作邮箱" value={s.email} focused={s.field === 'email'} status={s.status === 'none' ? undefined : s.status} />
              <div className="rf-lane" data-tone={s.status === 'error' ? 'error' : undefined}>
                <States
                  value={s.status === 'error' ? 'error' : 'hint'}
                  align="start"
                  states={{
                    hint: <Text className="rf-msg">发送确认链接，验证此邮箱</Text>,
                    error: <Text className="rf-msg rf-msg--error">请补全邮箱域名，例如 example.com</Text>,
                  }}
                />
              </div>
            </div>
            <div className="rf-group">
              <Field label="访问口令" value="northwind-2026" password />
              <div className="rf-lane" />
            </div>
            <span className="rf-button" data-target="create" data-cursor="pointer" data-done={s.done || undefined}>
              <span className="rf-layer rf-idle" data-on={!s.sending || undefined}>创建工作区</span>
              <span className="rf-layer rf-busy" data-on={s.sending || undefined}>
                <Check on={s.done} pending={s.sending && !s.done} size={14} />
                {/* Left-aligned in a cell as wide as the longer label: the
                    shorter sits 2px off center, which no eye sees */}
                <span className="rf-labels">
                  <span className="rf-label" data-on={!s.done || undefined}>正在创建</span>
                  <span className="rf-label" data-on={s.done || undefined}>创建完成</span>
                </span>
              </span>
            </span>
          </div>
        </Window>
      )}
    </Stage>
  )
}

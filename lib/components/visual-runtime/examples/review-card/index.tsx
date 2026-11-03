import { Bar, Stage, Text, Window, Row, Avatar } from '../../kit'
import './card.css'

// A feature card (400 × 300) with the product masked inside it: the window is
// pinned top-left, runs off the right and bottom, and a detail card straddles
// its left edge over the sidebar, about half outside. Real words only on the
// selected customer, its neighbors and the total; bars everywhere else.

// Three real rows (the selected one and its neighbors), bars only on the
// rows the crop takes
const ROWS: { selected?: boolean; name?: number | string; amount?: number | string }[] = [
  { name: '海风工程', amount: '$1,240' },
  { selected: true },
  { name: '山川设计', amount: '$860' },
  { name: 84, amount: 38 },
  { name: 64, amount: 48 },
  { name: 78, amount: 40 },
]
const NAV = ['概览', '项目', '清单', '报告']

export default function ReviewCard() {
  return (
    <Stage width={400} height={300} compact={{ below: 400, width: 358, height: 300 }} className="rc-card">
      {() => (
        <>
          <Window url="workspace.example.invalid" className="rc-window">
            {/* The sidebar is what the detail card covers, so the rows stay readable */}
            <aside className="rc-sidebar">
              <Bar w={20} h={20} r={6} tone={4} style={{ marginBottom: 10 }} />
              {NAV.map((label, i) => (
                // The active item is marked by weight, not a pill: a pill would peek out beside the detail card
                <div key={i} className="rc-nav" data-on={i === 1 || undefined}>
                  <Bar w={10} h={10} r={3} tone={i === 1 ? 4 : 3} />
                  <Text className="rc-nav__label">{label}</Text>
                </div>
              ))}
            </aside>
            <div className="rc-main">
              <div className="rc-header">
                <Text className="rc-title">项目</Text>
                <Bar w={52} h={22} r={6} tone={2} />
              </div>
              <div className="rc-list">
                {ROWS.map((row, i) =>
                  row.selected ? (
                    <Row key={i} pad={0} selected className="rc-row" data-target="selected" lead={<Avatar name="南山项目组" tone="accent" size={18} />} title={<Text className="rc-name">南山项目组</Text>}>
                      <Bar w={40} tone={4} />
                    </Row>
                  ) : (
                    <Row key={i} pad={0} className="rc-row" lead={<Bar w={18} h={18} r={9} tone={2} />} title={typeof row.name === 'string' ? <Text className="rc-rowname">{row.name}</Text> : <Bar w={row.name!} tone={3} />}>
                      {typeof row.amount === 'string' ? <Text className="rc-rowamount">{row.amount}</Text> : <Bar w={row.amount!} tone={2} />}
                    </Row>
                  ),
                )}
              </div>
            </div>
          </Window>

          <div className="rc-detail">
            <div className="rc-detail-head">
              <Avatar name="南山项目组" tone="accent" size={26} className="rc-avatar-large" />
              <div className="rc-detail-who">
                <Text className="rc-detail-name">南山项目组</Text>
                <Bar w={64} h={5} tone={2} />
              </div>
            </div>
            {[48, 36].map((w, i) => (
              <div key={i} className="rc-detail-row">
                <Bar w={w} h={5} tone={3} />
                <Bar w={w - 12} h={5} tone={2} />
              </div>
            ))}
            <div className="rc-detail-row total">
              <Text className="rc-detail-label">合计</Text>
              <Text className="rc-detail-total">$72.00</Text>
            </div>
          </div>
        </>
      )}
    </Stage>
  )
}

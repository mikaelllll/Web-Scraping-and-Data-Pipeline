import type { LucideIcon } from 'lucide-react'

type Props = { label: string; value: string | number; detail: string; icon: LucideIcon; tone?: 'cyan' | 'violet' | 'amber' }

export function MetricCard({ label, value, detail, icon: Icon, tone = 'cyan' }: Props) {
  return <article className={`metric-card ${tone}`}><div className="metric-icon"><Icon size={19} /></div><div><p>{label}</p><strong>{value}</strong><span>{detail}</span></div></article>
}


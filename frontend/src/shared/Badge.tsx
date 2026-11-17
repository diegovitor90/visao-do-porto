import type { ReactNode } from 'react'

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: 'neutral' | 'critical' | 'attention' | 'clear' | 'cyan' }) {
  return <span className={'badge badge-' + tone}><i aria-hidden="true" />{children}</span>
}

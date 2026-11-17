export type Severity = 'critical' | 'attention'
export type Decision = 'confirmed' | 'discarded' | 'insufficient'
export type Review = { decision: Decision; note: string; reviewedAt: string }
export type Reviews = Record<string, Review>
export type Alert = {
  id: string; title: string; type: string; severity: Severity;
  zone: string; camera: string; time: string; rule: string; reason: string;
}
export type Zone = { id: string; name: string; subtitle: string; grid: string }

export const alerts: Alert[] = [
  { id: 'EVT-024', title: 'Entrada em área restrita', type: 'Acesso à zona', severity: 'critical', zone: 'z2', camera: 'LAB-01', time: '14:32', rule: 'Z02 · Entrada em área restrita', reason: 'Nesta simulação, o ponto de apoio da pessoa cruza a zona de equipamentos. A imagem ilustrativa não comprova uma ocorrência real.' },
  { id: 'EVT-023', title: 'Capacete não detectado', type: 'Equipamento de proteção', severity: 'attention', zone: 'z3', camera: 'LAB-01', time: '14:18', rule: 'Z03 · Capacete obrigatório', reason: 'Exemplo de alerta em que o modelo não detecta capacete na área esperada. Uma não detecção não prova ausência de EPI.' },
  { id: 'EVT-022', title: 'Evidência com baixa visibilidade', type: 'Qualidade da evidência', severity: 'attention', zone: 'z1', camera: 'LAB-01', time: '13:56', rule: 'Z01 · Evidência inconclusiva', reason: 'Exemplo de alerta para um quadro com visibilidade insuficiente. O operador pode registrar essa limitação sem confirmar uma infração.' },
]
export const zones: Zone[] = [
  { id: 'z1', name: 'Entrada', subtitle: 'Área de passagem', grid: 'entry' },
  { id: 'z2', name: 'Equipamentos', subtitle: 'Acesso restrito', grid: 'equipment' },
  { id: 'z3', name: 'Bancada de testes', subtitle: 'EPI obrigatório', grid: 'bench' },
  { id: 'z4', name: 'Circulação', subtitle: 'Área de passagem', grid: 'aisle' },
]
export const severityLabels: Record<Severity, string> = { critical: 'Crítico', attention: 'Atenção' }
export const decisionLabels: Record<Decision, string> = { confirmed: 'Confirmado', discarded: 'Descartado', insufficient: 'Evidência insuficiente' }
export const dateLabel = '15 nov 2026'
export const zoneName = (id: string) => zones.find(z => z.id === id)?.name ?? id
export const reviewKey = 'visao-do-porto.reviews.v1'

export function readReviews(): Reviews {
  try {
    const raw: unknown = JSON.parse(localStorage.getItem(reviewKey) ?? '{}')
    if (!raw || typeof raw !== 'object') return {}
    const safe: Reviews = {}
    for (const a of alerts) {
      const row = (raw as Record<string, unknown>)[a.id]
      if (!row || typeof row !== 'object') continue
      const item = row as Partial<Review>
      if (item.decision && Object.hasOwn(decisionLabels, item.decision) && typeof item.note === 'string' && typeof item.reviewedAt === 'string') {
        safe[a.id] = { decision: item.decision, note: item.note, reviewedAt: item.reviewedAt }
      }
    }
    return safe
  } catch { return {} }
}

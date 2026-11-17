import { useEffect, useState } from 'react'
import { Activity, ChevronRight, History, LayoutDashboard, Map, ScanLine, ShieldAlert } from 'lucide-react'
import { AnalysisPage } from '../features/analysis/AnalysisPage'
import { AlertsPage, Dashboard, HistoryPage, ReviewDialog, ZonesPage } from '../features/operations/Operations'
import { readReviews, reviewKey, type Alert, type Review } from '../features/operations/model'

const pages = [
  { id: 'painel', label: 'Visão geral', Icon: LayoutDashboard },
  { id: 'analisar', label: 'Analisar imagem', Icon: ScanLine },
  { id: 'alertas', label: 'Alertas', Icon: ShieldAlert },
  { id: 'zonas', label: 'Zonas', Icon: Map },
  { id: 'historico', label: 'Histórico', Icon: History },
] as const
const readRoute = () => {
  const [path, query] = location.hash.slice(1).split('?')
  return { page: pages.find(p => p.id === path) ?? pages[0], zone: new URLSearchParams(query).get('zona') ?? '' }
}
const goTo = (id: string) => { location.hash = id }
const goToZone = (id: string) => { goTo('alertas?zona=' + encodeURIComponent(id)) }

export function App() {
  const [{ page, zone }, setRoute] = useState(readRoute)
  const [reviews, setReviews] = useState(readReviews)
  const [active, setActive] = useState<Alert | null>(null)
  const [feedback, setFeedback] = useState('')
  useEffect(() => {
    const handler = () => { setRoute(readRoute()); setActive(null); setFeedback(''); window.scrollTo(0, 0); requestAnimationFrame(() => document.getElementById('main-content')?.focus()) }
    window.addEventListener('hashchange', handler)
    return () => window.removeEventListener('hashchange', handler)
  }, [])

  function save(id: string, review: Review) {
    const next = { ...reviews, [id]: review }
    setReviews(next)
    try { localStorage.setItem(reviewKey, JSON.stringify(next)); setFeedback('Revisão registrada neste navegador.') }
    catch { setFeedback('Revisão registrada apenas nesta sessão. Não foi possível salvar no navegador.') }
  }

  return <div className="shell">
    <a className="skip" href="#main-content" onClick={e => { e.preventDefault(); document.getElementById('main-content')?.focus() }}>Pular para o conteúdo</a>
    <aside className="sidebar">
      <a className="brand" href="#painel"><img src={import.meta.env.BASE_URL + 'porto.svg'} alt="" /><span><strong>Visão do Porto</strong><small>Central de operações</small></span></a>
      <p className="nav-label">OPERAÇÃO</p>
      <nav aria-label="Navegação principal">{pages.map(({ id, label, Icon }) => <a href={'#' + id} key={id} aria-current={page.id === id ? 'page' : undefined}><Icon size={18} /><span>{label}</span>{page.id === id && <ChevronRight className="nav-arrow" size={15} />}</a>)}</nav>
      <div className="sidebar-bottom"><div className="sandbox-mark"><span className="site-indicator" aria-hidden="true" /><span><strong>Laboratório UNDB</strong><small>Piloto acadêmico</small></span></div></div>
    </aside>
    <div className="workspace">
      <header className="topbar"><div className="breadcrumb"><span>Operação</span><ChevronRight size={14} /><strong>{page.label}</strong></div><span className="environment-label"><i aria-hidden="true" /> Ambiente de demonstração</span></header>
      <main className="content" tabIndex={-1} id="main-content">
        {page.id === 'painel' && <Dashboard reviews={reviews} onOpen={setActive} onZone={goToZone} onNavigate={goTo} />}
        {page.id === 'analisar' && <AnalysisPage />}
        {page.id === 'alertas' && <AlertsPage key={zone} zone={zone} reviews={reviews} onOpen={setActive} />}
        {page.id === 'zonas' && <ZonesPage onZone={goToZone} reviews={reviews} />}
        {page.id === 'historico' && <HistoryPage reviews={reviews} onOpen={setActive} />}
        <div className="footer"><Activity size={14} /> Visão do Porto <span>·</span> Piloto de segurança assistida</div>
      </main>
    </div>
    {active && <ReviewDialog key={active.id} alert={active} review={reviews[active.id]} onClose={() => setActive(null)} onSave={save} />}
    <div className={feedback ? 'toast' : 'sr-only'} aria-live="polite">{feedback}</div>
  </div>
}

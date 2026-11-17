import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { CircleAlert, ScanLine, UploadCloud, Image as ImageIcon, FlaskConical, LoaderCircle } from 'lucide-react'
import { Badge } from '../../shared/Badge'
import { analyzeImage, classLabel, percent, validateUpload, type Analysis } from './api'
import { Evidence, labImage, sampleDetections } from './Evidence'

export function AnalysisPage() {
  const [file, setFile] = useState<File | null>(null)
  const [src, setSrc] = useState('')
  const [demo, setDemo] = useState(false)
  const [result, setResult] = useState<Analysis | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const controller = useRef<AbortController | null>(null)

  useEffect(() => {
    if (!file) { setSrc(''); return }
    const url = URL.createObjectURL(file)
    setSrc(url)
    return () => URL.revokeObjectURL(url)
  }, [file])
  useEffect(() => () => { controller.current?.abort() }, [])

  function choose(e: ChangeEvent<HTMLInputElement>) {
    const next = e.target.files?.[0]
    if (!next) return
    const invalid = validateUpload(next)
    setError(invalid ?? '')
    setResult(null)
    setDemo(false)
    setFile(invalid ? null : next)
    e.target.value = ''
  }

  async function submit(e: FormEvent) {
    e.preventDefault()
    if (!file || busy) return
    setBusy(true); setError(''); setResult(null)
    const ctrl = new AbortController()
    controller.current = ctrl
    const timer = window.setTimeout(() => ctrl.abort(), 30_000)
    try { setResult(await analyzeImage(file, ctrl.signal)) }
    catch (e) { setError(e instanceof Error ? e.message : 'Falha ao analisar imagem.') }
    finally { window.clearTimeout(timer); controller.current = null; setBusy(false) }
  }

  const detections = demo ? sampleDetections : result?.detections ?? []
  return <>
    <header className="page-intro">
      <div className="eyebrow"><ScanLine size={16} /> VISÃO COMPUTACIONAL</div>
      <h1>Analisar imagem</h1>
      <p>Envie uma imagem para a Vision API ou veja como as detecções são exibidas em uma cena de exemplo.</p>
    </header>
    <div className="analysis-grid">
      <section className="panel upload-panel">
        <h2>Arquivo de entrada</h2>
        <p>PNG ou JPEG, até 5 MB. A análise envia a imagem à Vision API configurada.</p>
        <form onSubmit={submit}>
          <label className="drop-area">
            <UploadCloud size={27} aria-hidden="true" />
            <strong>{file?.name ?? 'Selecionar imagem'}</strong>
            <span>{file ? 'Clique para trocar o arquivo' : 'JPEG ou PNG · até 5 MB'}</span>
            <input type="file" accept="image/png,image/jpeg" onChange={choose} disabled={busy} aria-label="Selecionar imagem" />
          </label>
          <button className="button primary" disabled={!file || busy} type="submit">
            {busy ? <LoaderCircle className="spin" size={17} /> : <ScanLine size={17} />}{busy ? 'Analisando…' : 'Enviar para análise'}
          </button>
          <button type="button" className="button secondary" disabled={busy} onClick={() => { setDemo(true); setFile(null); setResult(null); setError('') }}><FlaskConical size={17} /> Usar exemplo</button>
        </form>
        {!!error && <div className="notice danger" role="alert"><CircleAlert size={18} />{error}</div>}
      </section>
      <section className="panel result-panel">
        <div className="panel-head"><div><h2>Resultado visual</h2><p>Imagem e caixas de detecção nas coordenadas da origem.</p></div>{demo && <Badge tone="cyan">Exemplo simulado</Badge>}</div>
        <div className="result-body" aria-busy={busy}>
          {demo ? <Evidence src={labImage} width={960} height={540} detections={detections} alt="Cena ilustrativa de laboratório com uma pessoa" />
            : result && src ? <Evidence src={src} width={result.width} height={result.height} detections={detections} alt="Imagem analisada" />
              : src ? <img className="image-preview" src={src} alt="Prévia da imagem selecionada" />
                : <div className="image-empty"><ImageIcon size={33} /><span>A imagem aparecerá aqui</span></div>}
          <div className="result-status" aria-live="polite">
            {busy ? 'Aguardando resposta da Vision API…'
              : demo ? 'Detecções fictícias. Nenhuma inferência foi executada.'
                : result ? !result.inference_performed ? 'Imagem validada. A API ainda não executou inferência.'
                  : detections.length === 0 ? 'Análise concluída. Nenhuma pessoa detectada.' : `Análise concluída. ${detections.length} ${detections.length === 1 ? 'detecção' : 'detecções'}.`
                  : file ? 'Imagem selecionada. Aguardando envio.' : 'Selecione um arquivo ou abra o exemplo.'}
          </div>
          {detections.length > 0 && <ol className="detection-list" aria-label="Detecções">
            {detections.map((d, i) => <li key={i}><span>#{i + 1} · {classLabel(d.class_name)}</span><strong>{percent(d.confidence)}</strong></li>)}
          </ol>}
        </div>
      </section>
    </div>
  </>
}

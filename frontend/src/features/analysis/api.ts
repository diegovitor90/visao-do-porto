export type Bbox = { x1: number; y1: number; x2: number; y2: number }
export type Detection = { class_id: number; class_name: string; confidence: number; bbox: Bbox }
export type Analysis = { filename: string; width: number; height: number; status: string; inference_performed: boolean; detections: Detection[]; message: string }
type Obj = Record<string, unknown>
const isObj = (v: unknown): v is Obj => !!v && typeof v === 'object' && !Array.isArray(v)
const isNum = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v)
const positive = (v: unknown): v is number => isNum(v) && Number.isInteger(v) && v > 0
export const maxFileBytes = 5 * 1024 * 1024

export function validateUpload(file: File) {
  if (!['image/jpeg', 'image/png'].includes(file.type)) return 'Formato não suportado. Escolha uma imagem JPEG ou PNG.'
  if (file.size === 0) return 'O arquivo está vazio.'
  if (file.size > maxFileBytes) return 'A imagem excede o limite de 5 MB.'
  return null
}

export function parseAnalysis(data: unknown): Analysis {
  const invalid = () => new Error('Resposta inesperada da Vision API. Confira o contrato do endpoint /analyze.')
  if (!isObj(data) || typeof data.filename !== 'string' || !positive(data.width) || !positive(data.height)
    || typeof data.status !== 'string' || typeof data.inference_performed !== 'boolean'
    || typeof data.message !== 'string' || !Array.isArray(data.detections)) throw invalid()
  if (!data.inference_performed && data.detections.length > 0) throw invalid()
  const width = data.width, height = data.height
  const detections = data.detections.map((d: unknown): Detection => {
    if (!isObj(d) || !isNum(d.class_id) || typeof d.class_name !== 'string' || !isNum(d.confidence)
      || d.confidence < 0 || d.confidence > 1 || !isObj(d.bbox)) throw invalid()
    const { x1, y1, x2, y2 } = d.bbox
    if (!isNum(x1) || !isNum(y1) || !isNum(x2) || !isNum(y2)
      || x1 < 0 || y1 < 0 || x1 >= x2 || y1 >= y2 || x2 > width || y2 > height) throw invalid()
    return { class_id: d.class_id, class_name: d.class_name, confidence: d.confidence, bbox: { x1, y1, x2, y2 } }
  })
  return { filename: data.filename, width, height, status: data.status, inference_performed: data.inference_performed, message: data.message, detections }
}

export async function analyzeImage(file: File, signal: AbortSignal): Promise<Analysis> {
  const form = new FormData()
  form.set('file', file)
  const timeoutMessage = 'A análise não respondeu a tempo.'
  let response: Response
  try {
    response = await fetch('/api/v1/vision/analyze', { method: 'POST', body: form, signal })
  } catch {
    if (signal.aborted) throw new Error(timeoutMessage)
    throw new Error('Não foi possível conectar à Vision API. Confira se o FastAPI está rodando.')
  }
  const data: unknown = await response.json().catch(() => {
    if (signal.aborted) throw new Error(timeoutMessage)
    return null
  })
  if (!response.ok) {
    if (isObj(data) && typeof data.detail === 'string') throw new Error(data.detail)
    if (response.status >= 500) throw new Error('A Vision API está indisponível ou falhou durante a análise. Tente novamente.')
    throw new Error('A Vision API não aceitou a solicitação (HTTP ' + response.status + ').')
  }
  return parseAnalysis(data)
}

export const percent = (n: number) => new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 2 }).format(n)
export const classLabel = (name: string) => ({ person: 'Pessoa', helmet: 'Capacete', safety_vest: 'Colete' }[name] ?? name)

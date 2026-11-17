import { classLabel, percent, type Detection } from './api'

export const labImage = import.meta.env.BASE_URL + 'laboratorio.svg'
export const sampleDetections: Detection[] = [{ class_id: 0, class_name: 'person', confidence: .92, bbox: { x1: 443, y1: 224, x2: 577, y2: 447 } }]

export function Evidence({ src, width, height, detections = [], alt, zone = false }: {
  src: string; width: number; height: number; detections?: Detection[]; alt: string; zone?: boolean
}) {
  return <div className="evidence" style={{ aspectRatio: width + ' / ' + height }}>
    <img src={src} alt={alt} draggable={false} />
    <svg viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      {zone && <polygon points="364,368 591,368 654,527 260,527" className="scene-zone" vectorEffect="non-scaling-stroke" />}
      {detections.map(({ bbox: b, class_name, confidence }, i) => {
        const label = classLabel(class_name) + ' ' + percent(confidence)
        const font = Math.max(10, width / 62)
        const top = Math.max(0, b.y1 - font * 1.45)
        const labelWidth = Math.min(width, (label.length * .65 + 1.1) * font)
        const labelLeft = Math.max(0, Math.min(b.x1, width - labelWidth))
        return <g key={i}>
          <rect x={b.x1} y={b.y1} width={b.x2 - b.x1} height={b.y2 - b.y1} className="detect-box" vectorEffect="non-scaling-stroke" />
          <rect x={labelLeft} y={top} width={labelWidth} height={font * 1.45} rx={font * .18} className="detect-label" />
          <text x={labelLeft + font * .45} y={top + font * 1.04} fontSize={font} className="detect-text">{label}</text>
        </g>
      })}
    </svg>
  </div>
}

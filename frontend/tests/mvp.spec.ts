import { expect, test, type Page } from '@playwright/test'
import { analyzeImage, parseAnalysis } from '../src/features/analysis/api'
import { resolve } from 'node:path'

const endpoint = '**/api/v1/vision/analyze'
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aTKUAAAAASUVORK5CYII=', 'base64')
const input = async (page: Page) => {
  await page.goto('/#analisar')
  await page.getByLabel('Selecionar imagem').setInputFiles({ name: 'quadro.png', mimeType: 'image/png', buffer: png })
}
const validated = { filename: 'quadro.png', width: 1, height: 1, status: 'VALIDATED', inference_performed: false, detections: [], message: 'Imagem validada.' }
const hit = { ...validated, status: 'ANALYZED', inference_performed: true, detections: [{ class_id: 0, class_name: 'person', confidence: .8246, bbox: { x1: .1, y1: .1, x2: .8, y2: .8 } }] }

test('mapa abre a fila já filtrada, sem rota morta', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Visão geral' })).toBeVisible()
  await page.getByRole('button', { name: /^Z02 Equipamentos/i }).click()
  await expect(page.getByLabel('Zona', { exact: true })).toHaveValue('z2')
  await expect(page.getByRole('button', { name: /entrada em área restrita/i })).toBeVisible()
  await expect(page.getByRole('button', { name: /capacete não detectado/i })).toHaveCount(0)
  await page.getByLabel('Gravidade').selectOption('attention')
  await expect(page.getByText('Nenhum alerta encontrado')).toBeVisible()
})

test('revisão exige justificativa e permanece no histórico após recarregar', async ({ page }) => {
  await page.goto('/#alertas')
  await page.getByRole('button', { name: /entrada em área restrita/i }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await dialog.getByRole('button', { name: 'Confirmar', exact: true }).click()
  await expect(dialog.getByRole('alert')).toContainText('justificativa')
  await dialog.getByLabel('Justificativa da revisão').fill('A imagem é ilustrativa e não confirma ocorrência.')
  await dialog.getByRole('button', { name: 'Evidência insuficiente', exact: true }).click()
  await expect(dialog).not.toBeVisible()
  await expect(page.getByRole('button', { name: /entrada em área restrita/i })).toHaveCount(0)
  await page.getByRole('link', { name: 'Visão geral' }).click()
  await expect(page.getByRole('button', { name: /^Z02 Equipamentos.*Sem pendência/i })).toBeVisible()
  await page.getByRole('link', { name: 'Histórico' }).click()
  await page.reload()
  await page.getByRole('button', { name: /entrada em área restrita/i }).click()
  await expect(dialog.getByText('Evidência insuficiente', { exact: true })).toBeVisible()
  await expect(dialog.getByText('A imagem é ilustrativa e não confirma ocorrência.')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(dialog).not.toBeVisible()
})

test('exemplo não faz POST e é explicitamente simulado', async ({ page }) => {
  let posts = 0
  await page.route(endpoint, async route => { posts++; await route.abort() })
  await page.goto('/#analisar')
  await page.getByRole('button', { name: 'Usar exemplo' }).click()
  await expect(page.getByText('Detecções fictícias. Nenhuma inferência foi executada.')).toBeVisible()
  await expect(page.getByRole('list', { name: 'Detecções' })).toContainText('92%')
  expect(posts).toBe(0)
})

test('FastAPI 0.2 por contrato: envia multipart e exibe validação sem inferência', async ({ page }) => {
  await page.route(endpoint, async route => {
    expect(route.request().method()).toBe('POST')
    expect(route.request().headers()['content-type']).toContain('multipart/form-data; boundary=')
    expect(route.request().postData()).toContain('name="file"')
    await route.fulfill({ json: validated })
  })
  await input(page)
  await page.getByRole('button', { name: 'Enviar para análise' }).click()
  await expect(page.getByText('Imagem validada. A API ainda não executou inferência.')).toBeVisible()
  await expect(page.getByRole('list', { name: 'Detecções' })).toHaveCount(0)
})

test('contrato de inferência: desenha caixa SVG e mostra a confiança', async ({ page }) => {
  await page.route(endpoint, route => route.fulfill({ json: hit }))
  await input(page)
  await page.getByRole('button', { name: 'Enviar para análise' }).click()
  await expect(page.getByText('Análise concluída. 1 detecção.')).toBeVisible()
  await expect(page.locator('.detect-box')).toHaveAttribute('x', '0.1')
  await expect(page.getByRole('list', { name: 'Detecções' })).toContainText('82,46%')
})

test('zero detecções não é tratado como falha', async ({ page }) => {
  await page.route(endpoint, route => route.fulfill({ json: { ...hit, detections: [] } }))
  await input(page)
  await page.getByRole('button', { name: 'Enviar para análise' }).click()
  await expect(page.getByText('Análise concluída. Nenhuma pessoa detectada.')).toBeVisible()
})

test('falhas HTTP e arquivos inválidos ficam visíveis ao usuário', async ({ page }) => {
  await page.route(endpoint, route => route.fulfill({ status: 422, json: { detail: 'Arquivo de imagem inválido ou corrompido.' } }))
  await input(page)
  await page.getByRole('button', { name: 'Enviar para análise' }).click()
  await expect(page.getByRole('alert')).toContainText('corrompido')
  await page.getByLabel('Selecionar imagem').setInputFiles({ name: 'arquivo.txt', mimeType: 'text/plain', buffer: Buffer.from('x') })
  await expect(page.getByRole('alert')).toContainText('Formato não suportado')
  await expect(page.getByRole('button', { name: 'Enviar para análise' })).toBeDisabled()
})

test('resposta inválida não é interpretada como detecção', () => {
  expect(() => parseAnalysis({ ...hit, width: 0 })).toThrow('Resposta inesperada')
  expect(() => parseAnalysis({ ...validated, detections: hit.detections })).toThrow('Resposta inesperada')
  expect(() => parseAnalysis({ ...hit, detections: [{ ...hit.detections[0], bbox: { ...hit.detections[0].bbox, x2: 4 } }] })).toThrow('Resposta inesperada')
})

test('timeout ao ler o corpo da resposta é exibido como timeout', async () => {
  const controller = new AbortController()
  const originalFetch = globalThis.fetch
  globalThis.fetch = async () => new Response(new ReadableStream({
    start(body) {
      controller.signal.addEventListener('abort', () => body.error(controller.signal.reason), { once: true })
    },
    pull() {
      controller.abort()
    },
  }, { highWaterMark: 0 }), { headers: { 'Content-Type': 'application/json' } })
  try {
    await expect(analyzeImage(new File([png], 'quadro.png', { type: 'image/png' }), controller.signal))
      .rejects.toThrow('A análise não respondeu a tempo.')
  } finally {
    globalThis.fetch = originalFetch
  }
})

test('painel funciona em 390 px sem rolagem horizontal', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Visão geral' })).toBeVisible()
  expect(await page.locator('body').evaluate(el => el.scrollWidth)).toBeLessThanOrEqual(390)
  await page.getByRole('button', { name: /entrada em área restrita/i }).click()
  await expect(page.getByRole('button', { name: 'Fechar detalhes' })).toBeVisible()
})

test('envia um PNG real para a FastAPI quando o teste de integração é habilitado', async ({ page }) => {
  const imagePath = process.env.VISION_API_SMOKE_IMAGE
  test.skip(!imagePath, 'Requer FastAPI v0.3.0, pesos locais e VISION_API_SMOKE_IMAGE')
  if (!imagePath) return
  test.setTimeout(60_000)

  await page.goto('/#analisar')
  await page.getByLabel('Selecionar imagem').setInputFiles(resolve(imagePath))
  const [response] = await Promise.all([
    page.waitForResponse(
      response => new URL(response.url()).pathname === '/api/v1/vision/analyze'
        && response.request().method() === 'POST',
      { timeout: 45_000 },
    ),
    page.getByRole('button', { name: 'Enviar para análise' }).click(),
  ])

  expect(response.status()).toBe(200)
  const payload = await response.json()
  expect(payload).toMatchObject({ status: 'COMPLETED', inference_performed: true, model: 'yolo11n' })
  const result = parseAnalysis(payload)
  const count = result.detections.length
  const summary = count === 0
    ? 'Análise concluída. Nenhuma pessoa detectada.'
    : `Análise concluída. ${count} ${count === 1 ? 'detecção' : 'detecções'}.`
  await expect(page.getByText(summary, { exact: true })).toBeVisible()
  await expect(page.locator('.detect-box')).toHaveCount(count)
})

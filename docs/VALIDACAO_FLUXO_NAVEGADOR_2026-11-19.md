# Validação do fluxo real no navegador — frontend + Vite + FastAPI + YOLO11

Data: 19/11/2026, America/Sao_Paulo. Executada com apoio do Claude Code, no PC de Diego.

## Objetivo

Comprovar o caminho **upload pela tela Analisar imagem → proxy do Vite → FastAPI v0.3.0 →
YOLO11n → caixas no navegador**, sem resposta simulada e sem o botão **Usar exemplo**.
Até então, a inferência real só tinha sido comprovada por POST direto
([validação de 17/11](../backend/fastapi/VALIDACAO_INFERENCIA_REAL_2026-11-17.md)).

## Base e ambiente

- Código: `main` em `65c5f23`. Alterações locais existentes eram só de documentação.
  **Nenhuma linha de código foi alterada** nesta validação.
- Frontend `frontend/` v0.1.1, idêntico ao ZIP entregue (só o `README.md` difere).
- Windows 11; Node 22.17.1; Python 3.11.9 (`.venv`); fastapi 0.162.5; ultralytics 8.4.212;
  @playwright/test 1.65.1.
- FastAPI em `127.0.0.1:8000` (OpenAPI confirmou versão 0.3.0); Vite em `127.0.0.1:5173`,
  com proxy padrão `/api/v1/vision` → `http://127.0.0.1:8000`.
- Navegador: painel de navegador do aplicativo Claude (Chromium).

## Imagens de teste

| Arquivo | Descrição | Versionado? |
|---|---|---|
| `teste_pessoas.png` | 767 × 766, uma pessoa (mesmo arquivo de 17/11) | Não: foto de pessoa real, fora do Git por privacidade |
| `sem_pessoas.png` | 640 × 480, cena sintética sem pessoas, gerada com PIL | Não: temporária |
| `corrompida.png` | Cabeçalho PNG válido seguido de bytes inválidos | Não: temporária |

## 1. POST direto na FastAPI (sem frontend)

| Caso | HTTP | Resultado |
|---|---|---|
| Com pessoa | 200 | `inference_performed: true`, 1 `person`, confiança 0,8246, bbox (37,02; 34,14)–(731,36; 751,73), 4,33 s (primeira chamada, inclui carga dos pesos) |
| Sem pessoa | 200 | `inference_performed: true`, `detections: []`, 0,13 s |
| Corrompida | 422 | `"Arquivo de imagem inválido ou corrompido."` |

## 2. Fluxo pelo navegador

Método: a imagem foi colocada no campo de arquivo real da tela (`input[type=file]`) por
script, disparando o evento `change` do componente, e em seguida foi clicado o botão
**Enviar para análise**. Assim, o envio passa pelo mesmo código de produção
(`AnalysisPage.tsx` → `api.ts` → `fetch('/api/v1/vision/analyze')`). Para carregar os bytes
no navegador, as imagens foram servidas por um servidor HTTP local temporário.

| Caso | Requisição observada na aba Rede | O que a tela mostrou |
|---|---|---|
| Com pessoa | `POST /api/v1/vision/analyze` → 200 | Caixa "Pessoa 82,46%" e "Análise concluída. 1 detecção." |
| Sem pessoa | → 200 | "Análise concluída. Nenhuma pessoa detectada.", sem caixa |
| Corrompida | → 422 | "Arquivo de imagem inválido ou corrompido.", sem caixa e sem "concluída" |
| FastAPI desligada | → 500 (gerado pelo proxy do Vite) | "A Vision API está indisponível ou falhou durante a análise. Tente novamente.", sem caixa e sem "concluída" |

**Posição da caixa:** comparada a posição real do retângulo SVG com a posição esperada,
calculada a partir da bbox e do tamanho exibido da imagem (`viewBox="0 0 767 766"`).

| Largura exibida da imagem | Esperado (esquerda, topo, largura) | Medido |
|---|---|---|
| 474 px (desktop) | 519, 292, 429 | 519, 292, 429 |
| 314 px (viewport 375 × 812) | 46, 781, 284 | 46, 781, 284 |

## 3. Testes automatizados

| Suíte | Resultado |
|---|---|
| Python (`pytest`, `backend/fastapi`) | 17 passed, 1 warning (StarletteDeprecationWarning já conhecido) |
| Build do frontend (`tsc --noEmit && vite build`) | Aprovado |
| Playwright (`frontend/tests/mvp.spec.ts`) | 9 passed, 1 skipped (o teste opcional de upload real) |

O Chromium próprio do Playwright não está instalado neste PC; a primeira execução falhou
por isso, sem chegar a rodar os testes. A execução válida usou o Edge instalado, pela
variável já prevista em `playwright.config.ts`:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"; npm --prefix .\frontend test
```

Os testes Playwright usam respostas simuladas da API. **Não são evidência do YOLO**;
a evidência do YOLO é a seção 2.

## Como reproduzir manualmente

Em dois terminais, a partir da raiz do repositório:

```powershell
cd .\backend\fastapi; .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

```powershell
npm --prefix .\frontend run dev
```

Abrir `http://127.0.0.1:5173/#analisar`, escolher uma imagem pelo campo de arquivo e clicar
em **Enviar para análise**. Conferir o `POST` na aba Rede do navegador.

## Conclusão e limites

Critério de aceite do handoff de 19/11 atendido: um upload real produz a caixa retornada pelo
YOLO11, uma imagem sem pessoas produz resultado vazio válido e uma falha de API aparece como
falha.

Limites: três imagens, CPU local, uma execução por caso. Não comprova precisão, recall,
desempenho em vídeo nem uso operacional. Uma confiança de 82% não é acurácia do modelo.
O fluxo validado é o proxy de desenvolvimento do Vite; não passa pelo Spring Boot (ADR-001:
o Java fica fora do fluxo de vídeo). Pela decisão A da arquitetura v2, o detector de EPI do
MVP será o `epi_ppe` da Sophia; esta FastAPI continua responsável pela tela Analisar imagem.

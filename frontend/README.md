# Visão do Porto · Frontend 0.1.1

Estado revisado em 17/11/2026. Interface React/Vite do piloto acadêmico, preservada
na consolidação para a `main`. O painel, a planta, os alertas e a revisão são
demonstrativos; as revisões persistem somente no navegador atual.

## Executar no Windows

Requer Node.js 20.19+ na série 20 ou 22.12+. Ambiente verificado: Node 22.17.1 e
npm 10.9.2. Na pasta `frontend`, com dependências disponíveis:

```powershell
npm run build
npm run dev
```

Em ambiente novo, executar `npm ci` com autorização de download; o lockfile é
versionado, `node_modules` não. Abrir `http://127.0.0.1:5173`.

## Conexão atual com a FastAPI v0.3.0

Em outro terminal, a partir da raiz do repositório:

```powershell
cd backend/fastapi
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

O ambiente Python e os pesos devem estar preparados conforme o [README principal](../README.md).
O Vite encaminha `/api/v1/vision/*` diretamente para `http://127.0.0.1:8000`.
Para outro destino, copiar `.env.example` para `.env.local`, ajustar
`VISION_API_TARGET` e reiniciar o Vite. O upload é multipart, campo `file`.
Esse proxy de desenvolvimento não é incluído no build de produção.

A API v0.3.0 valida JPEG/PNG e executa YOLO11n para pessoas. Retorna
`status=COMPLETED`, `inference_performed=true`, `model=yolo11n`, dimensões e
detecções com `bbox={x1,y1,x2,y2}`. O frontend distingue zero detecções de falha,
renderiza caixas e confiança e também suporta respostas antigas sem inferência.
O tipo/parser atual não preserva `model` e não restringe `status`; esse alinhamento
fica pendente. O [contrato único](../docs/contrato-ia-backend.md) registra os campos reais.

O frontend ainda não passa pelo Spring Boot. A integração-alvo é frontend → Spring
Boot → FastAPI → YOLO11n → Spring Boot → frontend e ainda será implementada.

## Exemplo, revisão e estrutura

“Usar exemplo” mostra uma ilustração e detecção fictícia sem POST. Para revisar um
alerta demonstrativo, abrir seu painel, informar justificativa e selecionar decisão;
o histórico pode ser reaberto no mesmo navegador. Não usar dados pessoais reais.

| Caminho | Responsabilidade |
| --- | --- |
| `src/app/` | Layout, navegação e estado local das revisões |
| `src/features/analysis/` | Upload, parser e evidências |
| `src/features/operations/` | Painel, mapa, filtros, revisão e histórico |
| `src/shared/` | Componentes compartilhados |
| `tests/` | Fluxos de navegador e respostas simuladas |

## Testes disponíveis

```powershell
npm run build
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
npm test
```

Usar um Chromium/Chrome existente ou preparar o navegador separadamente, com
autorização para download. Não executar outro Vite na porta 5173 durante a suíte.
O diagnóstico de 17/11 aprovou nove testes e ignorou um teste optativo; a
[validação da consolidação](../docs/VALIDACAO_CONSOLIDACAO_2026-11-17.md) registra a reexecução.

Os fixtures de inferência usam `ANALYZED` e não incluem `model`. O teste optativo
habilitado por `VISION_API_SMOKE_IMAGE` ainda espera a v0.2.0, sem inferência;
não habilitá-lo para alegar teste da v0.3.0. Ele precisa ser atualizado em uma
próxima etapa. A suíte padrão verifica respostas simuladas, não YOLO real.

## Limites e publicação

Não há autenticação, câmera operacional integrada ao painel, vínculo com cadastro
Spring, edição real de polígonos, detecção de EPIs ou auditoria persistente no
servidor. Mapa/alertas ilustrativos não comprovam funcionalidades de IA.
Os ativos SVG são locais; a fotografia usada na validação Python não é distribuída.

O frontend 0.1.1 acompanha o backend e a documentação na `main`. Preservar o
`package-lock.json`; excluir `node_modules`, `dist`, relatórios e `.env.local`.
Em produção será necessário configurar o encaminhamento HTTP no servidor; o
destino final deverá acompanhar a futura integração via Spring Boot.

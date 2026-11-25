# Visão do Porto · Frontend 0.1.1

Interface React/Vite do piloto acadêmico. Documentação alinhada à implementação
local da T16 de 24/11/2026. O painel, a planta, os alertas e a revisão são
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

## Conexão com os serviços de visão

Em outro terminal, a partir da raiz do repositório:

```powershell
cd backend/fastapi
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

O ambiente Python e os pesos devem estar preparados conforme o [README principal](../README.md).
O Vite encaminha `/api/v1/vision/*` ao destino definido por `VISION_API_TARGET`.
O padrão sem variável é o FastAPI direto (`http://127.0.0.1:8000`). O arquivo
`.env.example` recomenda o Spring Boot (`http://127.0.0.1:8080`), que encaminha
as solicitações de imagem ao FastAPI. Para usar esse caminho, inicie também o
Spring conforme o README principal.

Copie `.env.example` para `.env.local`, ajuste o destino se necessário e reinicie
o Vite. O proxy é de desenvolvimento e não é incluído no build de produção.

A tela de análise usa `POST /api/v1/vision/analyze` (YOLO11n para pessoas),
com upload JPEG/PNG multipart no campo `file`. As APIs também disponibilizam
`POST /api/v1/vision/analyze/ppe` para YOLO26s, mas a tela atual não seleciona
essa rota. O parser renderiza caixas e confiança e distingue zero detecções de
falha. O tipo/parser atual não preserva `model` e não restringe `status`.

A T16 adiciona os rótulos `vest` (Colete), `no_helmet` (Sem capacete) e
`no_vest` (Sem colete), preservando `safety_vest` (Colete) e os demais rótulos.
O aceite formal da frente de frontend segue pendente. Consulte o
[contrato IA–backend](../docs/contrato-ia-backend.md).

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

Na validação local da T16, o build e nove testes Playwright passaram antes e
depois; um teste opcional permaneceu desabilitado. Os dois destinos do proxy
e os rótulos foram verificados no navegador, conforme o
[acompanhamento](../docs/ACOMPANHAMENTO_VC.md).

Os fixtures de inferência usam `ANALYZED` e não incluem `model`. O teste optativo
habilitado por `VISION_API_SMOKE_IMAGE` ainda espera a v0.2.0, sem inferência;
não habilitá-lo para alegar teste da v0.3.0. Ele precisa ser atualizado em uma
próxima etapa. A suíte padrão verifica respostas simuladas, não YOLO real.

## Limites e publicação

Não há autenticação, câmera operacional integrada ao painel, vínculo do painel
com o cadastro Spring, edição real de polígonos ou revisão persistida no servidor
pela interface. O backend possui APIs de zonas, eventos, revisão e streaming,
mas essas funcionalidades não estão conectadas às telas de operações. A API de
EPI também está disponível, sem integração de seleção dessa rota na tela atual.
Mapa e alertas ilustrativos não comprovam funcionalidades de IA.
Os ativos SVG são locais; a fotografia usada na validação Python não é distribuída.

Preserve `package-lock.json`; exclua `node_modules`, `dist`, relatórios e
`.env.local` do versionamento. O piloto deve permanecer em loopback. Antes de
uma implantação operacional, serão necessários controle de acesso, configuração
do encaminhamento HTTP e validações adicionais. Veja as
[limitações do piloto](../docs/LIMITACOES_VC.md).

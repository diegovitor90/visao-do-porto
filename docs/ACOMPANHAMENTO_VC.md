# Acompanhamento da frente de visão computacional

Implementação e revisão técnica em 24/11/2026. Branch local `feat/vc-implementacao-local`,
base `65c5f23`. D1 a D7 autorizadas pelo responsável para implementação
local experimental. A T16 recebeu autorização para implementação local.
O aceite coletivo e a confirmação da D8 seguem pendentes.

| Tarefa | Estado | Arquivos principais | Testes e critérios | Pendências |
| --- | --- | --- | --- | --- |
| T01 | IMPLEMENTADA | `training/MODEL_CARD_epi_v1.md`, `training/verificar_modelo.py` | SHA-256 confirmado, classes lidas e inferência em CPU com Ultralytics 8.4.212 | D8 |
| T02 | IMPLEMENTADA | `vision/config.py`, `vision/detector.py`, `main.py`, `demo_visual.py` | Testes legados; importação a partir da raiz e resolução dos pesos a partir de outra pasta | |
| T03 | IMPLEMENTADA | `main.py`, `vision/detector.py`, `test_ppe.py` | Detecção e validação simuladas; sucesso real e erro 422 após carregar o modelo | |
| T04 | IMPLEMENTADA | `VisionClient`, `VisionController`, `VisionClientTest` | 13 testes MockMvc; JSON idêntico para imagem real e status acessível via proxy Vite | |
| T05 | IMPLEMENTADA | `sources.py`, `metrics.py`, `cli.py` | Vídeo sintético valida ordem, descarte, métricas e encerramento | |
| T06 | IMPLEMENTADA | `tracker.py`, `cli.py`, `integracao/test_modelos_reais.py` | ByteTrack em CPU, teste lento aprovado, UUID e IDs isolados. Métricas no README | |
| T07 | IMPLEMENTADA | `association.py`, `test_association.py` | 16 casos sintéticos de geometria, exclusividade e sinais contraditórios | |
| T08 | IMPLEMENTADA | `state.py`, `test_state.py` | 12 sequências; estados, confiança, oscilação, expiração e lacunas de detecção | |
| T09 | IMPLEMENTADA | `pipeline.py`, `cli.py`, `test_pipeline.py`, `AVALIACAO_VC.md` | Teste ponta a ponta simulado e dois trechos públicos anotados com medição CPU | YOLO26n opcional |
| T10 | IMPLEMENTADA | `ZonaController`, `ZonaService`, `ZonaApiTest`, `ZONAS.md` | 8 testes; geometria, atomicidade, versão, isolamento e lista vazia | |
| T11 | IMPLEMENTADA | `zones.py`, `test_zones.py`, `zonas/CAM-LAB-01.exemplo.json` | Côncavo, duas resoluções, persistência, histerese, perda breve do track e JSON com BOM | |
| T12 | IMPLEMENTADA | `events.py`, `rules.py`, `test_rules.py` | Deduplicação e reabertura em teste. Vídeo com pesos reais gerou quatro JPEGs e JSONL | |
| T13 | IMPLEMENTADA | `EventoVisaoController`, `EventoVisaoService`, `EventoVisaoApiTest` | 10 testes; ingestão, reenvio, conflito, filtros, revisão e referência JPEG de outro evento rejeitada | |
| T14 | IMPLEMENTADA | `spring_client.py`, `test_spring_client.py`, `cli.py` | Cache por câmera com IDs que diferem em caixa; fila preservada com falha no JSONL. Quatro eventos recebidos após reinício do Spring | |
| T15 | IMPLEMENTADA | `sources.py`, `service.py`, `main.py`, `test_live.py` | Stream, reconexão e captura na mesma thread com fonte simulada. OpenCV conectou à escuta RTSP local sem credenciais no log. Endpoint rejeitou caminho de evidência resolvido fora da pasta | Webcam física e transmissão de câmera RTSP |
| T16 | IMPLEMENTADA | `frontend/.env.example`, `frontend/src/features/analysis/api.ts` | Build e 9 testes Playwright antes e depois. Proxy direto e via Spring, rótulos novos e legados verificados no navegador | Aceite formal da frente de frontend |
| T17 | PARCIAL | `avaliacao/`, `test_avaliacao.py`, `AVALIACAO_VC.md` | Exportação real de CSVs; cálculo validado com rótulos sintéticos; medições públicas de CPU | Rótulos manuais, avaliação de acerto/eventos e calibração |
| T18 | IMPLEMENTADA | `README.md`, `contrato-ia-backend.md` | Inicialização dos três serviços em loopback, proxy Vite e rotas de imagem, zonas e eventos verificados | |

## Validação final

- FastAPI com `python -m pytest -q -p no:cacheprovider`. 98 aprovados e um
  teste lento excluído da execução padrão. O teste de evidência usa link real
  quando permitido ou simula apenas a resolução do caminho no Windows.
  Permanece o aviso de depreciação do cliente de testes.
- FastAPI com `python -m pytest -q -m slow integracao`. Um teste real aprovado.
  `python -m pip check` confirmou as dependências.
- Spring Boot com `mvnw.cmd -o package` em JDK 21.0.4. 51 testes aprovados.
- Frontend em Node 20.20.2. Na T16, `npm run build` e Playwright passaram
  antes e depois, com 9 testes aprovados e 1 opcional da FastAPI v0.2.0
  ignorado em cada execução.
- T16 no navegador com inferência real. Via FastAPI direta e via Spring,
  status, imagem e EPI responderam HTTP 200. Os dois destinos retornaram
  JSON equivalente, com 4 detecções de pessoas, 10 do modelo de EPI e HTTP 422
  para JPEG inválido. Uma resposta controlada verificou os rótulos novos e
  legados na lista e no SVG.
- Exercício local com FastAPI, Spring e Vite e banco/fila temporários. Imagem de
  exemplo do Ultralytics com quatro detecções de pessoas e dez detecções do
  modelo de EPI. Ambas as respostas foram iguais no FastAPI e no Spring.
  Upload corrompido retornou 422 nos dois após carregar os pesos. Vídeo sintético
  de 16 quadros, produzido com a imagem de exemplo, gerou quatro alertas com
  o Spring desligado. A fila foi drenada ao reiniciar o Spring. O reenvio
  preservou a revisão e a rota de evidências devolveu JPEG válido.

Linha de base anterior às mudanças: 17 testes Python e 20 Java aprovados.
A única dependência nova do projeto é `lap==0.5.12`, exigida pelo ByteTrack.
O `httpx==0.28.1` passou a dependência de execução, com a mesma versão.
O pin do Ultralytics continua em 8.4.212. A revisão não adicionou dependências.

[Roteiro de testes manuais no Windows](ROTEIRO_TESTES_VC.md).

## Limitações e próxima validação

As limitações técnicas, operacionais e prioridades recomendadas estão em
[LIMITACOES_VC.md](LIMITACOES_VC.md). A próxima validação prática será realizada
com a equipe. Esta atualização documental não altera os estados das tarefas nem
acrescenta resultados de testes.

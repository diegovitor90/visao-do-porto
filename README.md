# Visão do Porto

MVP acadêmico de apoio à segurança portuária. O FastAPI analisa imagens e
vídeos, acompanha pessoas e EPIs, avalia zonas e gera eventos com evidências.
O Spring Boot mantém zonas e regras, recebe eventos e registra a revisão.
O frontend React/Vite oferece a demonstração de análise por imagem.

| Componente | Fluxo disponível | Evidência |
| --- | --- | --- |
| FastAPI | Imagens, YOLO11n, YOLO26s, ByteTrack, regras, arquivo de vídeo, webcam e RTSP | Suíte pytest e [medições CPU](docs/AVALIACAO_VC.md) |
| Spring Boot | Trabalhadores, capacitações, encaminhamento de imagens, cadastro de zonas, eventos e revisão | JUnit 5 e MockMvc |
| Frontend | Painel e upload via proxy Vite | Build local e verificação do proxy |

[Estado T01 a T18](docs/ACOMPANHAMENTO_VC.md) ·
[Contrato IA–backend](docs/contrato-ia-backend.md) ·
[Zonas e regras](docs/ZONAS.md) ·
[Roteiro de testes](docs/ROTEIRO_TESTES_VC.md) ·
[Avaliação](docs/AVALIACAO_VC.md) ·
[Limitações e pendências](docs/LIMITACOES_VC.md)

```text
Frontend → proxy Vite → FastAPI                       (padrão)
Frontend → proxy Vite → Spring Boot → FastAPI         (via VISION_API_TARGET)
Imagem/vídeo → FastAPI → modelos → eventos/evidências → SQLite → Spring Boot
FastAPI ← zonas e regras ← Spring Boot
Cliente administrativo → Spring Boot → JPA / H2
```

## Iniciar em três terminais PowerShell

Execute cada bloco em um terminal separado, partindo da raiz do repositório.

**Spring Boot** com JDK 21 e Maven Wrapper. O serviço escuta em `127.0.0.1:8080`.

```powershell
cd backend/backend-springboot
.\mvnw.cmd test
.\mvnw.cmd spring-boot:run
```

Use `-o` quando todos os plugins e dependências já estiverem no cache.

**FastAPI** com Python 3.11 ou 3.12. A validação usou Python 3.12.7.

```powershell
cd backend/fastapi
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --timeout-graceful-shutdown 10
```

Reutilize a `.venv` quando já estiver preparada. De outro diretório, inclua
`--app-dir C:/caminho/backend/fastapi` no Uvicorn. OpenAPI fica em
`http://127.0.0.1:8000/docs`. Com os pesos locais, execute o teste real separado
com `.\.venv\Scripts\python.exe -m pytest -q -m slow integracao`.

**Frontend** com Node.js 20.19+ ou 22.12+. O build foi verificado em Node 20.20.2.

```powershell
cd frontend
npm ci
npm run build
$env:VISION_API_TARGET = 'http://127.0.0.1:8080'
npm run dev -- --host 127.0.0.1
```

Abra `http://127.0.0.1:5173`. O `frontend/.env.example` aponta para o Spring
em `127.0.0.1:8080`. Para usar o FastAPI diretamente, configure
`VISION_API_TARGET=http://127.0.0.1:8000` ou use o padrão do Vite sem a variável.
Reinicie o Vite após trocar o destino.

O ajuste local T16 traduz `vest` como **Colete**, `no_helmet` como **Sem capacete**
e `no_vest` como **Sem colete**. O alias `safety_vest` também aparece como
**Colete**. O build e os nove testes Playwright ativos passaram antes e depois
do ajuste. A validação no navegador confirmou os dois destinos do proxy.
[Resultados da T16](docs/ACOMPANHAMENTO_VC.md).

## Pesos e configuração

Coloque os pesos locais em `backend/fastapi/models/`. A API carrega os modelos
sob demanda em CPU. Instale pacotes e obtenha os pesos na preparação do ambiente.

| Peso | Uso | Origem e SHA-256 |
| --- | --- | --- |
| `yolo11n.pt` | Pessoas e ByteTrack | [Ultralytics Assets v8.4.0](https://github.com/ultralytics/assets/releases/tag/v8.4.0). `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1` |
| `best_epi_grupo_yolo26s.pt` | Capacete, colete e sinais de ausência | [Ficha e verificação do treino](backend/fastapi/training/MODEL_CARD_epi_v1.md) |

| Variável | Padrão |
| --- | --- |
| `VISION_MODELS_DIR` | `backend/fastapi/models`. Fallback legado de YOLO11n junto à API |
| `SPRING_BASE_URL` | `http://127.0.0.1:8080` |
| `VISION_API_URL` | `http://127.0.0.1:8000`, destino do cliente Spring |
| `VISION_API_TARGET` | `http://127.0.0.1:8000`, destino do proxy Vite |
| `VISION_EVIDENCE_DIR` | `backend/fastapi/evidencias` |
| `VISION_EVENTS_FILE` | `backend/fastapi/eventos_locais.jsonl` |
| `VISION_EVENT_QUEUE` | `backend/fastapi/eventos.sqlite3` |
| `VISION_ZONES_CACHE` | `backend/fastapi/zonas_cache` |

## Testar a visão

O [roteiro manual PowerShell](docs/ROTEIRO_TESTES_VC.md) cobre imagens, vídeo,
tracking, zonas, eventos, evidências e webcam.

JPEG e PNG de até 5 MiB e 20 megapixels. Use o campo multipart `file`.

```powershell
curl.exe -F "file=@C:/caminho/imagem.png;type=image/png" http://127.0.0.1:8000/api/v1/vision/analyze
curl.exe -F "file=@C:/caminho/imagem.png;type=image/png" http://127.0.0.1:8080/api/v1/vision/analyze/ppe
```

A partir de `backend/fastapi`, teste o vídeo com as zonas locais do exemplo.
Troque `--zonas ...` por `--spring` para ler as zonas cadastradas e publicar
eventos. Para medir apenas pessoas e ByteTrack, passe `--track` como única opção de detecção.
Sem `--sem-descarte`, o leitor pode substituir quadros atrasados.

```powershell
.\.venv\Scripts\python.exe -m vision.cli --source C:/caminho/video.mp4 --epi models/best_epi_grupo_yolo26s.pt --zonas zonas/CAM-LAB-01.exemplo.json --camera CAM-LAB-01 --sem-descarte --saida "$env:TEMP/porto-anotado.mp4"
```

Para RTSP, coloque a URL na variável local `PORTO_RTSP_URL` e envie a
configuração `@{camera_id='CAM-LAB-02'; source='RTSP'; rtsp_url=$env:PORTO_RTSP_URL}`.
O exemplo a seguir usa uma webcam e abre o stream anotado em MJPEG. Interrompa
o `curl` com Ctrl+C antes de executar o DELETE.

```powershell
$api = 'http://127.0.0.1:8000'
$config = @{camera_id='CAM-LAB-01'; source='WEBCAM'; webcam_index=0}
$fonte = Invoke-RestMethod "$api/api/v1/sources" -Method Post -ContentType 'application/json' -Body ($config | ConvertTo-Json)
curl.exe --output "$env:TEMP/porto-stream.mjpeg" "$api/api/v1/sources/$($fonte.id)/stream"
Invoke-RestMethod "$api/api/v1/sources/$($fonte.id)" -Method Delete
```

Para cadastrar áreas, use o [exemplo de PUT](docs/ZONAS.md). A revisão usa
`PATCH /api/v1/eventos/{id}/revisao` com `{"status":"CONFIRMADO"}`.
Para `DESCARTADO`, inclua `motivo`.

## Rotas

| Serviço | Método e caminho |
| --- | --- |
| Ambos | GET `/api/health`, GET `/api/v1/vision/status` |
| Ambos | POST `/api/v1/vision/analyze`, POST `/api/v1/vision/analyze/ppe` |
| FastAPI | POST `/api/v1/sources`, DELETE `/api/v1/sources/{id}`, GET `/api/v1/sources/{id}/stream` |
| FastAPI | GET `/api/v1/evidencias/{evidence_ref}` |
| Spring Boot | GET/PUT `/api/v1/cameras/{cameraId}/zonas` |
| Spring Boot | POST/GET `/api/v1/eventos`, GET `/api/v1/eventos/{id}`, PATCH `/api/v1/eventos/{id}/revisao` |
| Spring Boot | POST/GET `/api/trabalhadores`, GET `/api/trabalhadores/{id}`, [rotas de capacitações](docs/CAPACITACOES.md) |

## Medições em CPU

Windows 11, Intel Core i7-1165G7, Python 3.12.7, Ultralytics 8.4.212, Torch 2.15.0,
OpenCV 5.0.0.93 e lap 0.5.12. Trechos de três segundos com `--sem-descarte`
e vídeo anotado. A latência inclui espera, processamento e escrita do quadro.

| Configuração | Resolução | Quadros | FPS | Mediana (ms) | p95 (ms) |
| --- | --- | ---: | ---: | ---: | ---: |
| YOLO11n + ByteTrack | 360×640 | 75 | 6,76 | 117,81 | 183,93 |
| YOLO11n + ByteTrack + YOLO26s | 360×640 | 75 | 3,88 | 395,45 | 495,71 |
| YOLO11n + ByteTrack + YOLO26s | 640×360 | 72 | 4,43 | 306,28 | 383,35 |

Fontes, rótulos e procedimento em [Avaliação de visão computacional](docs/AVALIACAO_VC.md).

## Validação e limites do piloto

O piloto é acadêmico e experimental. Não foi validado para operação portuária real.
A análise por imagem está integrada ao frontend; painel, mapa, alertas e revisão
na interface ainda são demonstrativos. A gestão real de zonas e eventos está
disponível pelas APIs do Spring Boot, e o stream anotado pela API do FastAPI.

| Limitação | Impacto | Prioridade |
| --- | --- | --- |
| Zonas carregadas no início da sessão e na reconexão | Alterações no Spring não chegam imediatamente à fonte ativa | Média |
| Spring indisponível e cache de zonas ausente ou inválido | A inferência continua, mas sem avaliação de infrações por zona | Média |
| H2 em memória | Zonas, eventos e revisões são perdidos ao reiniciar o Spring | Alta para produção |
| Pipeline completo em CPU: 3,88 a 4,43 FPS nos trechos medidos | Capacidade de monitoramento limitada; desempenho ao vivo ainda não validado | Média |
| Ausência de autenticação e identificação do revisor | Inadequado para exposição pública | Alta para produção |
| Webcam física e transmissão RTSP de câmera | Validação com equipamentos reais pendente | Média |
| Qualidade dos eventos e calibração (T17) | Precisão, recall e demais métricas empíricas dependem de rótulos manuais | Alta para validação científica |

Execute em loopback (`127.0.0.1`) com dados autorizados para teste. O `track_id`
é efêmero e tem escopo de câmera e sessão. Área restrita sinaliza presença, sem
avaliar autorização de acesso (`NAO_AVALIADA`). A fila SQLite e os JPEGs locais
persistem no disco, mas não restauram automaticamente o histórico já confirmado
pelo Spring. Consulte [limitações e próximos passos](docs/LIMITACOES_VC.md).

As tarefas T01–T16 e T18 estão registradas como implementadas localmente;
T17 permanece parcial. A aprovação coletiva de D1–D7, a confirmação das
licenças (D8) e o aceite formal da frente de frontend para T16 seguem pendentes.
Os resultados da execução anterior estão em [acompanhamento](docs/ACOMPANHAMENTO_VC.md).
A próxima validação prática será realizada com a equipe; não há novos resultados
de câmera física ou de avaliação empírica nesta revisão documental.

[Plano histórico](docs/PLANO_MVP.md) · [Rastreabilidade](docs/RASTREABILIDADE.md) ·
[Validação anterior](docs/VALIDACAO_CONSOLIDACAO_2026-11-17.md)

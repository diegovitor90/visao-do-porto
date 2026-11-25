# Contrato IA–backend

Referência do piloto local em 24/11/2026. FastAPI infere, processa fontes
e publica eventos. Spring Boot mantém zonas e regras, recebe eventos e registra
a revisão. Payloads de visão usam snake_case e datas ISO-8601. APIs
administrativas usam camelCase.

## Análise de imagens

FastAPI (`127.0.0.1:8000`) e Spring (`127.0.0.1:8080`) expõem
`POST /api/v1/vision/analyze` e `POST /api/v1/vision/analyze/ppe`. Envie
multipart com o campo `file` e MIME `image/jpeg` ou `image/png`.
O limite é 5 MiB, com até 20 milhões de pixels. O Spring aceita requisições
multipart de até 6 MiB e encaminha o nome e o MIME da parte.

```json
{
  "filename": "imagem.png",
  "width": 640,
  "height": 480,
  "status": "COMPLETED",
  "inference_performed": true,
  "model": "yolo11n",
  "detections": [
    {"class_id": 0, "class_name": "person", "confidence": 0.8246,
     "bbox": {"x1": 37.02, "y1": 34.14, "x2": 320.36, "y2": 451.73}}
  ],
  "message": "Análise de imagem concluída."
}
```

Ambos retornam HTTP 200 e aceitam `detections: []`. Coordenadas são em pixels
da imagem original. `/analyze` usa YOLO11n para pessoas com limiar 0,40.
`/analyze/ppe` usa `best_epi_grupo_yolo26s.pt` com limiar 0,40. O modelo de EPI
pode retornar `person`, `helmet`, `no_helmet`, `vest` e `no_vest`. Os nomes
vêm de `model.names`. A análise de imagem informa detecções de um quadro.

| HTTP | Causa |
| --- | --- |
| 413 | Limite de arquivo, requisição multipart ou dimensões excedido |
| 415 | MIME ou formato fora dos tipos aceitos |
| 422 | Imagem corrompida ou, no FastAPI, parâmetro obrigatório ausente |
| 400 | Campo multipart ausente no Spring |
| 503 | Inferência ou Vision API indisponível |
| 504 | Timeout entre Spring e FastAPI |
| 502 | Resposta inválida ou inesperada da Vision API |

O FastAPI envia `detail` em falhas explícitas. O Spring devolve ProblemDetail
e usa timeout de conexão de 2 s e leitura de 15 s. Os serviços expõem
`GET /api/health` e `GET /api/v1/vision/status`. O status inclui `service`,
`model`, `model_loaded`, `ppe_model_loaded`, `inference_available`, `status`,
`message`, `sources` e `fps`. `READY` indica que a tentativa de inferência
está disponível. Os campos `*_model_loaded` consultam os caches de modelos.

## Proxy Vite e rótulos do frontend

O `frontend/.env.example` sugere `VISION_API_TARGET=http://127.0.0.1:8080`
para o Spring intermediar a Vision API. Use `http://127.0.0.1:8000` para falar
diretamente com o FastAPI. Esse também é o padrão do Vite sem a variável.
Reinicie o Vite ao trocar o alvo.

A tela de análise usa `POST /api/v1/vision/analyze`. Na lista de detecções
e nas caixas do frontend, `vest` e `safety_vest` aparecem como **Colete**,
`no_helmet` como **Sem capacete** e `no_vest` como **Sem colete**.

Na validação da T16, os dois destinos devolveram HTTP 200 no status e nas
rotas de imagem e EPI, com JSON equivalente para os mesmos arquivos. O
JPEG inválido retornou 422 nos dois caminhos. Uma resposta controlada
confirmou a exibição dos rótulos no navegador.

## Zonas no Spring

`GET /api/v1/cameras/{cameraId}/zonas` devolve a lista de zonas ativas, ou `[]`.
`PUT` substitui a lista de forma atômica. Omita `zone_id` para criar e forneça
o UUID para atualizar. Um item omitido é desativado.

| Campo | Tipo |
| --- | --- |
| `zone_id` | UUID atribuído pelo Spring |
| `nome` | Nome da zona |
| `polygon` | Lista de 3 a 16 pares `[x,y]` normalizados |
| `required_ppe` | Lista de `CAPACETE` e/ou `COLETE` |
| `rule_type` | `EPI_OBRIGATORIO` ou `AREA_RESTRITA` |
| `rule_id` | Identificador estável. Se omitido na criação, usa o UUID da zona |
| `rule_version` | Inteiro gerado pelo Spring. Começa em 1 e sobe quando mudam polígono, EPIs ou tipo |
| `ativa` | Booleano. Padrão `true` no PUT |

O FastAPI carrega zonas no início da fonte, na reconexão e no CLI `--spring`.
Uma leitura bem-sucedida atualiza o cache por câmera. Os arquivos novos usam
o hash do identificador para distinguir câmeras mesmo em diretórios Windows
insensíveis a maiúsculas e minúsculas. Durante indisponibilidade, a API usa
a última lista disponível e aceita o formato anterior `<camera>.json` se o
nome corresponder exatamente. Não há atualização periódica durante uma sessão:
para aplicar uma alteração de zona imediatamente no piloto, encerre e inicie
novamente a fonte. Se a consulta falhar e não houver cache válido, o provedor
retorna uma lista vazia, registra aviso e o pipeline continua sem avaliar regras
por zona. Um GET bem-sucedido com lista vazia atualiza o cache normalmente.
Veja o [exemplo de cadastro](ZONAS.md).

## Eventos v0.2

`POST /api/v1/eventos` no Spring recebe os campos abaixo.

| Campo | Regra |
| --- | --- |
| `schema_version` | `"0.2"` |
| `event_id` | UUID, chave de idempotência |
| `camera_id` | 1 a 100 caracteres alfanuméricos, hífen ou sublinhado |
| `session_id` | UUID gerado a cada início ou reconexão |
| `zone_id` | UUID da zona |
| `timestamp` | ISO-8601 UTC, instante de captura do quadro |
| `event_type` | `INTRUSAO`, `EPI_AUSENTE` ou `EPI_INDETERMINADO` |
| `track_id` | Inteiro ≥ 0, efêmero e restrito à câmera e à sessão |
| `rule_id`, `rule_version` | Identificador da regra e versão ≥ 1 |
| `confidence` | Confiança visual de 0 a 1 ou `null` |
| `evidence_ref` | Nome `<event_id>.jpg` ou `null` |
| `source` | `ARQUIVO`, `WEBCAM` ou `RTSP` |
| `explanation` | Texto em português com zona, condição, duração e regra |

O FastAPI usa o ponto dos pés e confirma entrada após 5 quadros e saída após
10 quadros. Durante uma perda breve do track, a zona mantém presença com
pés incertos até o limite de saída. Cada EPI usa até 15 quadros processados,
começa após 8 observações do track e exige consenso de 70% e qualidade.
Um quadro processado sem o track conta como falta de evidência. Sinal contraditório com diferença de confiança
menor que 0,10 fica sem evidência. Uma condição indeterminada mantida por mais
de 5 s em zona de EPI gera `EPI_INDETERMINADO`. Ausência exige evidência
negativa temporal. Pés incertos impedem a abertura de evento naquele quadro.
A chave de deduplicação usa sessão, track, zona, regra e tipo. Uma nova abertura
exige o encerramento da condição e um intervalo mínimo de 30 s.

O pipeline grava JPEG e JSONL localmente. Com integração ativa, a fila SQLite
é gravada antes do JSONL e processada em ordem por uma thread própria. Uma falha
no JSONL fica registrada no log e a publicação continua. Se a gravação em
SQLite falhar, o processo ainda tenta gravar o evento no JSONL e sinaliza o erro.
A fila reenvia somente itens persistidos em SQLite. HTTP 200 ou 201 confirma o envio.
Falhas de transporte, HTTP 408, 429 e 5xx têm reenvio com espera de 1 a 60 s.
Outros 4xx ficam em `rejeitados`. O FastAPI retoma itens pendentes quando sobe.

| Operação no Spring | Resultado |
| --- | --- |
| POST `/api/v1/eventos` | 201 novo, 200 reenvio idêntico, 409 colisão de conteúdo, 400 validação |
| GET `/api/v1/eventos` | Mais recentes primeiro. Filtros `camera_id`, `zone_id`, `event_type`, `review_status`, `desde` e `limite` (100 padrão, 500 máximo) |
| GET `/api/v1/eventos/{id}` | Evento ou 404 |
| PATCH `/api/v1/eventos/{id}/revisao` | Atualiza `status` e `motivo`, obrigatório para descarte, ou 404 |

O Spring adiciona `received_at`, `review_status`, `reviewed_at` e
`review_reason`. O status inicial é `PENDENTE`. A revisão permite definir
`CONFIRMADO`, `DESCARTADO`, `INDETERMINADO` ou reabrir como `PENDENTE`.
O Spring ignora `review_status` no recebimento. O evento registra apenas
referências visuais, sem campos cadastrais. O revisor fica sem identificação.

## Fontes e evidências no FastAPI

| Operação | Dados |
| --- | --- |
| POST `/api/v1/sources` | `camera_id` e `source`. Webcam aceita `webcam_index` de 0 a 255, padrão 0. RTSP exige `rtsp_url`. Retorna 201 e `id` UUID |
| DELETE `/api/v1/sources/{id}` | 204 ao encerrar, 404 fonte ausente ou 503 se ainda estiver encerrando |
| GET `/api/v1/sources/{id}/stream` | MJPEG, `multipart/x-mixed-replace; boundary=frame`, ou 404 |
| GET `/api/v1/evidencias/{evidence_ref}` | JPEG identificado por UUID dentro da pasta de evidências, ou 404 |

O status informa câmera, tipo, sessão e métricas por fonte. Cada fonte tem
um tracker próprio. Uma trava protege o contador global do ByteTrack e outra
serializa o acesso aos detectores de imagem/EPI em cache. A captura reconecta
com espera de 1 a 30 s. URL e credenciais RTSP ficam fora das respostas e
dos logs. Os endpoints são locais e operam sem autenticação.

## Limites operacionais

O H2 do Spring é volátil: reiniciar o serviço elimina zonas, eventos e revisões.
A fila SQLite mantém apenas os itens ainda pendentes de entrega; eventos já
confirmados pelo Spring não são reenviados automaticamente após o reinício.
O piloto deve permanecer em loopback, sem exposição pública. Os testes com
webcam física e transmissão de câmera RTSP, assim como a avaliação empírica
dos eventos (T17), seguem pendentes. As medições curtas em CPU estão em
[AVALIACAO_VC.md](AVALIACAO_VC.md). Consulte as
[limitações e pendências operacionais](LIMITACOES_VC.md).

## Pendências

Aceite coletivo de D1 a D7, confirmação de licenças, autenticação e perfis,
retenção de evidências, dados do laboratório e aceite formal da frente de
frontend para o ajuste local T16. O vínculo
manual entre evento e trabalhador e a proposta de observações por quadro
de 13/11 permanecem fora do contrato ativo.

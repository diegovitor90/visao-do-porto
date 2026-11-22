# Contrato IA–backend: API real e evolução planejada

Revisão: **17/11/2026**. Este é o documento único de referência. A primeira seção
descreve a FastAPI local **v0.3.0**; a proposta histórica ao final é planejamento e
não deve ser usada como payload do endpoint de análise.

## Contrato implementado — análise de imagem

Fonte: `backend/fastapi/main.py`, modelos Pydantic `ImageAnalysisResponse`,
`Detection` e `BoundingBox`; detector em `vision_detector.py`.

```http
POST /api/v1/vision/analyze
Content-Type: multipart/form-data; boundary=...
```

Parte obrigatória `file`, com nome do arquivo e `Content-Type` `image/jpeg` ou
`image/png`. Limites: 5.242.880 bytes e 20.000.000 pixels. O conteúdo deve ser JPEG
ou PNG íntegro, verificado pelo Pillow. Não enviar JSON/base64 nesse endpoint.

Resposta HTTP 200, exemplo da validação real histórica:

```json
{
  "filename": "teste_pessoas.png",
  "width": 767,
  "height": 766,
  "status": "COMPLETED",
  "inference_performed": true,
  "model": "yolo11n",
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.8246,
      "bbox": {"x1": 37.02, "y1": 34.14, "x2": 731.36, "y2": 751.73}
    }
  ],
  "message": "Análise de imagem concluída."
}
```

| Campo | Tipo | Semântica atual |
| --- | --- | --- |
| `filename` | string | Nome recebido; fallback `sem_nome` |
| `width`, `height` | inteiro | Dimensões da imagem original |
| `status` | string | `COMPLETED` após inferência bem-sucedida |
| `inference_performed` | boolean | `true` no sucesso da v0.3.0 |
| `model` | string | `yolo11n` |
| `detections` | lista | Pode ser vazia sem erro |
| `message` | string | Mensagem de conclusão |
| `detections[].class_id` | inteiro | `0`, classe pessoa |
| `detections[].class_name` | string | `person` |
| `detections[].confidence` | número | Confiança de detecção, arredondada a quatro casas |
| `detections[].bbox` | objeto | `x1`, `y1`, `x2`, `y2` numéricos, em pixels, arredondados a duas casas |

O detector usa CPU, limiar 0.40 e filtro `classes=[0]`. A inferência roda fora do
event loop e os pesos são carregados sob demanda/cache. Os tipos dos schemas não
impõem por si só todos os limites geométricos ou intervalo de confiança; não
confundir comportamento do detector com validações Pydantic adicionais.

| HTTP | Causa |
| --- | --- |
| 413 | Arquivo acima de 5 MiB ou imagem acima de 20 MP |
| 415 | MIME declarado ou formato real não suportado |
| 422 | Imagem inválida/corrompida ou validação automática da entrada |
| 503 | Detector/inferência indisponível ou falha na construção da resposta |

Os erros explícitos usam `{"detail":"mensagem"}`; validação automática pode
retornar `detail` como lista. Ausência do campo `file` é erro de entrada.

Também implementados: `GET /api/health`, `GET /api/v1/vision/status` e OpenAPI em
`/openapi.json`. O status `READY` não carrega o modelo nem garante inferência.

## Consumidores e integração pendente

Hoje o frontend chama a FastAPI pelo proxy Vite. Seu parser utiliza os campos de
imagem/detecções, mas descarta `model`; os fixtures antigos usam `ANALYZED`, sem
restringir `status`. Esses limites não alteram a resposta real `COMPLETED`.

O [ADR-001](arquitetura/adrs/ADR-001.adoc) mantém o upload e os frames no fluxo
de visão. O Spring Boot expõe dados administrativos por matrícula. A integração
operacional deverá trocar metadados com contratos próprios para origem, falhas,
repetição e atualização. A Vision API v0.3.0 mantém os endpoints e formatos acima.

## Diferenças em relação à proposta de 13/11

`frame_width/frame_height`, `person_confidence` e `bbox_xyxy` não são nomes da API
real. Não há `track_id`, `zone_id`, câmera, sessão, observação, PPE ou identidade
na análise v0.3.0. Não fabricar esses campos nem inferir vínculos administrativos.

## Proposta histórica — não implementada

O texto abaixo preserva a proposta de 13/11 como referência de evolução. Ele não
é um segundo contrato ativo; sua implementação exigirá revisão e acordo futuros.

### Observação visual e vínculo administrativo (rascunho de 13/11)

13/11/2026. Rascunho para revisão entre Gustavo, Diego, Jason e Hugo. Este arquivo descreve a próxima integração; endpoints de observação e vínculo ainda não estão implementados.

### Responsabilidades

FastAPI produz observações de detecção/rastreamento. Spring Boot recebe observações e mantém cadastros, capacitações e decisões administrativas. O front-end apresenta a trajetória para confirmação manual pelo operador. Uma detecção não identifica civilmente a pessoa.

### Mensagem candidata de observação

```json
{
  "schema_version": "0.1",
  "observation_id": "uuid-unico-da-observacao",
  "source": "simulated",
  "camera_id": "CAM-LAB-01",
  "session_id": "uuid-da-sessao-de-captura",
  "timestamp": "2026-11-13T15:00:00Z",
  "frame_id": 120,
  "frame_width": 1280,
  "frame_height": 720,
  "track_id": 17,
  "bbox_xyxy": [100, 100, 250, 600],
  "person_confidence": 0.93,
  "quality": "adequate",
  "ppe": {
    "helmet": {"state": "detected", "confidence": 0.87},
    "vest": {"state": "unknown", "confidence": null}
  }
}
```

| Campo/regra | Semântica a preservar |
| --- | --- |
| camera + session + track | Chave conjunta da trajetória; `track_id` sozinho não é único globalmente. |
| session | Nova sessão a cada reinício/reconexão do rastreador; não reaproveitar vínculo antigo. |
| observation_id | Identificador para deduplicação de reenvios. |
| timestamp | Instante de captura com fuso; backend registra também recebimento. |
| frame_id | Ordem crescente dentro da sessão. Definir tratamento de atraso, duplicação e descarte antes de integrar. |
| bbox | Pixels no quadro de referência, x1 < x2 e y1 < y2, dentro da imagem. |
| confidence | Valor entre 0 e 1; confiança de detecção não é confiança de identidade. |
| PPE | `detected`, `not_detected` ou `unknown`. Não detectado não comprova ausência. |
| source | `simulated` em testes; sinalizar claramente no painel. |

### Vínculo manual

O operador seleciona uma trajetória atual e um trabalhador fictício já cadastrado. O registro deverá conter a chave conjunta, UUID do trabalhador, operador autenticado, instante, método de confirmação e motivo da alteração/invalidação. Não enviar nome, CPF ou certificados no evento da IA.

Regras a implementar/testar: perda de trajetória, reinício de sessão, mudança de câmera ou dúvida na associação invalidam o vínculo; dados antigos não podem permanecer como situação atual. Uma confirmação humana pode falhar, e trocas silenciosas de ID precisam ser avaliadas. O limite de idade da observação e o tempo para considerar uma trajetória perdida ainda devem ser acordados com IA/VC.

### Consulta administrativa disponível

Após um vínculo confirmado, a futura integração poderá usar `GET /api/trabalhadores/{uuid}/capacitacoes/{codigo}/situacao`. Sem vínculo, exibir identidade não confirmada. Com vínculo, mostrar separadamente situação da capacitação e resultado da regra de acesso. A consulta implementada retorna `autorizacaoAcesso=NAO_AVALIADA`.

Requisitos de capacitação/EPI por zona, atividade, regras de autorização, versões/fontes, geometria e estados de alerta ainda precisam de definição e implementação. Este contrato não presume que a consulta de treinamento, sozinha, detecte intrusão ou libere acesso.

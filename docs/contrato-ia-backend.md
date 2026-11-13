# Contrato proposto: observação visual e vínculo administrativo

13/11/2026. Rascunho para revisão entre Gustavo, Diego, Jason e Hugo. Este arquivo descreve a próxima integração; endpoints de observação e vínculo ainda não estão implementados.

## Responsabilidades

FastAPI produz observações de detecção/rastreamento. Spring Boot recebe observações e mantém cadastros, capacitações e decisões administrativas. O front-end apresenta a trajetória para confirmação manual pelo operador. Uma detecção não identifica civilmente a pessoa.

## Mensagem candidata de observação

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

## Vínculo manual

O operador seleciona uma trajetória atual e um trabalhador fictício já cadastrado. O registro deverá conter a chave conjunta, UUID do trabalhador, operador autenticado, instante, método de confirmação e motivo da alteração/invalidação. Não enviar nome, CPF ou certificados no evento da IA.

Regras a implementar/testar: perda de trajetória, reinício de sessão, mudança de câmera ou dúvida na associação invalidam o vínculo; dados antigos não podem permanecer como situação atual. Uma confirmação humana pode falhar, e trocas silenciosas de ID precisam ser avaliadas. O limite de idade da observação e o tempo para considerar uma trajetória perdida ainda devem ser acordados com IA/VC.

## Consulta administrativa disponível

Após um vínculo confirmado, a futura integração poderá usar `GET /api/trabalhadores/{uuid}/capacitacoes/{codigo}/situacao`. Sem vínculo, exibir identidade não confirmada. Com vínculo, mostrar separadamente situação da capacitação e resultado da regra de acesso. A consulta implementada retorna `autorizacaoAcesso=NAO_AVALIADA`.

Requisitos de capacitação/EPI por zona, atividade, regras de autorização, versões/fontes, geometria e estados de alerta ainda precisam de definição e implementação. Este contrato não presume que a consulta de treinamento, sozinha, detecte intrusão ou libere acesso.

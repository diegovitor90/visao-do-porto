# Limitações e pendências da visão computacional

## Escopo

Este documento registra as limitações conhecidas do MVP acadêmico implementado
localmente em 24/11/2026. Não constitui homologação operacional. As prioridades
abaixo são recomendações técnicas, sujeitas à revisão pela equipe. Elas não
representam metas aprovadas nem autorização para ampliar o escopo.

## Limitações técnicas e operacionais

| ID | Limitação | Impacto | Prioridade | Encaminhamento recomendado |
| --- | --- | --- | --- | --- |
| L01 | Zonas carregadas no início da fonte, na reconexão e no início do CLI `--spring` | Mudanças de zonas e regras no Spring não são refletidas imediatamente em sessões ativas | Média | Durante o piloto, encerrar e iniciar novamente a fonte após alterar zonas. Avaliar atualização dinâmica em etapa futura. |
| L02 | Spring indisponível e cache de zonas ausente ou inválido | A inferência continua sem avaliar infrações por zona. Ausência de eventos não implica conformidade | Média | Conferir cadastro e conectividade antes da demonstração. Verificar avisos de cache nos logs. Não apresentar uma sessão sem zonas como monitoramento de infrações validado. |
| L03 | H2 em memória, com `ddl-auto=create-drop` | Zonas, eventos e revisões não sobrevivem ao reinício do Spring | Alta para produção | Tratar persistência definitiva com a frente de backend. A fila SQLite reenvia itens pendentes, não restaura eventos já confirmados. |
| L04 | Pipeline completo em CPU: 3,88 e 4,43 FPS nos dois trechos públicos medidos | Capacidade de processamento limitada; não demonstra desempenho sustentado em câmera ao vivo ou múltiplas fontes | Média | Medir no hardware do laboratório, em execuções representativas. Avaliar otimizações somente após as medições. |
| L05 | Serviços sem autenticação, autorização por perfil e identificação do revisor | Exposição pública inadequada; ausência de controle de acesso às operações e evidências | Alta para produção | Manter em loopback e com dados autorizados. Definir autenticação, perfis e política de retenção/acesso antes de implantação operacional. |
| L06 | Webcam física e transmissão de câmera RTSP ainda não validadas | Não há comprovação de funcionamento com o equipamento, rede e condições reais de captura | Média | Executar o roteiro com a equipe no laboratório, registrando conexão, FPS, latência, interrupção, reconexão e encerramento. |
| L07 | T17 parcial: avaliação empírica de estados e eventos e calibração pendentes | A qualidade dos alertas e os limiares não estão validados com verdade de referência | Alta para validação científica | Anotar clipes, medir estados e eventos, calibrar um parâmetro por vez e registrar antes/depois. |

## Condições de interpretação

- As zonas são carregadas novamente quando a fonte reconecta. Não há atualização
  periódica das regras durante uma sessão ativa.
- Se o Spring responde com sucesso com lista vazia, a lista vazia é válida e
  atualiza o cache; se a consulta falha, o cache disponível pode ser usado. Sem
  uma lista válida, não há avaliação de regras por zona.
- Os valores de FPS foram registrados em CPU, em trechos públicos de três
  segundos, sem descarte, com vídeo anotado e sem zonas ou envio HTTP. Não são
  metas de aceitação nem medições de operação portuária contínua.
- Testes de software e reconexão em loopback não substituem teste de câmera física.
- O recall de detecções por classe do modelo de EPI não equivale ao recall dos
  eventos do pipeline. Ausência de detecção não prova ausência física de EPI.
- A interface de operações ainda é demonstrativa. A integração por imagem está
  disponível, mas gestão de zonas, revisão real de eventos e streaming não estão
  integrados ao painel do frontend.

## Validação com a equipe

Usar o [roteiro manual](ROTEIRO_TESTES_VC.md) e registrar as condições de execução
em [AVALIACAO_VC.md](AVALIACAO_VC.md). Os testes devem incluir a atualização de
zonas após reiniciar uma fonte, indisponibilidade do Spring com e sem cache,
recuperação da fila, webcam física e câmera RTSP. Utilizar dados autorizados e
um ambiente de teste, sem interromper serviços operacionais.

Para concluir T17, fornecer os CSVs de rótulos de estados e eventos descritos
em [AVALIACAO_VC.md](AVALIACAO_VC.md). Medir acerto de estado por track, oscilação,
precisão e recall de eventos, atraso de alerta, falsos alarmes por hora, FPS,
latência e reconexão. Separar dados públicos e de laboratório. As metas de
aceitação continuam a definir com a equipe.

## Aprovações e pendências de escopo

- D1–D7: implementação local experimental realizada; aceite coletivo pendente.
- D8: confirmação das licenças do modelo e do dataset pelo orientador.
- T16: alteração local realizada; aceite formal da frente de frontend pendente.
- T17: scripts disponíveis; avaliação com rótulos reais e calibração pendentes.
- Persistência definitiva, autenticação, perfis, identificação do revisor,
  retenção de evidências e vínculo manual com trabalhador: alinhar com as frentes
  responsáveis antes de ampliar o escopo.

Referências internas: [README](../README.md), [contrato IA–backend](contrato-ia-backend.md),
[acompanhamento T01–T18](ACOMPANHAMENTO_VC.md), [zonas](ZONAS.md),
`backend/fastapi/vision/service.py`, `backend/fastapi/vision/spring_client.py` e
`backend/backend-springboot/src/main/resources/application.properties`.

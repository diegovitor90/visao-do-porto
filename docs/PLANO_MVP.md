# Visão do Porto: plano do MVP

Revisão 2, 12/11/2026. Planejamento corrigido a partir do documento de requisitos v1.0 (26/10) e da ata de 28/10. Código do protótipo ainda precisa ser disponibilizado; todas as entregas técnicas abaixo estão abertas.

## Escopo e evolução registrada

O núcleo do MVP inclui câmera, pessoas, capacete e colete, associação pessoa–EPI, zonas configuráveis, regras, persistência temporal, alertas com evidência, revisão e histórico. O plano anterior colocou EPIs para depois indevidamente; esta revisão corrige essa omissão.

A ata tratava identificação/autorização/treinamento como ampliação a deliberar. Em 12/11, Diego solicitou o diferencial ByteTrack + vínculo cadastral + treinamento. Essa evolução entra no piloto com dados fictícios e confirmação manual, sem atribuir à ata uma decisão que ela não registrou. Não houve validação coletiva documentada dessas novas escolhas.

O primeiro piloto será em uma câmera fixa no laboratório, uma zona e regras de exemplo explicitamente identificadas. Treinamento válido é um requisito possível, não sinônimo de autorização. ByteTrack mantém trajetórias, não comprova identidade civil. O piloto apoia revisão humana e não controla máquinas ou libera acesso físico automaticamente.

## Entregas e dependências

| Ordem | Entrega | Frente de referência |
| --- | --- | --- |
| 1 | [fechar regras, governança e critérios de aceite ](https://github.com/diegovitor90/visao-do-porto/issues/2) | Hugo como referência de governança; composição e validação operacional a confirmar. |
| 2 | [conectar câmera e detectar pessoas com ByteTrack ](https://github.com/diegovitor90/visao-do-porto/issues/3) | IA a definir; Diego na integração; Jason no painel. |
| 3 | [detectar capacete/colete e associar EPI à pessoa ](https://github.com/diegovitor90/visao-do-porto/issues/4) | IA a definir; Diego recebe observações; Jason exibe estados. |
| 4 | [editar zonas e aplicar regras com persistência temporal ](https://github.com/diegovitor90/visao-do-porto/issues/5) | Jason: editor; Diego: regras e eventos; Hugo: fontes. |
| 5 | [vincular trajetória ao cadastro e consultar treinamentos ](https://github.com/diegovitor90/visao-do-porto/issues/6) | Diego: cadastro/regras; Jason: confirmação visual; Hugo: registros fictícios. |
| 6 | [painel, evidências, revisão e histórico de alertas ](https://github.com/diegovitor90/visao-do-porto/issues/7) | Jason: interface; Diego: API/persistência; Hugo: critérios de revisão. |
| 7 | [preparar dados e executar teste integrado no laboratório ](https://github.com/diegovitor90/visao-do-porto/issues/8) | IA a definir; todas as frentes; Hugo consolida critérios. |

A tarefa [#1](https://github.com/diegovitor90/visao-do-porto/issues/1) acompanha o conjunto. Governança e plano de avaliação começam junto com câmera/rastreamento. EPIs e editor de zonas podem avançar em paralelo com contrato comum. Vínculo de treinamento depende da trajetória e das regras; integração final depende de todas as frentes. Responsável por IA e prazos permanecem a confirmar.

## Arquitetura e contratos mínimos

Captura -> detecção de pessoas/EPIs -> ByteTrack e associação pessoa–EPI -> zona/contexto cadastrado -> regras e persistência -> evento -> painel/revisão/histórico.

O cadastro e o vínculo manual alimentam a consulta de treinamento quando exigida pela zona, sem impedir a observação anônima de EPIs.

- IA para back-end: camera_id, session_id, timestamp, frame_id, track_id, bbox, classe/confiança, EPIs associados/confiança e qualidade da observação.
- Regras: zone_id, geometria e resolução de referência, contexto, atividade, condição ativa, EPIs/treinamentos exigidos, origem, item, versão e validação.
- Vínculo: worker_id fictício separado da chave camera_id + session_id + track_id, operador confirmador, horário e estado da associação.
- Evento para painel: event_id, início/fim, zona, câmera, tipo, regra/versão, motivo, evidência, revisão e autor/data da revisão.
- Estados separados: EPI detectado/possível ausência/indeterminado; identidade confirmada/não confirmada; treinamento válido/vencido/ausente/não verificado; permissão conforme regra.

Não transformar confiança de detecção em confiança de identidade. Perda/reinício ou dúvida no vínculo exige nova confirmação. Trocas silenciosas de ID precisam ser medidas. Não detectar EPI em uma observação ruim não prova ausência. Falha de câmera deve gerar estado técnico, sem conservar o último resultado como atual.

## Aceite do conjunto

- Câmera conectada, timestamps, detecções e IDs visíveis; queda e recuperação demonstradas.
- Capacete e colete associados à pessoa, incluindo exemplos próximos/ocultos.
- Zona desenhada na imagem, editável/desativável e recalibrável; contexto cadastrado, sem VLM.
- Verificação em dois níveis (presença e adequação à zona), evidência insuficiente e persistência configurável.
- Evento sem duplicação por quadro, com evidência, origem/versionamento da regra e explicação em português.
- Operador confirma/descarta e consulta histórico por filtros, sob autenticação/perfis.
- Cadastro fictício vinculado manualmente à trajetória; estados de treinamento e perda do vínculo demonstrados separadamente da permissão.
- Metas numéricas, dados de referência, condições do teste e resultados documentados; avaliar também ocorrências não alertadas.

Critérios detalhados estão nas tarefas. Não marcar o MVP concluído só porque os documentos ou telas existem.

## Ciclo de desenvolvimento e avaliação

Seguir o guia Ultralytics como orientação: objetivos, dados, preparação, solução inicial, avaliação, teste, implantação e acompanhamento. Começar com modelos pré-treinados; ajustar/treinar somente se a avaliação justificar. O treinamento profissional do trabalhador vem de registros verificados e não do modelo visual.

Gravar sequências autorizadas e anotar pessoas, EPIs, trajetórias e eventos. Separar sessões inteiras para ajuste e teste, evitando quadros vizinhos em conjuntos diferentes. Se houver treino, dividir antes do aumento de dados. Não usar o teste reservado para ajustar parâmetros.

Medir precisão/recall por classe e evento, falsos alarmes por período, eventos perdidos, trocas de ID, erros de associação EPI/pessoa e cadastro/trajetória, FPS e latência incluindo p95. Explicitar denominadores, hardware, versões e parâmetros. Metas numéricas devem ser acordadas após a medição inicial e antes do aceite. Avaliação em laboratório não comprova desempenho portuário.

## Governança e segurança dos dados

Definir fontes/versões das regras, matriz de permissões, retenção, proteção e descarte. Considerar as propostas de Isabelle sobre procedimentos do Itaqui, qualidade da imagem e técnico de segurança, distinguindo sugestão de decisão validada. Conferir as fontes normativas vigentes antes de converter requisitos em obrigações legais.

Cadastros do piloto são fictícios. Não versionar senhas RTSP, imagens identificáveis, documentos ou certificados reais no Git. Verificar licenças de código, modelos e datasets antes da incorporação.

## Fora deste incremento

EPIs especializados, VLM, reconhecimento facial, leitura automatizada de QR, reidentificação entre câmeras, integração real com bases institucionais, relatórios agregados RF22, contêineres, quedas e execução em borda RNF19. Escala física multicâmera e avaliação em condições portuárias são evoluções; testar isolamento de falha com fontes simuladas no piloto.

## Organização e encaminhamentos

Estrutura sugerida: src/vision, src/registry, src/rules, src/api, configs, tests e docs. Adaptar ao código existente quando disponibilizado. Jason é referência de front-end, Diego de back-end, Hugo de governança; IA e composição das equipes ainda precisam de definição.

Entregas de 30/10 e verificação da atividade VLI foram informadas como concluídas por Diego. Compartilhamento das visitas, nova visita, frequência das reuniões, sigla LDL e disponibilidade de bases permanecem a confirmar. O prazo 11/11 é histórico; novo prazo de demonstração deve ser combinado sem presumir conclusão. Manter escrita dos artigos em paralelo.

## Referências e rastreabilidade

- [Matriz completa: RF01–RF22, RNF01–RNF19 e ata](RASTREABILIDADE.md).
- Documento de Requisitos Sistema de Visão Computacional para Segurança Portuária, v1.0, 26/10/2026, fornecido por Diego.
- Ata_VC_UNDB_28-10-2026(1).docx, fornecida por Diego, incluindo complemento de arquitetura.
- https://docs.ultralytics.com/pt/guides/steps-of-a-cv-project/
- https://github.com/FoundationVision/ByteTrack
- Arquitetura indicada: https://excalidraw.com/#json=bfOGqeFUAc2f7SfcG8_Iw,YeRc1H65m6-Lo3VBv4mUnQ

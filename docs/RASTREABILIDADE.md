# Rastreabilidade de requisitos e decisões

Revisão de planejamento em 12/11/2026. Fontes lidas: Documento de Requisitos de Software v1.0, 26/10/2026 (11 páginas), e Ata VC UNDB de 28/10/2026, incluindo seu complemento de arquitetura. Os originais não foram alterados. A cobertura abaixo indica tarefas planejadas, não requisitos implementados.

## Requisitos funcionais

| IDs | Tratamento no MVP | Tarefa |
| --- | --- | --- |
| RF01 | Uma câmera física no piloto; múltiplas fontes e isolamento testados inicialmente por simulação. Expansão física posterior. | #3 |
| RF02–RF03 | Processamento, detecção de pessoas e medição de desempenho. | #3, #8 |
| RF04 | Capacete e colete no MVP; EPIs especializados adiados conforme ata. | #4 |
| RF05 | Associação pessoa–EPI, incluindo proximidade. | #4 |
| RF06 | Contexto cadastrado por câmera/zona; reconhecimento automático de cena adiado conforme ata. | #5 |
| RF07–RF09 | Editor de polígonos, EPIs por zona e cadastro/editabilidade de regras. | #5 |
| RF10 | Verificação de EPI por pessoa. | #4 |
| RF11–RF12 | Adequação à zona e presença/intrusão contextual. | #5 |
| RF13 | Fora do recorte apresentado em outubro; inclusão limitada agora a vínculo manual e dados fictícios, por orientação de Diego. | #6 |
| RF14 | Regras com origem/versão e subconjunto validado. | #2, #5 |
| RF15–RF16 | Persistência temporal, deduplicação, oclusão e indeterminado. | #5 |
| RF17–RF19 | Alertas, evidências e explicação. | #7 |
| RF20 | Revisão auditável; indicador de alertas descartados sem confundir com taxa baseada em referência independente. | #7, #8 |
| RF21 | Histórico com filtros. | #7 |
| RF22 | Relatórios agregados fora do MVP, conforme ata; medições de teste não equivalem a implementar BI completo. | Posterior |

## Requisitos não funcionais

| IDs | Tratamento | Tarefa |
| --- | --- | --- |
| RNF01–RNF02 | Metas antes do aceite; medição inicial de FPS e latência no hardware disponível. | #2, #3, #8 |
| RNF03 | Modularidade no início; escalabilidade multicâmera medida em etapa posterior. | #3, #8 |
| RNF04 | Precisão/recall de pessoas, capacete/colete e eventos no laboratório; validação portuária ainda pendente. | #2, #4, #8 |
| RNF05–RNF06 | Baixa luz/oclusão e falsos alarmes no piloto; condições ambientais do porto requerem avaliação posterior. | #3, #4, #8 |
| RNF07 | Pequenos EPIs especializados adiados; documentar limite de observação de capacete/colete no piloto. | #4, #8 |
| RNF08–RNF09 | Rastreabilidade e versão das regras. | #2, #5, #7 |
| RNF10–RNF11 | Editor visual e mensagens em português. | #5, #7 |
| RNF12–RNF14 | Autenticação, perfis, proteção, finalidade, retenção e descarte; identidade limitada a cadastros fictícios. | #2, #6, #7 |
| RNF15–RNF16 | Módulos separados, configuração e recalibração após mudar câmera. | #3, #5, #8 |
| RNF17 | Dados e avaliação reprodutíveis agora; coleta/validação portuária futura. | #8 |
| RNF18 | Falha/reconexão; isolamento com fonte simulada; operação contínua ainda a avaliar. | #3, #8 |
| RNF19 | Piloto em computador do laboratório; processamento em borda adiado conforme ata. | Posterior |

## Decisões, propostas e encaminhamentos da ata

| Registro | Tratamento atual |
| --- | --- |
| Pessoas, capacete e colete; contexto cadastrado | Restaurado como núcleo do MVP (#3–#5). |
| Laboratório da UNDB | Ambiente de demonstração #8; sem alegar validação no porto. |
| Diego back-end, Jason front-end, Hugo governança | Referências preservadas; responsáveis individuais/prazos e IA a confirmar em #2. |
| Contratos IA/back-end/front-end | Campos mínimos no plano; especificação e integração #3, #5 e #7. |
| Regras Itaqui, qualidade de imagem, técnico de segurança | Contribuições de Isabelle transformadas em tarefas de especificação/validação #2–#3 e implementação conforme decisões. Não apresentadas como já validadas. |
| Face ID, QR, autorização e treinamento | Ideias da ata. Atualização de Diego inclui treinamento e vínculo manual no piloto (#6); demais meios de identificação continuam posteriores. |
| CCO libera 10 e câmera conta 12; locais sem catraca | Oportunidade futura, não identificação de pessoas não autorizadas. Comparação exige mesma área/instante e controle de saídas/oclusão. |
| SharePoint, Power BI, integração institucional | Não há acesso confirmado; usar dados fictícios no primeiro piloto. |
| Mapa e polígono | Mapa geográfico não substitui zona na câmera; integração geográfica posterior. |
| Sigla LDL e procedimentos para entrada no silo | Confirmar com operação; não tratar relatos como inexistência comprovada de procedimentos. |
| Entregas de 30/10 e verificação da atividade VLI | Informadas como concluídas por Diego no histórico; isso não comprova presença na atividade ou código funcional no novo repositório. |
| Fotos/anotações de visitas e nova visita | Compartilhamento por Hugo e organização da visita ainda sem evidência de conclusão nesta conferência. |
| Reuniões rápidas | Horários/frequência e registro de impedimentos a combinar. |
| Piloto em 11/11 | Meta histórica da ata; não marcar como concluída nem reutilizar como prazo futuro. Novo prazo em #2. |
| Artigos em paralelo | Preservar produção acadêmica sem apresentar resultados do piloto antes de medidos. |

A ata é histórica. Esta revisão altera o planejamento do repositório, não reescreve deliberações do grupo. Não há alegação de aprovação coletiva das novas escolhas técnicas.

# Visão do Porto — Rastreabilidade de Requisitos e Decisões

**Revisão:** 12/11/2026  
**Natureza:** planejamento e mapeamento de cobertura; não é atestado de implementação ou aceite.  
**Fontes informadas:** Documento de Requisitos de Software v1.0 (26/10/2026, 11 páginas); Ata VC UNDB (28/10/2026), inclusive complemento de arquitetura; revisão de rastreabilidade de 12/11/2026.  
**Documento operacional:** `PLANO_DE_ACAO.md`.

> Os originais não são alterados por este documento. As descrições abaixo sintetizam o recorte informado na revisão, sem reproduzir integralmente a redação dos requisitos. Os identificadores #2–#8 devem ser conferidos com as Issues publicadas.

## 1. Convenções de acompanhamento

- **Planejado:** escopo definido, mas sem evidência de implementação.
- **Parcial:** parte demonstrada, sem cobertura integral do requisito.
- **Em validação:** código/fluxo existe, mas ainda requer critérios de aceite ou evidências.
- **Validado:** critérios de aceite atendidos e evidências revisadas.
- **Posterior:** explicitamente fora do MVP.

Não confundir **implementado**, **testado em laboratório** e **validado em ambiente portuário**. A existência de código, commit ou teste de unidade não comprova desempenho do sistema completo.

## 2. Requisitos funcionais

| IDs | Tratamento no MVP | Tarefa | Estado/evidência em 12/11 |
| --- | --- | --- | --- |
| RF01 | Uma câmera física no piloto; múltiplas fontes e isolamento testados inicialmente por simulação. Expansão física posterior. | #3 | Planejado; sem teste de câmera confirmado |
| RF02–RF03 | Processamento, detecção de pessoas e medição de desempenho. | #3, #8 | Planejado; métricas pendentes |
| RF04 | Capacete e colete no MVP; EPIs especializados adiados conforme ata. | #4 | Planejado |
| RF05 | Associação pessoa–EPI, incluindo proximidade. | #4 | Planejado |
| RF06 | Contexto cadastrado por câmera/zona; reconhecimento automático de cena adiado conforme ata. | #5 | Planejado |
| RF07–RF09 | Editor de polígonos, EPIs por zona e cadastro/editabilidade de regras. | #5 | Planejado |
| RF10 | Verificação de EPI por pessoa. | #4 | Planejado |
| RF11–RF12 | Adequação à zona e presença/intrusão contextual. | #5 | Planejado |
| RF13 | Fora do recorte apresentado em outubro; inclusão limitada agora a vínculo manual e dados fictícios, por orientação de Diego. | #6 | Parcial apenas na infraestrutura de cadastro; vínculo manual pendente |
| RF14 | Regras com origem/versão e subconjunto validado. | #2, #5 | Planejado |
| RF15–RF16 | Persistência temporal, deduplicação, oclusão e indeterminado. | #5 | Planejado |
| RF17–RF19 | Alertas, evidências e explicação. | #7 | Planejado |
| RF20 | Revisão auditável; indicador de alertas descartados sem confundir com taxa baseada em referência independente. | #7, #8 | Planejado |
| RF21 | Histórico com filtros. | #7 | Planejado |
| RF22 | Relatórios agregados fora do MVP, conforme ata; medições de teste não equivalem a implementar BI completo. | Posterior | Adiado |

## 3. Requisitos não funcionais

| IDs | Tratamento | Tarefa | Estado/evidência em 12/11 |
| --- | --- | --- | --- |
| RNF01–RNF02 | Metas antes do aceite; medição inicial de FPS e latência no hardware disponível. | #2, #3, #8 | Metas e medições pendentes |
| RNF03 | Modularidade no início; escalabilidade multicâmera medida em etapa posterior. | #3, #8 | Estrutura modular inicial; escalabilidade não validada |
| RNF04 | Precisão/recall de pessoas, capacete/colete e eventos no laboratório; validação portuária ainda pendente. | #2, #4, #8 | Planejado |
| RNF05–RNF06 | Baixa luz/oclusão e falsos alarmes no piloto; condições ambientais do porto requerem avaliação posterior. | #3, #4, #8 | Planejado |
| RNF07 | Pequenos EPIs especializados adiados; documentar limite de observação de capacete/colete no piloto. | #4, #8 | Planejado |
| RNF08–RNF09 | Rastreabilidade e versão das regras. | #2, #5, #7 | Planejado |
| RNF10–RNF11 | Editor visual e mensagens em português. | #5, #7 | Planejado |
| RNF12–RNF14 | Autenticação, perfis, proteção, finalidade, retenção e descarte; identidade limitada a cadastros fictícios. | #2, #6, #7 | Planejado; não presumir segurança pronta |
| RNF15–RNF16 | Módulos separados, configuração e recalibração após mudar câmera. | #3, #5, #8 | Separação estrutural inicial; integração/recalibração pendentes |
| RNF17 | Dados e avaliação reprodutíveis agora; coleta/validação portuária futura. | #8 | Planejado |
| RNF18 | Falha/reconexão; isolamento com fonte simulada; operação contínua ainda a avaliar. | #3, #8 | Planejado |
| RNF19 | Piloto em computador do laboratório; processamento em borda adiado conforme ata. | Posterior | Laboratório previsto; borda adiada |

## 4. Decisões, propostas e encaminhamentos da ata

| Registro | Tratamento atual | Natureza |
| --- | --- | --- |
| Pessoas, capacete e colete; contexto cadastrado | Núcleo do MVP (#3–#5). | Escopo retomado |
| Laboratório da UNDB | Ambiente de demonstração #8; sem alegar validação no porto. | Planejamento |
| Diego back-end, Jason front-end, Hugo governança | Histórico preservado; composição atual e quatro líderes abaixo. Executores e prazos a combinar em #2. | Histórico + atualização |
| Contratos IA/back-end/front-end | Campos mínimos propostos; especificação e integração em #2, #3, #5 e #7. | Pendente de validação |
| Regras Itaqui, qualidade de imagem, técnico de segurança | Contribuições de Isabelle transformadas em especificação/validação #2–#3 e implementação conforme decisões. | Encaminhamento |
| Face ID, QR, autorização e treinamento | Ideias da ata; treinamento e vínculo manual limitados ao piloto (#6); demais formas de identificação posteriores. | Recorte proposto |
| CCO libera 10 e câmera conta 12; locais sem catraca | Oportunidade futura, não identificação de pessoas não autorizadas. Comparação exige mesma área/instante e controle de saídas/oclusão. | Futuro |
| SharePoint, Power BI, integração institucional | Sem acesso confirmado; dados fictícios no primeiro piloto. | Futuro |
| Mapa e polígono | Mapa geográfico não substitui zona desenhada na imagem da câmera; integração geográfica posterior. | Distinção técnica |
| Sigla LDL e procedimentos para entrada no silo | Confirmar com operação; relatos não provam inexistência de procedimentos. | Verificação pendente |
| Entregas de 30/10 e atividade VLI | Informadas como concluídas por Diego no histórico; não comprovam presença nem código funcional no novo repositório. | Histórico não verificado |
| Fotos/anotações de visitas e nova visita | Compartilhamento por Hugo e organização da visita sem evidência de conclusão nesta conferência. | Pendente de evidência |
| Reuniões rápidas | Horários/frequência e impedimentos a combinar. | Pendente |
| Piloto em 11/11 | Meta histórica da ata; não marcar como concluído nem reutilizar como prazo futuro. Novo prazo em #2. | Prazo histórico |
| Artigos em paralelo | Produção acadêmica preservada sem apresentar resultados do piloto antes de medidos. | Diretriz |

A ata permanece **histórica**. A revisão altera o planejamento do repositório, sem reescrever deliberações ou alegar aprovação coletiva das novas escolhas.

## 5. Registro de decisões arquiteturais (propostas e estado)

| ID | Decisão/hipótese | Motivo e limite | Estado |
| --- | --- | --- | --- |
| DA-01 | Spring Boot para cadastros, regras e auditoria | Separar lógica administrativa de inferência | Estrutura e cadastro inicial implementados |
| DA-02 | FastAPI para visão computacional | Isolar processamento e eventos | Estrutura inicial; pipeline não comprovado |
| DA-03 | H2 no desenvolvimento; PostgreSQL posteriormente | Testes locais e futura persistência durável | H2 em uso; migração proposta |
| DA-04 | Detecção/trajetória ≠ identidade pessoal | Evitar atribuição indevida de identidade por track | Princípio arquitetural |
| DA-05 | Vínculo manual com dados fictícios no piloto | Limitar risco e escopo de RF13 | Proposto; implementação pendente |
| DA-06 | Regras por zona versionadas | Permitir explicação e auditoria | Proposto |
| DA-07 | Revisão humana de alertas | Tratar indeterminação e evitar conclusões automáticas | Proposto |
| DA-08 | Uma câmera física + fontes simuladas | Escopo laboratorial controlado | Proposto |

Decisões ainda não aprovadas devem ser revisadas pelos líderes e registradas com data e responsável quando formalizadas.

## 6. Equipes e lideranças

Composição conforme a planilha de atribuições enviada por Diego; lideranças informadas em 12/11/2026.

| Frente | Líder | Integrantes |
| --- | --- | --- |
| Requisitos, Gestão e BI | Hugo Diniz | Victor Santos, Hugo Diniz e Isabelle Rodrigues |
| Front-end e UX | Jason Araujo | Luiza, Victor Santos e Jason Araujo |
| Back-end | Diego Souza | Diego Souza e Sophia |
| IA e Visão Computacional | Gustavo Sousa | Isabelle Rodrigues, Gustavo Sousa e Micaelle Susy |

Liderança não define automaticamente executor de subtarefa. Distribuição individual, prazos e contas GitHub dos demais integrantes ainda precisam ser confirmados.

## 7. Evidências técnicas conhecidas e lacunas

| Evidência conhecida | O que sustenta | O que **não** sustenta |
| --- | --- | --- |
| Commit `d685999` em `feature/backend-diego` | Estrutura inicial Spring Boot/FastAPI | IA em operação, integração ponta a ponta |
| Commit `a6e22c4` em `feature/backend-diego` | Cadastro inicial de trabalhadores, JPA e testes | Capacitações, controle de zonas ou RF13 completo |
| Testes Maven relatados como aprovados | Validação automatizada inicial do backend | Aceite do MVP, desempenho de vídeo ou validação portuária |
| `git push` e branch sincronizada informados | Entrega enviada à branch remota | Merge à `main` confirmado |

**Pendências técnicas imediatas:** conferir estado do merge/PR; verificar arquivo não rastreado `src/main/java/.../repository/TrabalhadorService.java` antes de remover; manter relatório local `erros-maven.txt` fora do versionamento; definir contratos, testes e evidências de cada Issue.

## 8. Matriz de evidência a preencher por requisito

Para cada RF/RNF, registrar ao longo da execução:

- **Issue e responsável confirmado** (não inferir apenas pela liderança).
- **Branch, Pull Request e commit** associados.
- **Cenário e procedimento de teste**, dataset/hardware/versões quando aplicável.
- **Resultado e evidência verificável** (log, teste, vídeo, captura, relatório).
- **Ambiente da evidência:** desenvolvimento, laboratório UNDB ou porto.
- **Decisão de aceite:** responsável, data e pendências.

Não substituir métricas independentes por quantidade de alertas descartados em revisão humana. Não declarar validação em ambiente portuário com base em testes de laboratório.

## 9. Histórico

- **26/10/2026:** Documento de Requisitos v1.0 — referência histórica.
- **28/10/2026:** Ata VC UNDB e complemento — referência histórica.
- **12/11/2026:** revisão de rastreabilidade e proposta de arquitetura/execução, sem alterar fontes originais nem registrar aprovação coletiva.

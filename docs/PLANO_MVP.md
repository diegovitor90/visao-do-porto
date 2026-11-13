# Visão do Porto — Plano de Ação do MVP

**Revisão:** 12/11/2026  
**Estado:** Proposta de planejamento técnico, sujeita a alinhamento e aprovação coletiva.  
**Fontes de referência:** Documento de Requisitos de Software v1.0 (26/10/2026, 11 páginas); Ata VC UNDB (28/10/2026) e complemento de arquitetura; revisão de rastreabilidade de 12/11/2026.  
**Documento complementar:** `RASTREABILIDADE.md`.

> Este plano organiza entregas previstas; não comprova implementação, aceite coletivo ou validação em ambiente portuário. Os números #2–#8 são identificadores usados no planejamento e devem ser conferidos com as Issues reais do GitHub.

## 1. Objetivo e recorte do MVP

Demonstrar, em **laboratório da UNDB**, um fluxo de segurança assistida por visão computacional que detecta pessoas e EPIs básicos (capacete e colete), acompanha trajetórias, interpreta zonas configuradas, aplica regras e produz alertas com evidências revisáveis.

**Núcleo do MVP:** captura de uma câmera física; simulação de múltiplas fontes; detecção e rastreamento de pessoas; capacete e colete; associação pessoa–EPI; editor de polígonos; contexto e EPIs exigidos por zona; persistência temporal, deduplicação, oclusão/indeterminação; alertas, evidências, explicação, revisão e histórico.

**Suporte administrativo limitado:** cadastro fictício de trabalhadores, capacitações e vínculo manual com eventos, sem pressupor identificação biométrica ou automática de pessoas.

**Fora do MVP:** EPIs especializados; reconhecimento automático de cena; reconhecimento facial/Face ID; implantação física multicâmera; integrações institucionais com SharePoint/Power BI/CCO; BI agregado completo; processamento em borda; validação operacional no porto. QR/RFID e outras formas de identificação permanecem propostas futuras, não requisitos implementados no piloto.

## 2. Arquitetura e fronteiras

- **Spring Boot (Java):** API administrativa, cadastros, capacitações, regras de autorização, histórico, auditoria e integração.
- **FastAPI (Python):** serviços de inferência e eventos de visão computacional; detecção e rastreamento são distintos de identificação pessoal.
- **Frontend:** configuração de zonas, acompanhamento de alertas, revisão humana e consulta ao histórico.
- **Persistência:** H2 apenas no desenvolvimento inicial; PostgreSQL é evolução proposta, com migrações e contratos a definir.
- **Identidade:** credencial/cadastro fornece identidade administrativa; trajetória visual não identifica automaticamente um trabalhador. Vínculos no piloto serão manuais e com dados fictícios.
- **Governança:** autenticação, perfis, finalidade, retenção, descarte, versionamento de regras e trilha de auditoria devem ser definidos antes do aceite.

**Contrato mínimo a especificar em #2 e validar na integração:** `event_id`, `camera_id`, `zone_id`, `timestamp`, `event_type`, `track_id` (efêmero), `rule_id`, `rule_version`, `confidence` (quando aplicável), `evidence_ref`, `review_status`. Campos, tipos, valores e responsabilidades são **proposta**, não contrato aprovado. Evitar colocar identidade pessoal diretamente no evento de inferência.

## 3. Equipes

| Frente | Liderança informada | Integrantes informados |
| --- | --- | --- |
| Requisitos, Gestão e BI | Hugo Diniz | Victor Santos, Hugo Diniz, Isabelle Rodrigues |
| Front-end e UX | Jason Araujo | Luiza, Victor Santos, Jason Araujo |
| Back-end | Diego Souza | Diego Souza, Sophia |
| IA e Visão Computacional | Gustavo Sousa | Isabelle Rodrigues, Gustavo Sousa, Micaelle Susy |

Liderança não implica atribuição automática de cada subtarefa. Responsáveis individuais, datas e contas GitHub para `Assignees` ainda precisam ser confirmados.

## 4. Entregas por tarefa

### #2 — Escopo, contratos, critérios de aceite e governança

**Frente principal:** Requisitos/Gestão, com líderes técnicos.  
**Situação:** Pendente de alinhamento coletivo.

- [ ] Validar o recorte do MVP, o ambiente do laboratório e as exclusões.
- [ ] Confirmar regras de segurança, critérios de zonas e requisitos de EPI com especialista operacional; não presumir procedimentos do Porto do Itaqui.
- [ ] Especificar contratos IA ↔ backend ↔ frontend, versões, tratamento de erros e indeterminação.
- [ ] Definir metas de FPS, latência, precisão/recall, falsos alarmes e critérios de aceite antes dos testes.
- [ ] Definir perfis, autenticação, retenção, finalidade, descarte e auditoria.
- [ ] Atribuir executores, prazos, frequência das reuniões e registro de impedimentos.

**Aceite:** decisões registradas, contratos revisados pelas frentes e critérios mensuráveis publicados.

### #3 — Fontes de vídeo, detecção e rastreamento

**Frente principal:** IA/VC.  
**Situação:** Planejado; a existência da estrutura FastAPI não comprova pipeline funcional.

- [ ] Integrar uma câmera física no laboratório e fontes simuladas independentes.
- [ ] Detectar pessoas e produzir `track_id` temporal, sem equipará-lo a identidade pessoal.
- [ ] Medir FPS, latência, falhas de fonte, reconexão e isolamento.
- [ ] Documentar condições de iluminação, oclusão e limitações do hardware.

**Aceite:** demonstração reproduzível e medições com configuração/hardware registrados.

### #4 — EPIs básicos e associação pessoa–EPI

**Frente principal:** IA/VC.  
**Situação:** Planejado.

- [ ] Detectar capacete e colete.
- [ ] Associar EPIs a pessoas com regra de proximidade e limites de confiança.
- [ ] Tratar ausência, incerteza e oclusão sem gerar conclusão indevida.
- [ ] Medir precisão/recall e erros de associação em conjunto de teste documentado.

**Aceite:** cenários positivos, negativos e indeterminados demonstrados com métricas e evidências.

### #5 — Zonas, polígonos e motor de regras

**Frentes:** IA/VC, backend e frontend.  
**Situação:** Planejado.

- [ ] Editor visual de polígonos por câmera; contexto de zona cadastrado manualmente.
- [ ] Cadastro/editabilidade dos EPIs exigidos e regras por zona, com origem e versão.
- [ ] Verificação de presença/intrusão e adequação de EPI por pessoa/zona.
- [ ] Persistência temporal, deduplicação de eventos e tratamento de oclusão/indeterminação.
- [ ] Definir recalibração de polígonos após alteração de câmera.

**Aceite:** cenários controlados com rastreabilidade da regra acionada e eventos sem duplicação indevida.

### #6 — Cadastro, capacitações e vínculo manual

**Frente:** Backend (Diego e Sophia; divisão individual a combinar).  
**Situação:** **Parcialmente implementado** na branch `feature/backend-diego`.

**Já demonstrado em desenvolvimento:** entidade e repositório de trabalhador; cadastro, listagem e consulta; rejeição de matrícula duplicada; testes automatizados passando; commit `a6e22c4`. Isso **não** comprova integração à `main` nem conclusão de RF13.

- [x] Cadastro básico de trabalhadores fictícios com JPA/H2.
- [x] Endpoints iniciais de cadastro, listagem e consulta.
- [x] Regra inicial de matrícula única e testes de serviço.
- [ ] Revisar o Pull Request/merge e resolver arquivo `TrabalhadorService.java` não rastreado em `repository`.
- [ ] Especificar e implementar capacitações, validade e vínculo trabalhador–capacitação.
- [ ] Definir requisitos de treinamento por atividade/zona, com decisões registradas.
- [ ] Implementar vínculo **manual e auditável** entre cadastro fictício e evento, sem inferir identidade pela trajetória.
- [ ] Adicionar validações, testes, documentação de API e tratamento de erros consistente.

**Aceite:** cenários de capacitação válida, vencida, ausente e vínculo manual revisável; sem alegar reconhecimento pessoal automático.

### #7 — Alertas, evidências, revisão e histórico

**Frentes:** Backend e frontend, com IA/VC.  
**Situação:** Planejado.

- [ ] Registrar alertas com regra, versão, zona, câmera, instante e explicação em português.
- [ ] Vincular evidências de forma controlada, com política de acesso/retenção.
- [ ] Disponibilizar revisão humana auditável (confirmar, descartar, indeterminado).
- [ ] Histórico pesquisável com filtros; indicadores de alertas descartados sem chamar isso de taxa de falso positivo validada.

**Aceite:** trilha reproduzível do evento à revisão, com filtros e permissões testados.

### #8 — Integração, medição e demonstração

**Frentes:** Todas.  
**Situação:** Planejado; o prazo histórico de 11/11 não é evidência de piloto realizado.

- [ ] Integrar câmera → IA/VC → backend → frontend → revisão.
- [ ] Executar cenários de teste e registrar dados, versões, hardware e limitações.
- [ ] Medir FPS, latência, precisão/recall, erros de associação, alertas e falhas/reconexão.
- [ ] Separar resultados laboratoriais de qualquer alegação de validação portuária.
- [ ] Apresentar demonstração no laboratório da UNDB com critérios de aceite definidos em #2.

**Aceite:** roteiro demonstrável, relatório de métricas reprodutíveis e pendências explícitas.

## 5. Ordem e dependências

1. **Agora:** resolver pendências locais da entrega de trabalhadores; conferir merge/PR e atualizar o status real da branch.
2. **Antes de integrar:** fechar #2 (contratos, regras, aceite, responsáveis e cronograma).
3. **Em paralelo:** #3 e #4 pela IA/VC; capacitações da #6 pelo backend; desenho de UX de zonas/alertas pelo frontend.
4. **Integração incremental:** #5 → #7 → #8, sem bloquear testes isolados anteriores.
5. **Depois do piloto:** revisar expansão física, integrações institucionais, BI completo e identificação autorizada.

## 6. Gestão da execução no GitHub

Cada Issue deve indicar: objetivo, RF/RNF relacionados, responsável confirmado, dependências, checklist, critérios de aceite, branch/PR, evidências e estado (`Planejado`, `Em andamento`, `Em revisão`, `Validado`, `Adiado`). Uma tarefa só passa a `Validado` quando os critérios e evidências forem revisados. Usar Pull Requests para integração à `main`, conforme fluxo aprovado pela equipe.

**Pendências de coordenação:** confirmar composição/atribuições, prazos e reuniões; obter avaliação operacional de regras Itaqui e qualidade de imagem; confirmar registros de visita e material compartilhado por Hugo; verificar eventuais compromissos históricos sem convertê-los em implementação comprovada. Artigos acadêmicos podem seguir em paralelo, com resultados apenas após medição.

## 7. Histórico de revisão

- **26/10/2026:** Documento de Requisitos v1.0 (fonte histórica).
- **28/10/2026:** Ata VC UNDB e complemento de arquitetura (fonte histórica).
- **12/11/2026:** revisão proposta de plano, com foco em pessoas/EPI/zonas/alertas e suporte administrativo limitado; **não representa aprovação coletiva**.

## Atualização de implementação: 13/11/2026

O commit `a6e22c4` está na história da `main`, conferida no commit `8ea0b68`. O serviço de trabalhadores importado pelo controller estava ausente nas duas branches; esta entrega o completa. Na branch de revisão, o incremento da tarefa #6 implementa cadastro/listagem/consulta de capacitações fictícias, validade por data e estados distintos. Veja [CAPACITACOES.md](CAPACITACOES.md).

O cadastro visual, vínculo manual com trajetória, requisitos por zona, autenticação e integração com IA continuam pendentes. O [contrato de observação](contrato-ia-backend.md) é um rascunho; não representa endpoint implementado ou aprovação coletiva. Os checklists anteriores registram o estágio de 12/11 e não devem ser usados como evidência de aceite deste incremento.

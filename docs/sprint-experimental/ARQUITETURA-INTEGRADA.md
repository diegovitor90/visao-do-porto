# Arquitetura da integração experimental

A topologia segue o ADR-001 aprovado na revisão `9ec17c7` de `docs/arquitetura-v2`. O Spring Boot concentra o cadastro administrativo e as capacitações. O fluxo de vídeo e a inferência ficam nos serviços Python. A Vision API v0.3 com YOLO11n permanece disponível para análise de fotos. A proposta antiga de transportar mídia pelo Java, citada no README, no plano e no contrato histórico, foi superada pelo ADR. [ADR-001](https://github.com/diegovitor90/visao-do-porto/blob/9ec17c7e79629b12827b99418f0927b2387bad32/docs/arquitetura/adrs/ADR-001.adoc)

As decisões D1 e D2 registradas no handoff adotam a matrícula para sincronização administrativa e delimitam o piloto a capacete e colete. As decisões A, B, D e F registram as escolhas de usar o detector de EPI da Sophia, manter o frontend React/TypeScript existente, deixar o cadastro de câmeras e setores no Tracker durante o MVP e preservar a autoria da contribuição. A formalização nos ADRs 002–004 e a confirmação do motor de regras continuam pendentes. O rascunho serve de referência para a sprint. [Rascunho na branch de arquitetura](https://github.com/diegovitor90/visao-do-porto/blob/9ec17c7e79629b12827b99418f0927b2387bad32/docs/arquitetura/adrs/RASCUNHO-decisoes-v2.md)

## Inventário

Os contratos da Sophia abaixo foram inspecionados por leitura estática do ZIP. As rotas listadas dos serviços candidatos usam o prefixo `/api/v1`. Portas refletem o script de demo ou, no caso de Compliance, o README do módulo.

| Componente | Porta | Responsabilidade e interface | Estado |
| --- | --- | --- | --- |
| Spring Boot | 8080 | `GET /api/trabalhadores` e rotas administrativas de trabalhadores e capacitações | H2 em memória |
| Vision API v0.3 | 8000 atual, 8100 proposto para coexistência | `POST /api/v1/vision/analyze` com JPEG/PNG multipart, saída tipada de detecção de pessoa | YOLO11n local |
| React/Vite | 5173 | Interface oficial. Proxy de desenvolvimento usa `VISION_API_TARGET` para análise de fotos | Painel demonstrativo e revisão local na base da sprint |
| `epi_ppe` | 8000 | `POST /detect` e `POST /pipeline/process-frame`. Detecta, rastreia e associa EPIs a pessoas | Provider mock por padrão. O provider YOLO depende dos pesos ajustados |
| `epi_identity` | 8001 | `GET/POST /employees` e `PUT /employees/{id}`, com JWT/RBAC. Possui rotas de biometria montadas na mesma aplicação | SQLite por padrão. A execução requer um perfil estritamente administrativo |
| `epi_fusion` | 8002 | `POST /fusion/observations`, consultas por câmera, estado e observações anônimas. Consolida observações e condições de visibilidade | Estado temporal de processo, com expiração |
| `epi_rules` | 8003 | `POST /rules/evaluate`, versões e consultas de avaliação. Configura limiares, indeterminação e persistência temporal | Regras iniciais e estado de processo. Seleção final do motor pendente |
| `epi_incident` | 8004 | `POST /incidents/evaluations`, lista incidentes e permite resolvê-los. Usa chave de deduplicação para incidentes abertos | Repositório em memória e IDs sequenciais. Reiniciar perde o histórico |
| `epi_alerts` | 8005 | `GET /alerts`, resumo, sincronização e `POST /alerts/{id}/ack`. Agrega Fusion, Incident e Tracker | Alertas em memória. O reconhecimento de leitura não registra revisão motivada |
| `epi_tracker` | 8010, UI de referência 8020 | `/cameras`, `/areas`, `/trackers` e `/ppe`. Câmeras e setores fornecem contexto ao MVP | Cadastro de câmeras em `~/.epi_vision/cameras.json`. Outros dados e eventos usam estado de processo |
| `epi_integration` | — | Scripts para sincronizar trabalhadores, orquestrar mídia e iniciar a demonstração | Clientes HTTP e cache de execução. O runner de demo inclui reconhecimento simulado |
| `epi_compliance` | 8000 no README | `POST /compliance/evaluate`, estado e evidências. Motor alternativo | Fora da topologia mínima até decisão sobre sobreposição com Rules |

## Topologia mínima

- **Disponível na base da sprint:** navegador → Vite → Vision API v0.3 → YOLO11n, em paralelo ao cadastro administrativo do Spring.
- **Candidato para o piloto de EPI:** mídia autorizada → PPE → observação por câmera/track → Fusion → Rules versionadas → Incident → Alerts → React. O Tracker fornece contexto de câmera e setor. A revisão humana deve ter contrato próprio no servidor, vinculado ao identificador estável da ocorrência, com decisão, justificativa, responsável autenticado e horário. Para esse fluxo, começar por uma câmera e um processo de cada serviço.
- **Sincronização administrativa separada:** Spring → adaptador de leitura → Identity com rotas administrativas apenas. Matrícula é a chave de sincronização. A matrícula fica ausente no fluxo de câmera até eventual vínculo administrativo manual. A associação automática de pessoa a matrícula permanece fora do piloto.

Para coexistência, reservar 8000 ao PPE e executar a Vision API em 8100 usando `VISION_API_TARGET=http://127.0.0.1:8100` no frontend. Isso preserva o endpoint e o formato da v0.3. A matriz de portas é local. Os serviços experimentais devem permanecer em loopback, sem publicar as APIs administrativas ou operacionais do ZIP.

## Contratos e critérios de integração

**Cadastro e sincronização.** O consumidor do ZIP lê `GET /api/trabalhadores` como uma lista de objetos com `id`, `nome`, `matricula`, `empresa`, `ativo` e os opcionais `setor` e `cargo`. Mapeia `matricula` para `registration`, `nome` para `name`, `cargo` para `role_title` e `ativo=false` para `INACTIVE`. O setor usa códigos do domínio do Tracker. O sincronizador tenta conservar setor/cargo quando a origem não os informa, reportar setores desconhecidos, manter registros ausentes da origem e abortar sem gravar quando falha a leitura do Spring. Na criação, setor ausente ou desconhecido recai num valor padrão, e a criação já inativa usa duas chamadas. É preciso acordar a política desses casos antes de ativar a sincronização.

O cliente do ZIP redefine `list_employees` e a última implementação elimina a paginação. Uma sincronização cujo destino excede a primeira página pode tratar um registro existente como novo. O cliente de integração também gera um JWT privilegiado com segredo fixo de teste. Validar paginação, idempotência, falha parcial, status inativo na criação e credenciais de serviço de privilégio mínimo antes de habilitar o destino. Um contrato lido do Spring real evidencia o produtor administrativo. A sincronização requer verificar o destino real com dados exclusivamente fictícios.

**Eventos e regras.** Transportar identificadores de câmera e track, horário, tipo de EPI, visibilidade, confiança e versão da regra. Preservar estado indeterminado para observações insuficientes. A configuração-base do Rules usa zero segundos de persistência e desabilita avaliação anônima. O valor de três segundos é aplicado pelo ajuste do runner de demo. O piloto precisa de política explícita por câmera/track, configuração de persistência versionada e teste que cubra interrupção e recuperação. Nenhum resultado de regra deve acionar autorização de acesso físico. Incidentes e alertas em memória não atendem a um requisito de auditoria após reinício. Um identificador estável e deduplicação entre reinícios são pré-condições do contrato definitivo de revisão.

**Isolamento de biometria.** O módulo Identity monta os routers `biometrics` e `recognition` sempre. O pipeline chama o reconhecimento, e o runner geral registra identidade mock. O provider mock executa o caminho de identidade e, por isso, é insuficiente para isolamento. Antes de qualquer execução do pipeline candidato, o perfil autorizado precisa excluir esses routers e as chamadas de reconhecimento e enrollment. Os testes devem verificar ausência das rotas, ausência dessas chamadas no fluxo e continuidade de observações anônimas sem vincular matrículas.

## Evidência e limites

- ZIP inspecionado por leitura estática, SHA-256 `031311901cf253835b0f29f1f6b5d080892d959e425330bb366064e0237d45a0`. Evidência para rotas e configurações em `epi_*/app/{main,config}.py`, `app/api/` e no runner `epi_integration/scripts/start_demo.py`. A auditoria de sincronização leu `spring_client.py`, `worker_sync.py` e `identity_client.py`.
- O ZIP não contém `best.pt` nem outro arquivo `.pt`. O README descreve o detector e `docs/MODELO.md` atribui CC BY 4.0 aos datasets listados, sem licença verificável para o arquivo de pesos ausente. As métricas descritas ali são resultados atribuídos à autora. A identificação do commit de origem, a autorização de uso com atribuição e a verificação de peso, licença e hash ficam pendentes.
- O código da Sophia permanece no anexo. A revisão estática não valida integração em execução, conformidade temporal real, precisão de detecção, nem operação no Porto do Itaqui.

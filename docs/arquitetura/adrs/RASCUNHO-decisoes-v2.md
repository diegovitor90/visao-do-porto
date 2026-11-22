# Rascunho de decisões — arquitetura v2 (integração com o projeto da Sophia)

**Data:** 20/11/2026
**Decidido por:** Diego (líder do back-end), após conversa com a Sophia em 19/11/2026.
**Natureza:** rascunho de trabalho. Matéria-prima para os ADRs 002–004. Não é ADR aprovado
pela equipe e não comprova integração implementada.

## Contexto

A Sophia desenvolveu o projeto `epi-vision-porto-itaqui`: 9 serviços Python (ppe, identity,
fusion, rules, incident, alerts, tracker, compliance, integration) e um frontend React.
O ADR-001 continua válido: o Spring Boot é o núcleo administrativo e nenhum frame de vídeo
atravessa o Spring. As decisões abaixo completam o ADR-001; não o substituem.

## Decisões acordadas na conversa com a Sophia (19/11)

| ID | Decisão | Destino |
|---|---|---|
| D1 | Spring Boot é a base oficial do cadastro de trabalhadores: matrícula, nome, setor e cargo. O `epi_identity` sincroniza a partir do Spring (leitura). O elo entre os dois é a matrícula. Não manter dois cadastros administrativos. | ADR-002 |
| D2 | Escopo de EPI do MVP: capacete e colete. Luvas e botas ficam adiadas (retreino pronto em notebook, ainda não executado). Motivo: apresentação antes do fim do ano. | ADR-003 |

## Decisões tomadas por Diego na Tarefa 2 (20/11)

| ID | Decisão | Consequências | Destino |
|---|---|---|---|
| A | O `epi_ppe` da Sophia (`best.pt`, YOLOv8n ajustado) é o detector de EPI do MVP. | FastAPI v0.3.0 (YOLO11n) é preservado para a tela Analisar imagem e muda de porta (8000 → proposta 8100); ajustar `vite.config.ts` e README. Documentar local, versão e responsável pelo `best.pt`, que fica fora do Git. | ADR-004 |
| B | O frontend React + TypeScript do `visao-do-porto` é a tela oficial e passa a consumir as APIs da Sophia (alertas, fusion, tracker). | Trocar dados demonstrativos por APIs reais. Revisão humana com justificativa precisa de persistência no servidor (o `epi_alerts` só tem "visto"). Tela de Câmeras da Sophia fica como referência. | ADR-004 |
| D | Cadastro de câmeras e setores fica no Tracker da Sophia durante o MVP. | Dívida técnica registrada: o Spring pode assumir depois, com sincronizador semelhante ao de trabalhadores, sem mudar a tela. | ADR-004 / riscos |
| F | O código da Sophia entra no `visao-do-porto` pela branch `feature/integracao-sophia`. | Preservar autoria (commit feito pela Sophia ou importação com histórico). Uma única fonte da verdade após a integração. `.gitignore` para `best.pt`, `dist/bundle.js` e bancos SQLite antes do primeiro commit. | ADR-004 |

## Pendentes de confirmação com a Sophia

| ID | Pergunta | Indício no código |
|---|---|---|
| C | O MVP roda com reconhecimento facial desligado? | `epi_identity`: `EPI_FACE_PROVIDER=mock` por padrão; `insightface` é opcional. |
| E | O `epi_rules` é o motor oficial de conformidade? E o `epi_compliance`? | A demo (`start_demo.py`) sobe `epi_rules` na porta 8003; `epi_compliance` não aparece nela. |
| — | O projeto dela está no GitHub? Qual endereço e commit entram no MVP? | Nome do ZIP: `epi-vision-porto-itaqui-main`. |

## Ação técnica decorrente de D1

O `Trabalhador` do Spring tem hoje nome, matrícula, empresa e ativo. Faltam `setor` e `cargo`,
que o sincronizador da Sophia já aceita como opcionais. A sincronização nunca foi testada
contra o Spring real.

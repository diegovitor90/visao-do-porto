# Handoff — Visão do Porto: integração com o projeto da Sophia e arquitetura v2

**Data de consolidação:** 22/11/2026
**Substitui como ponto de retomada:** o handoff de 19/11/2026 (frontend/FastAPI). Aquele continua válido como histórico.
**Escopo:** verificação do fluxo real no navegador, diagnóstico do MVP, análise do projeto da Sophia, decisões de arquitetura e roteiro de aulas para reconstruir o documento de arquitetura sem retrabalho.

## 1. Ponto de retomada

- Repositório local: `C:\Users\User\Documents\visao-do-porto`.
- Branch de trabalho: **`docs/arquitetura-v2`**, criada a partir da `main` (`65c5f23`). Commit `f839c54` preserva a documentação de 18/11. **Push feito**: a branch existe no GitHub.
- **Sem commit:** `docs/arquitetura/adrs/RASCUNHO-decisoes-v2.md`, o registro escrito das decisões abaixo. Revisar, fazer o commit e o push.
- **Próximo passo:** Aula 2, escrever o **ADR-002** no modelo MADR (Diego redige, o assistente revisa como professor).
- Modo de trabalho combinado: **ensino passo a passo**, em português, como professor de engenharia de software. Comandos PowerShell copiáveis. Diego executa os comandos de Git. Não fazer push nem merge na `main` sem pedido explícito.

## 2. O que foi comprovado em 19/11 (fluxo real no navegador)

Caminho **upload → proxy do Vite → FastAPI v0.3.0 → YOLO11n → caixas na tela**, sem usar "Usar exemplo":

| Caso | Requisição | Resultado na tela |
|---|---|---|
| Com pessoa (`teste_pessoas.png`) | 200 | Caixa "Pessoa 82,46%"; posição conferida ao pixel com 474 px e 314 px de largura |
| Sem pessoa | 200 | "Análise concluída. Nenhuma pessoa detectada.", sem caixa |
| PNG corrompido | 422 | Mensagem de erro, sem "nenhuma pessoa" |
| FastAPI desligada | 500 (proxy) | "A Vision API está indisponível…", sem caixa |

Testes: Python 17/17; build do frontend aprovado; Playwright 9 aprovados e 1 pulado (o opcional de upload real). O Chromium do Playwright não está instalado no PC; funciona com o Edge:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"; npm --prefix .\frontend test
```

Nenhum código foi alterado para isso. Uma confiança de 82% numa imagem não é precisão nem recall.

## 3. Estado do MVP (diagnóstico de 20/11)

Da cadeia **câmera → pessoa + EPI → zona → regra → alerta → revisão → histórico → métricas**, só a detecção de pessoa por foto estava pronta no `visao-do-porto`. Issues #1–#8 continuam abertas no GitHub, sem responsáveis; só o PR #9 (capacitações) foi fechado.

| Frente | Pronto | Falta |
|---|---|---|
| FastAPI (Diego) | Pessoa por foto, 17 testes; `demo_visual.py` com webcam fora da API | Vídeo na API, ByteTrack, EPI, métricas |
| Spring Boot | Trabalhadores (nome, matrícula, empresa, ativo), capacitações, validade, 20 testes | `setor` e `cargo`, vínculo manual evento–trabalhador, autenticação |
| Frontend (Diego) | Painel, upload real, caixas, revisão com justificativa no `localStorage` | Alertas reais do servidor, editor de zonas, revisão persistida |
| Gestão (#2) | ADR-001 aprovado | Critérios de aceite, metas de FPS/latência/precisão, responsáveis, novo prazo |

Inconsistências conhecidas: `PLANO_MVP.md` e `RASTREABILIDADE.md` ainda descrevem o fluxo-alvo passando imagens pelo Spring, o que o ADR-001 superou.

## 4. Projeto da Sophia (`epi-vision-porto-itaqui`)

Recebido como ZIP (`epi-vision-porto-itaqui-main.zip`). Ainda **não está** em nenhum repositório do Diego: a branch `feature/integracao-sophia` existe no GitHub, mas aponta para `65c5f23` (igual à `main`) e não tem nenhum arquivo dela. Todos os 23 commits do repositório são do Diego.

| Serviço | Porta | Função |
|---|---|---|
| `epi_ppe` | 8000 | Detector: pessoa, capacete, colete (`best.pt`, YOLOv8n ajustado; mAP50 capacete 0,889, colete 0,918, segundo ela) |
| `epi_identity` | 8001 | Cadastro operacional; tem biometria/insightface opcional (padrão `mock`) |
| `epi_fusion` | 8002 | Junta visão e identidade por câmera |
| `epi_rules` | 8003 | Decide conformidade; violação só após 3 s contínuos |
| `epi_incident` | 8004 | Abre e resolve incidentes |
| `epi_alerts` | 8005 | Alertas (só "visto", sem justificativa) |
| `epi_tracker` | 8010 | Mapa, setores, câmeras (`~/.epi_vision/cameras.json`) e rastreadores físicos |
| `epi_tracker/frontend` | 8020 | Tela React/JSX |
| `epi_integration` | — | Pipeline da câmera, ponte Spring → Identity (`sync_trabalhadores.py`) |
| `epi_compliance` | — | Motor alternativo de conformidade, fora da demo |

Princípios dela compatíveis com o projeto: "não observável ≠ violação", "EPI atribuído ≠ EPI usado", sem biometria na interface. Dados de treino CC BY 4.0. O `best.pt` não está no Git.

Pontos de atenção: a ponte Spring → Identity **nunca foi testada contra o Spring real** (só com um Spring simulado); o `epi_ppe` e a FastAPI do Diego usam a mesma porta 8000.

### Comparação das telas (base da decisão B)

| Critério | Tela do Diego | Tela da Sophia |
|---|---|---|
| Qualidade interna | TypeScript, Vite, 9 testes, CSS centralizado, 30 atributos de acessibilidade | JSX sem tipos, sem testes no repositório, `bundle.js` de 1,2 MB no Git, 275 estilos inline, 4 atributos de acessibilidade |
| Evidência (imagem com caixas) | Sim | Não |
| Revisão com justificativa | Sim (Confirmar / Descartar / Evidência insuficiente) | Só "visto" |
| Dados reais | Não (demonstração) | Sim (alerts, fusion, tracker) |
| Foco | Câmera e EPI | Grande parte sobre rastreadores físicos (fora do MVP) |

## 5. Decisões

O **ADR-001 continua válido**: Spring Boot é o núcleo administrativo e nenhum frame de vídeo atravessa o Spring. As decisões abaixo o completam e não o substituem.

### Combinadas com a Sophia (19/11)

| ID | Decisão | Vira |
|---|---|---|
| D1 | Spring Boot é a base oficial do cadastro de trabalhadores (matrícula, nome, setor, cargo). O `epi_identity` sincroniza a partir dele, só leitura. O elo é a **matrícula**. Sem dois cadastros administrativos. | ADR-002 |
| D2 | EPI do MVP: **capacete e colete**. Luvas e botas adiadas (notebook de retreino pronto, não executado). Motivo: apresentar ao Arlley antes do fim do ano. | ADR-003 |

### Tomadas por Diego (20/11)

| ID | Decisão | Consequências |
|---|---|---|
| A | O **`epi_ppe` da Sophia** é o detector de EPI do MVP. | A FastAPI v0.3.0 (YOLO11n) é preservada para a tela Analisar imagem e muda de porta (proposta: 8100); ajustar `vite.config.ts` e README. Documentar local, versão e responsável pelo `best.pt`. Deixar claro qual modelo responde a qual pergunta. |
| B | O **frontend do Diego** (React + TypeScript) é a tela oficial e passa a consumir as APIs da Sophia. | Trocar dados demonstrativos por alerts/fusion/tracker. A revisão com justificativa precisa de um lugar no servidor. A tela de Câmeras da Sophia fica como referência. Plano B se o prazo apertar: apresentar com a tela dela, sem revisão auditável. |
| D | O cadastro de **câmeras e setores fica no Tracker** da Sophia durante o MVP. | Dívida técnica: o Spring pode assumir depois, com sincronizador igual ao de trabalhadores, sem mudar a tela. |
| F | O código da Sophia **entra no `visao-do-porto` pela branch `feature/integracao-sophia`**. | Preservar autoria: commit feito pela Sophia ou importação com histórico (`git subtree`, se o repositório dela estiver no GitHub). Uma só fonte da verdade depois. `.gitignore` para `best.pt`, `dist/bundle.js` e SQLite antes do primeiro commit. |

Nota: a recomendação inicial para F foi "repositório separado". Ela foi revista porque a branch `feature/integracao-sophia` já registrava a intenção de integrar.

### Pendentes de confirmação com a Sophia

| ID | Pergunta | Indício no código |
|---|---|---|
| C | O MVP roda com reconhecimento facial desligado? | `EPI_FACE_PROVIDER=mock` por padrão |
| E | O `epi_rules` é o motor oficial? E o `epi_compliance`? | A demo sobe o `epi_rules` (8003); o `epi_compliance` não aparece |
| — | O projeto dela está no GitHub? Endereço e commit do MVP? | Nome do ZIP: `epi-vision-porto-itaqui-main` |

Mensagem sugerida já foi entregue ao Diego para enviar a ela.

### Ação técnica decorrente de D1

Acrescentar `setor` e `cargo` ao `Trabalhador` do Spring (entidade, DTO, testes). O sincronizador dela já aceita os dois como opcionais. Setores válidos no lado dela: `GRANEIS_SOLIDOS`, `GRANEIS_LIQUIDOS`, `CARGA_GERAL_CELULOSE`, `PIER_BORDO`, `MANUTENCAO_ENGENHARIA`, `GUARDA_PORTUARIA`. Depois, rodar `sync_trabalhadores.py` contra o Spring real.

## 6. Modelo de documento escolhido

- **arc42** como esqueleto (há versão em português e em AsciiDoc): <https://arc42.org> e <https://github.com/arc42/arc42-template>.
- **C4** para diagramas, com C4-PlantUML: <https://c4model.com> e <https://github.com/plantuml-stdlib/C4-PlantUML>.
- **MADR** para ADRs: <https://github.com/adr/madr>.

O documento atual (`docs/arquitetura/arquitetura.adoc`, AsciiDoc + PlantUML) já cobre quase todo o arc42; a mudança é de organização:

| arc42 | Fonte existente |
|---|---|
| 1 Introdução e objetivos | `introducao.adoc` + objetivo do `PLANO_MVP.md` |
| 2 Restrições | Partes do plano (CPU, laboratório, sem reconhecimento facial, dados fictícios) |
| 3 Contexto e escopo | Diagrama `01-contexto-atual` |
| 4 Estratégia da solução | Parte de `arquitetura.adoc` |
| 5 Visão de blocos | `arquitetura.adoc` + diagramas 02, 03, 05, 06 |
| 6 Visão de execução | `fluxos.adoc` + DFDs 09–11 |
| 7 Implantação | `execucao.adoc` |
| 8 Conceitos transversais | `dominio.adoc` |
| 9 Decisões | ADR-001 + novos ADR-002 a 004 |
| 10 Qualidade | RNF01–RNF19 de `RASTREABILIDADE.md` |
| 11 Riscos e dívida técnica | `pendencias.adoc` |
| 12 Glossário | **Não existe; criar** |

Princípio: ADR aprovado nunca é apagado. Decisão nova vira ADR novo; se substituir outra, a antiga ganha "Substituído por".

## 7. Roteiro das aulas

1. ~~Aula 1: inventário e decisões~~ (feita).
2. **Aula 2:** ADR-002 (D1) no modelo MADR.
3. **Aula 3:** ADR-003 (D2, escopo de EPI) e ADR-004 (A, B, D, F).
4. **Aula 4:** diagrama de containers-alvo (`03-containers-alvo.puml`) no C4.
5. **Aula 5:** reorganizar no arc42; atualizar `arquitetura.adoc`, `pendencias.adoc`; criar glossário; corrigir `PLANO_MVP.md` e `RASTREABILIDADE.md`.
6. **Aula 6:** `setor` e `cargo` no Java com teste; rodar a sincronização contra o Spring real.
7. **Aula 7:** regerar HTML/PDF (`docs/tools/gerar.ps1`), revisar e fazer o commit.

## 8. Backups e cuidados

- `C:\Users\User\Documents\visao-do-porto-temp` (12/11): **vazia**.
- `C:\Users\User\Documents\visao-do-porto-preservacao-20261117`: cópia da `feature/backend-diego` com alterações locais da época. **Não apagar.** Não contém a documentação de 18/11.
- A proteção real da arquitetura de 18/11 é o commit `f839c54`, com push feito.
- Não versionar `.venv`, `node_modules`, `.pt`, datasets, fotos de teste nem `bundle.js`.
- O ZIP da Sophia é material de terceiro: não copiar para o repositório sem passar pela decisão F (autoria).

## Prompt para retomar

> Retome o Visão do Porto a partir deste handoff de 22/11. Estou no Windows, no repositório `C:\Users\User\Documents\visao-do-porto`, branch `docs/arquitetura-v2`. Quero continuar aprendendo passo a passo, como aluno de engenharia de software: você explica o conceito, eu faço e você revisa. Preserve o trabalho existente (ADR-001 continua válido) e não faça push nem merge na `main`. Primeiro confira se o `RASCUNHO-decisoes-v2.md` já tem commit. Depois começamos a Aula 2: escrever o ADR-002 (Spring como base oficial do cadastro; Identity da Sophia sincroniza pela matrícula) no modelo MADR.

# Validação da consolidação — 17/11/2026

Ambiente local Windows, fuso America/Sao_Paulo. Entrega prevista: 18/11/2026.
Escopo autorizado: preservar trabalho local, centralizar componentes/documentação
na `main`, testar e publicar por push normal. Não implementar integração nova.

## Preservação

Base: `feature/backend-diego` em `a5dc66f016b9edb505e447b2d0c1f1c2bb0513f1`.
`origin/main` inicialmente em `8ea0b68923da6c73f48fab6dfe4f9977d5e7fd7f`.
Cópia externa `visao-do-porto-preservacao-20261117`, fora do repositório,
incluindo `.git`, não rastreados, pesos e backups. Conferidos 299 arquivos por
SHA-256; manifesto `PRESERVACAO_SHA256.json` na cópia privada.
Excluídos da cópia somente dependências e artefatos regeneráveis: `node_modules`,
`.venv`, `target`, `dist`, caches, bytecode e relatórios de testes.

Referências preservadas: `safety/backend-20261117`, `safety/vision-20261117`,
`safety/main-20261117`, `safety/origin-main-20261117` e `safety/stash-20261117`.
O stash histórico permanece em `772e7755a3d8da0ec0b4bc7ac07f0ba20cb0baec`.
Branch temporária: `consolidacao/main-20261117`.

## Conteúdo e limites

Spring Boot 4.1.2 com trabalhadores/capacitações; FastAPI v0.3.0 local e frontend
0.1.1 preservados. Alterações desta preparação limitadas a documentação,
`.gitignore` e manifesto Python. Lógica de aplicação/testes existentes preservada.
O relatório histórico de inferência real permanece byte a byte inalterado.

`requirements.txt` registra versões verificadas no ambiente existente, incluindo
API, inferência, demonstração e testes. Nenhuma dependência instalada. Não é um
lock completo nem evidência de instalação limpa em outra máquina/plataforma.

## Validação após preparação

| Validação | Comando no diretório do componente | Resultado |
| --- | --- | --- |
| Java | `.\mvnw.cmd -o test` | 20 testes; 0 falhas, 0 erros, 0 ignorados; BUILD SUCCESS; 1 min 19 s |
| Python | `.\.venv\Scripts\python.exe -B -m pytest test_main.py -q -p no:cacheprovider` | 17 aprovados; 1 aviso; 8,68 s |
| Frontend build | `npm run build` | TypeScript sem emissão e Vite concluídos; build Vite 18,08 s |
| Frontend testes | `npm test`, com Chrome existente via `PLAYWRIGHT_CHROMIUM_EXECUTABLE` | 9 aprovados; 1 ignorado; 0 falhas; 45,8 s |

Java: contexto (1), API de capacitações (6), serviço de capacitações (11) e
serviço de trabalhadores (2). JDK 26, alvo 21, Maven Wrapper 3.10.0. Reutilizou
classes compiladas; não houve `clean` nem comprovação de compilação limpa nesta
execução. Avisos existentes de agente Mockito/Byte Buddy não causaram falha.

Python 3.11.9; testes usam detector simulado e não carregam pesos. Aviso existente
Starlette/httpx de depreciação. Não foi instalado `httpx2` nem alterada a suíte.

Node 22.17.1, npm 10.9.2, React instalado 19.3.1, Vite 7.3.8 e Playwright 1.65.1.
O smoke optativo foi ignorado por ausência de `VISION_API_SMOKE_IMAGE`; ele ainda
espera o comportamento da API v0.2.0 e não comprova integração real v0.3.0.
Avisos de NO_COLOR/FORCE_COLOR não afetaram a suíte.

Os 57 arquivos de aplicação/recursos existentes conferem com os hashes da cópia
externa; o relatório histórico de inferência também permaneceu intacto. Verificados
UTF-8, pares de fences e destinos locais dos links dos nove arquivos Markdown.
As 13 versões de `requirements.txt` correspondem ao ambiente instalado.

Auditoria antes do commit: conferidos os 35 caminhos explicitamente preparados e
os 63 arquivos de texto da árvore proposta. Não houve achados nos padrões comuns
de tokens, chaves privadas, senhas literais, CPF/e-mail, caminhos indevidos ou
conteúdo binário. Nenhum arquivo preparado excede 1 MiB; o maior é o lockfile npm,
com 40.178 bytes. `git diff --cached --check` passou; `--stat` e `--name-only`
foram inspecionados. Essa busca por padrões não é uma auditoria exaustiva de
segurança ou do histórico Git.

## Exclusões da publicação

- Pesos `backend/fastapi/yolo11n.pt` (5.613.764 bytes).
- Fotografia local `backend/fastapi/teste_pessoas.png`; origem/autorização pública não estabelecidas.
- `backend/fastapi/main.py.bak`, `backend/fastapi/test_main.py.bak` e `frontend-backup 0.1/`.
- `backend/backend-springboot/erros-maven.txt` e `HELP.md` gerado/ignorado.
- Ambientes virtuais, `node_modules`, `target`, `dist`, caches e relatórios automáticos.
- Configurações privadas `.env*` (exceto `.env.example`), chaves, credenciais e bancos locais.

Esses arquivos locais não são apagados. O Git recebe somente caminhos explícitos
revisados. O tamanho de cada arquivo preparado e padrões comuns de segredos/dados
pessoais serão verificados antes do commit.

## Pendências

Integração Spring Boot–FastAPI não implementada. Hoje frontend → proxy Vite →
FastAPI, com Spring administrativo separado. Permanecem pendentes cliente HTTP,
DTOs/controller Java, URL/timeouts, erros upstream e testes sem YOLO por teste Java.
O parser frontend descarta `model`; fixtures e smoke optativo ainda refletem
contrato anterior. Sem novas funcionalidades de EPIs, rastreamento, zonas ou alertas reais.

A inferência real anterior (HTTP 200, uma pessoa, confiança 0.8246) está na
[evidência histórica](../backend/fastapi/VALIDACAO_INFERENCIA_REAL_2026-11-17.md).
Não será repetida nesta consolidação. Não há validação operacional portuária.

## Publicação

Commit planejado: `chore: consolida backend, FastAPI 0.3.0, frontend e documentação`.
Publicação condicionada a testes, revisão do índice, atualização de `origin/main`,
ancestralidade compatível com fast-forward e sucesso do dry-run. Sem force push.
Este documento registra a preparação; a confirmação do hash publicado é apresentada
no relatório final da execução, após consulta ao remoto.


## Manifesto de arquivos incluídos

Caminhos novos ou alterados em relação a `origin/main` inicial (`8ea0b68`),
incluindo o incremento Spring Boot já commitado e os arquivos locais selecionados.
Demais arquivos rastreados existentes são mantidos. Total: 52 caminhos.

```text
.gitignore
README.md
backend/backend-springboot/mvnw
backend/backend-springboot/scripts/demo_capacitacoes.py
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/config/TempoConfig.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/controller/CapacitacaoController.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/controller/TrabalhadorController.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/dto/CapacitacaoRequest.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/dto/CapacitacaoResponse.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/dto/ConsultaCapacitacaoResponse.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/dto/TrabalhadorRequest.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/entity/Capacitacao.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/repository/CapacitacaoRepository.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/service/CapacitacaoService.java
backend/backend-springboot/src/main/java/br/com/visaodoporto/backend/service/TrabalhadorService.java
backend/backend-springboot/src/main/resources/application.properties
backend/backend-springboot/src/test/java/br/com/visaodoporto/backend/CapacitacaoApiTest.java
backend/backend-springboot/src/test/java/br/com/visaodoporto/backend/service/CapacitacaoServiceTest.java
backend/backend-springboot/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
backend/fastapi/VALIDACAO_INFERENCIA_REAL_2026-11-17.md
backend/fastapi/demo_visual.py
backend/fastapi/main.py
backend/fastapi/requirements.txt
backend/fastapi/test_main.py
backend/fastapi/vision_detector.py
docs/CAPACITACOES.md
docs/PLANO_MVP.md
docs/RASTREABILIDADE.md
docs/TESTES_CAPACITACOES.md
docs/VALIDACAO_CONSOLIDACAO_2026-11-17.md
docs/contrato-ia-backend.md
frontend/.env.example
frontend/.gitignore
frontend/README.md
frontend/index.html
frontend/package-lock.json
frontend/package.json
frontend/playwright.config.ts
frontend/public/laboratorio.svg
frontend/public/porto.svg
frontend/src/app/App.tsx
frontend/src/features/analysis/AnalysisPage.tsx
frontend/src/features/analysis/Evidence.tsx
frontend/src/features/analysis/api.ts
frontend/src/features/operations/Operations.tsx
frontend/src/features/operations/model.ts
frontend/src/main.tsx
frontend/src/shared/Badge.tsx
frontend/src/styles.css
frontend/tests/mvp.spec.ts
frontend/tsconfig.json
frontend/vite.config.ts
```

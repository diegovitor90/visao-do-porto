# Revisão independente de ambiente e confiabilidade

A8 revisou a branch experimental do repositório oficial em Codex Cloud a partir de `00f915c`. O ambiente é adequado para os fluxos locais com dados fictícios. Os controles de CI e a prontidão operacional do pipeline EPI permanecem pendentes.

## Ambiente e reprodução

| Item | Verificação | Limite |
|---|---|---|
| Java/Maven | JDK Temurin 21.0.13.1 neste workspace e Maven Wrapper 3.10.0. O build com o truststore do sistema resolve o erro PKIX observado no Lab. A2 publicou evidência de `clean verify` com 23 testes. | O Java padrão é só runtime. O Wrapper fixa a versão, mas não declara `distributionSha256Sum`. |
| Python | Python 3.12.14, dependências diretas fixadas em `requirements.txt` e instalação limpa anterior com constraints dos wheels CPU do PyTorch. A3 comprova inferência de pessoa com peso local verificado. | Fixar dependências transitivas e hashes por plataforma para garantir instalação idêntica em outra instância. O ambiente virtual e as constraints usadas no Cloud ficam fora do Git. |
| Frontend | Node.js 24.22.3, npm 11.19.1, Chromium 156. Reinstalei 27 dependências via `npm ci --offline` e gerei SBOM CycloneDX 1.5 com 27 componentes. | Revisar a política de scripts do npm para o `postinstall` de `esbuild`. Inventário local do npm não cobre Java e Python. |
| Máquina | Cota de 2 CPUs, limite de 8 GiB e cerca de 58 GiB livres. Docker rootless 29.9.2 e Compose 2.40.3. | O teste `hello-world` do Lab comprova o daemon. O projeto oficial nesta revisão não contém Dockerfile ou Compose. A capacidade simultânea do pipeline EPI é desconhecida. |

Evite usar as funções `visao_maven` e `visao_api` de `/workspace/scratch/visao-lab-env.sh` para evidência do repositório oficial. Elas apontam ao checkout `visao-do-porto-lab`, e a função da API usa a porta 8000. Os comandos abaixo usam o checkout oficial e artefatos locais previamente verificados. Rode cada bloco em um terminal separado.

```bash
cd /workspace/visao-do-porto/backend/backend-springboot
export JAVA_HOME=/workspace/scratch/visao-tools/jdk-21.0.13.1+2
export PATH="$JAVA_HOME/bin:$PATH"
export MAVEN_USER_HOME=/workspace/scratch/visao-maven
export MAVEN_OPTS="-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts"
./mvnw -o -B -s "$MAVEN_USER_HOME/settings.xml" \
  "-Dmaven.repo.local=$MAVEN_USER_HOME/repository" clean verify
```

```bash
cd /workspace/visao-do-porto/backend/fastapi
python_bin=/workspace/scratch/visao-python-repro/bin/python
"$python_bin" -m pip check
"$python_bin" -m pytest -q
model_path=/workspace/scratch/visao-yolo/official-yolo11n.pt
model_sha=0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1
printf '%s  %s\n' "$model_sha" "$model_path" | sha256sum -c - &&
  cp "$model_path" yolo11n.pt &&
  YOLO_OFFLINE=true YOLO_AUTOINSTALL=false \
  YOLO_CONFIG_DIR=/workspace/scratch/visao-yolo OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 \
  "$python_bin" -m uvicorn main:app --host 127.0.0.1 --port 8100
```

```bash
cd /workspace/visao-do-porto/frontend
npm ci --offline --cache /workspace/scratch/visao-npm --no-audit --no-fund
npm run build
PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium \
  VISION_API_SMOKE_IMAGE=/workspace/scratch/visao-yolo/synthetic.png npm test
npm sbom --sbom-format=cyclonedx > /workspace/scratch/sprint-frontend.cdx.json
```

A porta 5173 é do Vite. A 8100 separa a Vision API do candidato `epi_ppe` na 8000. O Spring administrativo usa 8080 em loopback. Execute a prova do navegador com uma única instância do Vite, iniciada pelo Playwright. Se a imagem sintética estiver ausente, gere um PNG local com Pillow, sem dados pessoais. Em uma instância sem os caches, reponha Maven Central, PyPI/PyTorch e npm pelos clientes normais com validação TLS ativa. Reproduza o peso a partir da release oficial verificando SHA-256 antes do carregamento.

## Prontidão, falhas e observabilidade

- O `/api/health` de Spring e FastAPI sinaliza liveness. O `/api/v1/vision/status` indica `READY` se conseguir importar o detector e localizar a função, inclusive com `model_loaded=false`. O indicador não checa o peso em disco nem executa um frame. A confirmação funcional é o POST sintético com `inference_performed=true`.
- O carregamento é sob demanda. Registre latência fria e quente separadamente e teste concorrência antes de definir orçamento de timeout, workers e filas. No piloto, evite multiplicar processos de inferência no mesmo limite de CPU e memória sem medição.
- O cadastro em H2 perde dados ao reiniciar nessa configuração. Rode um POST seguido de GET para evidenciar o cadastro real na mesma sessão. Para o piloto operacional, o estado de ocorrências, os identificadores e o comportamento após reinício precisam de verificação própria.
- A integração experimental carece de metas e coleta de latência por estágio, fila, erros e quedas de fluxo. Prefira logs com identificador de requisição e metadados mínimos, sem conteúdo de mídia ou cadastro. Nos serviços candidatos, condicione a prontidão à dependência necessária e teste indisponibilidade e recuperação com dados sintéticos.

## Cadeia de fornecimento e controles de promoção

- A revisão não encontrou workflows em `.github/workflows`. Builds e testes da sprint são verificações locais. Antes da promoção, automatize JDK 21, Python CPU, `npm ci` e suítes pertinentes, com permissões mínimas e logs/artefatos que excluam mídia, pesos e credenciais.
- A busca local com `git grep -IlE` em arquivos rastreados não encontrou assinaturas comuns de chaves privadas, tokens do GitHub ou chaves AWS. A checagem usa poucos padrões e cobre apenas o snapshot. Não há evidência de scanner dedicado e histórico varrido nesta revisão.
- O `npm audit` anterior do Lab reportou zero vulnerabilidades no frontend. As dependências Java e Python, a imagem de implantação, a cobertura SAST e o SBOM do sistema completo continuam sem varredura comprovada. Não há configuração versionada de SBOM, scanner ou CI nesta revisão.
- O gate local de reprodução está aprovado para os componentes disponíveis. O gate de promoção operacional depende da autorização e validação dos componentes EPI, da disciplina de cadeia de fornecimento acima e de evidências de readiness e recuperação.

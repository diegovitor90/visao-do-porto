# Verificação independente da sprint

A revisão QA conferiu o cadastro administrativo em `d19d3f7` e o frontend integrado em `00f915c`. O backend operacional da Sophia ficou fora da execução. Os dados de teste incluíram apenas pessoas e empresas fictícias e imagens sintéticas.

| Verificação | Ambiente e evidência |
| --- | --- |
| Compilação e testes Java | JDK 21, Maven Wrapper 3.10.0, `verify` com cache local e `-o`. **23 testes aprovados**, JAR empacotado. |
| Contrato administrativo por HTTP | JAR real em loopback com H2. `201` com os três campos legados e os opcionais nulos. `201` com 255 caracteres e normalização dos espaços do cargo. Listagem e leitura por UUID preservaram os dados. Duplicata sequencial e campo de 256 caracteres receberam `400`; o dado inválido ficou fora da listagem. UUID válido inexistente recebeu `404`. |
| Build web e regressão | `npm ci --offline` com cache já preenchido, `npm run build` e Playwright com Chromium de sistema. **10 testes aprovados**, incluindo upload de PNG sintético via Vite e inferência real do YOLO11n em CPU. O caso de navegador levou 17,7 s sob execução simultânea da suíte Java. Isso mede o caso de teste completo. |
| Upload inválido | O navegador enviou um PNG corrompido para a FastAPI real, recebeu `422` e exibiu erro sem caixa de detecção. |
| Serviço interrompido | Após parar a FastAPI de teste, um upload pelo navegador recebeu `500` do proxy Vite e exibiu indisponibilidade sem caixa de detecção. |
| Timeout do cliente | Um interceptador Playwright manteve uma resposta simulada pendente e o relógio virtual avançou 30 s. A interface exibiu “A análise não respondeu a tempo” e nenhuma caixa. |
| Fluxo demonstrativo | A suíte verifica que o exemplo não dispara POST, a fila filtrada mostra estado vazio e uma revisão sem justificativa é rejeitada. A decisão de evidência insuficiente reaparece no histórico após recarregar o navegador, via armazenamento local. |

## Limites observados

- A aplicação aborta o upload em **30 s**. Os **45 s** da espera Playwright permitem aguardar o evento de resposta e não estendem o prazo do cliente. Para validar capacidade, medir latência concorrente e cold starts em execução separada.
- O teste de timeout cobre a espera anterior aos cabeçalhos HTTP. Uma resposta iniciada que atrase o corpo pode aparecer como erro genérico de contrato, pois a leitura de JSON suprime a exceção de abortamento. Vale uma regressão específica quando o contrato de timeout for ampliado.
- Novos campos são opcionais no contrato HTTP. A sincronização de setor com a taxonomia de Identity, concorrência de matrículas, deduplicação de eventos, permissões por função, recuperação dos serviços operacionais e persistência de revisão ainda exigem provas próprias.
- A integração real validada neste recorte é **frontend → Vite → FastAPI → YOLO11n**. A porta da API de análise é 8100. A prova administrativa HTTP é independente e nenhum upload passa pelo Spring.

## Reprodução

Execute `./mvnw -B -o verify` com JDK 21 e cache Maven preenchido, no backend Spring. Para o smoke do frontend, inicie a FastAPI v0.3 no diretório com os pesos locais verificados, na porta 8100. Execute `npm ci`, `npm run build` e `npm test` com `VISION_API_SMOKE_IMAGE` apontando para um PNG sintético e, se necessário, `PLAYWRIGHT_CHROMIUM_EXECUTABLE` para o Chromium de sistema. O teste opcional de upload real confere HTTP 200, `COMPLETED`, `inference_performed=true`, modelo YOLO11n e consistência entre o JSON e os elementos exibidos.

# Verificação do incremento de capacitações

Data: 13/11/2026. Ambiente de desenvolvimento Linux, Eclipse Temurin JDK 21.0.13+9, Maven Wrapper 3.10.0, Spring Boot 4.1.2 e H2 em memória. Não foi realizado teste no computador de Diego, no laboratório da UNDB ou no porto.

## Evidência de origem

A `main` consultada estava em `8ea0b68923da6c73f48fab6dfe4f9977d5e7fd7f`. Sua história contém `a6e22c4` e `d685999`. A branch `feature/backend-diego` estava em `a6e22c45e954aa8b80a41cfe748bd65658b2d1ba`. Nenhuma das duas árvores continha `src/main/java/br/com/visaodoporto/backend/service/TrabalhadorService.java`, embora controller e testes importassem essa classe. O arquivo local no computador de Diego não foi inspecionado.

## Testes automatizados

| Classe | Testes | Falhas | Erros | Ignorados |
| --- | ---: | ---: | ---: | ---: |
| TrabalhadorServiceTest | 2 | 0 | 0 | 0 |
| CapacitacaoServiceTest | 11 | 0 | 0 | 0 |
| CapacitacaoApiTest | 6 | 0 | 0 | 0 |
| BackendSpringbootApplicationTests | 1 | 0 | 0 | 0 |
| Total | 20 | 0 | 0 | 0 |

Executados com Maven após preparar JDK 21 completo e baixar dependências. O ambiente tinha inicialmente apenas JRE 21; a execução inicial falhou por ausência de compilador adequado. Mockito utiliza `mock-maker-proxy` nos testes porque os objetos simulados são interfaces de repositório; isso dispensa anexação dinâmica de agente à JVM. Os testes de API utilizam contexto Spring real, validação HTTP via MockMvc e repositórios JPA/H2.

Reprodução no Windows: `./mvnw.cmd test`, dentro de `backend/backend-springboot`. Relatórios gerados em `target/surefire-reports/`. O diretório target não é versionado.

## Demonstração HTTP real

Aplicação Spring Boot iniciada com o classpath compilado e servidor embutido em `127.0.0.1:8080`. Saúde retornou `UP`. O roteiro `scripts/demo_capacitacoes.py` executou cadastro, registro e consulta por HTTP e verificou:

- `VALIDA`: registro verificado dentro da validade.
- `VENCIDA`: registro verificado vencido.
- `AUSENTE`: trabalhador cadastrado, sem registro daquele curso.
- `NAO_VERIFICADA`: registro existente, sem verificação.

As quatro respostas mantiveram `autorizacaoAcesso=NAO_AVALIADA`. Cada execução usa matrículas fictícias únicas. A aplicação foi encerrada após a verificação e seus dados em memória foram descartados.

## Limites da evidência

Não foram testados vídeo, ByteTrack, vínculo cadastro-trajetória, geometria de zonas, EPIs, alertas, autenticação, front-end ou desempenho portuário. A tarefa #6 permanece parcial. Estes resultados sustentam somente o incremento administrativo descrito em [CAPACITACOES.md](CAPACITACOES.md).

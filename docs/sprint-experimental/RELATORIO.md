# Sprint experimental de integração — 22 de novembro de 2026

A sprint integrou dois caminhos executáveis. O Spring Boot passou a aceitar e devolver setor e cargo para cadastros fictícios. O frontend enviou um PNG sintético pelo Vite à FastAPI v0.3, que executou YOLO11n em CPU e devolveu um resultado vazio válido. A integração de EPI segue bloqueada por autorização, pesos e contratos necessários para operar sem biometria.

A base é `65c5f23b3b18f5e7e7e01a5f22c666714914194f`, na branch `experiment/integracao-sophia-piloto-20261122`. O [ADR-001 aprovado](../arquitetura/adrs/ADR-001.adoc) foi trazido byte a byte de `docs/arquitetura-v2` (`9ec17c7`). O Spring recebe dados administrativos. O fluxo principal de vídeo permanece no Python. O ZIP da Sophia foi consultado como referência estática, sem importar seus arquivos ou executar seus serviços.

## Requisito, implementação e evidência

| Requisito | Estado | Entrega e verificação |
| --- | --- | --- |
| Cadastro com matrícula, setor e cargo | **Implementado e testado** | Campos opcionais, limite de 255 caracteres, normalização e compatibilidade com o cadastro anterior. JAR real via HTTP e suíte Java com 23 testes. |
| Análise de imagem no React existente | **Implementado e testado** | Proxy local para a Vision API em 8100, com configuração substituível. Build TypeScript/Vite e 10 testes Playwright com smoke real habilitado. |
| Resposta vazia e estados de falha | **Implementado e testado** | Inferência real em PNG sintético com resultado vazio. QA verificou PNG corrompido, indisponibilidade real e prazo do cliente com atraso simulado. |
| Contrato de sincronização por matrícula | **Implementado, mas não validado na integração** | O produtor Spring foi validado. O consumidor Identity foi avaliado estaticamente. Nenhuma sincronização real foi confirmada. |
| Fila e revisão com justificativa | **Simulado** | O frontend conserva a demonstração e guarda a revisão no navegador. A persistência de revisão no servidor **não foi implementada**. |
| EPI, ocorrência, regra e feed real | **Bloqueado** | Faltam checkpoint autorizado, perfil sem biometria e contrato de evento por câmera/track. Os módulos inspecionados não foram executados. |
| Uso com dados reais e decisões de acesso | **Não implementado** | O ensaio usa loopback e dados sintéticos. Os controles de promoção e o escopo de decisão humana estão documentados. |

## Coordenação e critérios de aceite

Quatro responsáveis pela construção trabalharam em worktrees separadas. A1 auditou arquitetura e contratos, A2 implementou o incremento Java, A3 avaliou o pipeline visual e A4 atualizou o frontend. A5 revisou segurança, A6 avaliou a evidência científica, A7 repetiu testes de forma independente e A8 verificou reprodutibilidade e confiabilidade. Nenhuma branch auxiliar faz parte da publicação da sprint.

| Gate | Incremento local | Cadeia operacional de EPI |
| --- | --- | --- |
| Contrato | Aprovado para cadastro e Vision v0.3 | Bloqueado para ocorrência anônima, sincronização e revisão persistente |
| Implementação | Aprovado para cadastro e fluxo de análise | Bloqueado pela autorização e dependências ausentes |
| Verificação funcional | Aprovado para os cenários sintéticos exercitados | Bloqueado pelo checkpoint e corpus ausentes |
| Segurança | Aprovado para loopback sintético | Bloqueado para exposição operacional e uso de Identity |
| Integração | Aprovado para navegador → Vite → Vision e para o HTTP administrativo | Bloqueado para Spring → Identity e para PPE → Alerts |
| Revisão independente | Concluída nas quatro especialidades | Concluída para leitura estática e condições de entrada |
| Documentação e entrega | Comandos, limitações e commits registrados | Condições para retomada registradas |

## Evidências

- [Arquitetura e inventário](ARQUITETURA-INTEGRADA.md)
- [Testes e reprodução](TESTES-E-EVIDENCIAS.md) e [QA independente](QA-INDEPENDENTE.md)
- [Segurança e riscos](SEGURANCA.md)
- [Avaliação da visão](AVALIACAO-IA.md) e [validação científica independente](VALIDACAO-CIENTIFICA.md)
- [Confiabilidade e dependências](CONFIABILIDADE.md)
- [Bloqueios](BLOQUEIOS.md) e [próximas etapas](PROXIMAS-ETAPAS.md)

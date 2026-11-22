# Documentação técnica do Visão do Porto

Versão documental **1.0**, 18/11/2026. Base de código: `65c5f23`.
Estado: documentação para revisão da equipe; não é aceite operacional.

**Comece pelo [documento mestre de arquitetura](arquitetura/arquitetura.adoc).**
O [ADR-001](arquitetura/adrs/ADR-001.adoc) registra a decisão aprovada: Java
administrativo fora do fluxo principal de vídeo. Referências históricas que
propunham frames via Spring estão superadas nesse ponto.

| Leitura | Conteúdo |
| --- | --- |
| [Arquitetura e domínio](arquitetura/arquitetura.adoc) | Contexto, atual/alvo, responsabilidades, UML, DER e DFD |
| [API Spring](api/spring.adoc) | Endpoints administrativos, campos, regras e testes |
| [API FastAPI](api/fastapi.adoc) | Multipart, detecções, limites, erros e OpenAPI |
| [Execução e testes](operacao/execucao.adoc) | Windows, comandos e configuração existente |
| [Gerar e manter a documentação](operacao/documentacao.md) | Ferramentas isoladas, diagramas, HTML/PDF e verificações |
| [Auditoria e evidências](arquitetura/secoes/auditoria.adoc) | Versões, classificação das evidências e limites da inspeção |
| [Pendências e propostas](arquitetura/secoes/pendencias.adoc) | Decisões abertas e plano mínimo de integração |

Diagramas editáveis: [fontes PlantUML](arquitetura/diagramas/fontes/).
Exportações: [SVG/PNG](arquitetura/diagramas/imagens/).
Artefatos de leitura: [HTML](arquitetura/gerado/arquitetura.html) e
[PDF](arquitetura/gerado/arquitetura.pdf).
O HTML incorpora os diagramas; as fontes continuam sendo AsciiDoc e PlantUML.

[Validação desta documentação](operacao/VALIDACAO_DOCUMENTACAO.md): ferramentas, verificações e limites.

## Evidências históricas preservadas

- [Capacitações](CAPACITACOES.md) e [testes administrativos](TESTES_CAPACITACOES.md).
- [Contrato da API e planejamento histórico](contrato-ia-backend.md).
- [Consolidação de 17/11](VALIDACAO_CONSOLIDACAO_2026-11-17.md).
- [Inferência real anterior](../backend/fastapi/VALIDACAO_INFERENCIA_REAL_2026-11-17.md).
- [Fluxo real no navegador, 19/11](VALIDACAO_FLUXO_NAVEGADOR_2026-11-19.md).
- [Plano MVP](PLANO_MVP.md) e [rastreabilidade](RASTREABILIDADE.md).

Implementado, testado historicamente, proposto e não verificado são estados
diferentes. Uma confiança de detecção não é acurácia do modelo. Não há evidência
de integração completa com Sophia, EPIs ou reconhecimento facial neste projeto.

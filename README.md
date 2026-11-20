# Visão do Porto

Piloto acadêmico de apoio à segurança portuária: núcleo administrativo Spring
Boot, Vision API FastAPI v0.3.0 com YOLO11n e frontend React/Vite 0.1.1.
Base publicada: `65c5f23`. Não há validação operacional em ambiente portuário.

## Arquitetura e documentação

**[Índice técnico](docs/README.md)** ·
[Arquitetura e diagramas](docs/arquitetura/arquitetura.adoc) ·
[API Spring](docs/api/spring.adoc) · [API FastAPI](docs/api/fastapi.adoc) ·
[Execução e testes](docs/operacao/execucao.adoc) ·
[Gerar HTML/PDF](docs/operacao/documentacao.md).

Decisão aprovada: Spring mantém trabalhadores/capacitações; Python processa
visão e operação. **Nenhum frame de vídeo atravessa o Spring no fluxo principal.**
A [ADR-001](docs/arquitetura/adrs/ADR-001.adoc) supera a proposta antiga de proxy
Java para imagens. Módulos da Sophia são candidatos, ainda não integrados.

Hoje: frontend → proxy Vite → FastAPI → YOLO11n; cliente administrativo → Spring → H2.
Alertas/mapa são demonstrativos; revisões ficam no navegador. Ainda faltam
integração operacional, EPIs validados, zonas reais e auditoria persistente.

## Executar com ambientes já preparados

Em terminais separados, a partir da raiz:

```powershell
cd backend/backend-springboot
.\mvnw.cmd spring-boot:run
```

```powershell
cd backend/fastapi
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm run dev
```

Spring: `127.0.0.1:8080`; FastAPI: `127.0.0.1:8000/docs`; frontend: `127.0.0.1:5173`.
H2 é volátil. Disponibilizar pesos locais em backend/fastapi e usar imagem autorizada.
Não versionar pesos, fotografias privadas, dependências, bancos ou segredos.
Pré-requisitos, testes e preparação: [guia operacional](docs/operacao/execucao.adoc).

## Evidências e evolução

[Consolidação](docs/VALIDACAO_CONSOLIDACAO_2026-11-17.md),
[inferência real histórica](backend/fastapi/VALIDACAO_INFERENCIA_REAL_2026-11-17.md),
[capacitações](docs/CAPACITACOES.md) e
[contrato/histórico](docs/contrato-ia-backend.md).
Resultados históricos não comprovam integração completa ou acurácia do modelo.
Mudanças de código devem revisar contratos, testes e fontes dos diagramas.
Preservar o trabalho da equipe; esta revisão documental não faz commit ou push.

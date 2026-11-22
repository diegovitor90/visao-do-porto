# Testes e evidências

## Base e comandos

A branch experimental parte de `65c5f23b3b18f5e7e7e01a5f22c666714914194f`. Codex Cloud Linux x86_64 com cota de 2 CPUs, limite de 8 GiB e sem CUDA. Os testes usam cadastros fictícios e mídia sintética.

| Cobertura | Comando e evidência |
| --- | --- |
| Spring Boot | Em `backend/backend-springboot`, executar `./mvnw clean verify` com JDK 21 e a CA do ambiente quando necessária. **23 testes aprovados**. A suíte verifica persistência dos novos campos, nulos para cadastros legados, normalização e limites. |
| API Spring real | JAR em loopback. `POST /api/trabalhadores` devolveu HTTP 201 e `GET /api/trabalhadores` devolveu HTTP 200 com os campos persistidos para a matrícula fictícia. A prova valida o produtor. O consumidor Identity não participou. |
| FastAPI | Em `backend/fastapi`, `python -m pip check` e `python -m pytest -q`. **17 testes aprovados**. A suíte usa dublê de detector nos casos de análise. Há aviso de depreciação do TestClient. |
| Frontend | Em `frontend`, `npm ci`, `npm run build` e `npm test`. Com Vision API em 8100 e `VISION_API_SMOKE_IMAGE` apontando ao PNG sintético, **10 testes aprovados** na worktree de construção. |
| YOLO11n real | HTTP 200, `COMPLETED`, `inference_performed=true` e zero detecções. O navegador verifica a resposta e a renderização do resultado. Ver [avaliação de IA](AVALIACAO-IA.md) para hash e tempos da prova separada. |
| Integridade de escopo | `git diff --check` e comparação byte a byte do ADR-001 com a versão aprovada. A prova não envolve a branch `main`, os serviços da Sophia ou o CredenciaOS. |

## Reproduzir o teste no navegador

1. Obtenha o peso YOLO11n da [release oficial v8.4.0](https://github.com/ultralytics/assets/releases/tag/v8.4.0) e confira o SHA-256 `0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`. Coloque o peso localmente em `backend/fastapi/yolo11n.pt`.
2. Use o ambiente Python de CPU, gere um PNG sintético com Pillow e inicie a Vision API em `backend/fastapi` com `YOLO_OFFLINE=true YOLO_AUTOINSTALL=false python -m uvicorn main:app --host 127.0.0.1 --port 8100`.
3. Em `frontend`, execute `VISION_API_SMOKE_IMAGE=/caminho/absoluto/sintetico.png npm test`. Se usar Chromium do sistema, defina `PLAYWRIGHT_CHROMIUM_EXECUTABLE` com o caminho do executável. A aplicação usa 30 s de prazo na análise. O teste usa uma imagem pequena e mede um único fluxo, sem carga concorrente.

A fila de ocorrências e a revisão local usam dados demonstrativos. A imagem sintética comprova o caminho de inferência vazio. A precisão de detecção, a cadeia de EPI e a persistência após reinício têm gates próprios.

## Verificações complementares

- `npm audit` na branch experimental reportou zero vulnerabilidades conhecidas no frontend no momento da consulta. As dependências Java e Python ficaram fora dessa consulta.
- A revisão de segurança executou 10 casos defensivos da Vision API. A revisão de confiabilidade gerou um SBOM CycloneDX com 27 componentes do frontend, fora do Git.
- A validação científica independente repetiu o caso negativo e observou latências diferentes. As medições não fornecem uma estimativa de FPS ou de capacidade concorrente.

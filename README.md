# Visão do Porto

Projeto acadêmico de apoio à segurança portuária. Este repositório centraliza o
backend Spring Boot, a Vision API FastAPI v0.3.0, o frontend React/Vite 0.1.1,
os testes e a documentação. Estado técnico revisado em **17/11/2026**, com entrega
prevista para **18/11/2026**. Não há validação operacional em ambiente portuário.

## Estado implementado

| Componente | Disponível | Limites |
| --- | --- | --- |
| Spring Boot 4.1.2 | Saúde, cadastro/listagem/consulta de trabalhadores, capacitações e validade | H2 em memória; sem autenticação; `autorizacaoAcesso=NAO_AVALIADA` |
| Vision API v0.3.0 | Upload JPEG/PNG, validação e inferência real YOLO11n de pessoas em CPU | Classe `person`; sem identificação civil, rastreamento ou EPIs |
| Frontend 0.1.1 | Painel demonstrativo, upload, caixas de detecção, filtros e revisão local | Alertas/mapa ilustrativos; revisão no navegador; sem persistência no servidor |
| Testes | Java, Python e navegador; build TypeScript/Vite | Testes isolados não comprovam integração completa |

**Pendente:** integração Spring Boot–FastAPI, vínculo administrativo com detecções,
pipeline operacional de vídeo, EPIs, zonas/regras reais, alertas produzidos pela IA,
autenticação, auditoria de servidor e avaliação de desempenho/precisão.

## Arquitetura atual e próxima integração

Hoje, o frontend usa o proxy de desenvolvimento Vite diretamente para a FastAPI:

```text
Frontend → Vite /api/v1/vision/* → FastAPI → YOLO11n → Frontend
Cliente administrativo → Spring Boot → JPA / H2
```

Arquitetura-alvo, **ainda não implementada**:

```text
Cliente/Frontend → Spring Boot → FastAPI → YOLO11n → Spring Boot → Cliente
```

A consolidação na `main` não implementa essa comunicação. A API real e a proposta
futura estão distinguidas no [contrato único](docs/contrato-ia-backend.md).

## Executar o Spring Boot

Alvo de compilação Java 21; Maven Wrapper 3.10.0. Os testes locais de 17/11 foram
executados com JDK 26; a evidência histórica também inclui JDK 21.

```powershell
cd backend/backend-springboot
.\mvnw.cmd -o test
.\mvnw.cmd spring-boot:run
```

O modo `-o` exige dependências já disponíveis. Em ambiente novo, após autorizar os
downloads, executar `.\mvnw.cmd test`. Servidor local: `http://127.0.0.1:8080`.

| Método | Caminho |
| --- | --- |
| GET | `/api/health` |
| POST / GET | `/api/trabalhadores` |
| GET | `/api/trabalhadores/{id}` |
| POST / GET | `/api/trabalhadores/{id}/capacitacoes` |
| GET | `/api/trabalhadores/{id}/capacitacoes/{codigo}/situacao` |

Usar dados fictícios. O H2 é volátil e os dados são descartados ao encerrar a
aplicação. [API administrativa](docs/CAPACITACOES.md).

## Executar a Vision API

Ambiente validado: Windows e Python 3.11.9. `requirements.txt` fixa as versões
diretas e transitivas críticas verificadas; não é um lock completo de todas as
dependências nem comprova instalação limpa em outras plataformas. A consolidação
não instala pacotes. Para preparar um ambiente novo, com downloads autorizados:

```powershell
cd backend/fastapi
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Com o ambiente e os pesos locais disponíveis:

```powershell
cd backend/fastapi
.\.venv\Scripts\python.exe -B -m pytest test_main.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Se o terminal já estiver nessa pasta, não repetir o `cd`. Consultar `/api/health`,
`/api/v1/vision/status` e `/docs`. `READY` indica que o detector está disponível;
não comprova que os pesos já foram carregados ou que uma inferência foi bem-sucedida.

Análise: `POST /api/v1/vision/analyze`, multipart com campo `file`, JPEG ou PNG,
até 5 MiB e 20 megapixels. Exemplo em outro terminal:

```powershell
curl.exe -F "file=@C:/caminho/imagem-autorizada.png;type=image/png" http://127.0.0.1:8000/api/v1/vision/analyze
```

### Pesos e reprodução da inferência

`yolo11n.pt` fica fora do Git. A distribuição oficial está em
[Ultralytics Assets](https://github.com/ultralytics/assets/releases) e o uso em
[YOLO11](https://docs.ultralytics.com/models/yolo11/). O pacote instalado possui
download automático a partir de `ultralytics/assets`, release padrão `v8.4.0`.
Para reproduzir de forma controlada, obter o artefato da release oficial escolhida,
registrar URL/release e SHA-256 e colocá-lo em `backend/fastapi/yolo11n.pt`.

O arquivo local validado tem 5.613.764 bytes e SHA-256
`0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1`.
Sua origem de download histórica não foi comprovada e esse hash não foi comparado
com o artefato oficial. Não tratar o hash local como certificado de autenticidade.
Executar a API a partir de `backend/fastapi`, pois o detector usa caminho relativo.
Na ausência do peso, a biblioteca pode tentar download durante a inferência.

O registro [de inferência real](backend/fastapi/VALIDACAO_INFERENCIA_REAL_2026-11-17.md)
preserva a evidência anterior: HTTP 200, uma pessoa e confiança 0.8246. A fotografia
original permanece privada e não é distribuída; usar imagem própria/autorizada.
Para a demonstração gráfica existente: `.\.venv\Scripts\python.exe demo_visual.py
--image C:/caminho/imagem-autorizada.png` ou `demo_visual.py --webcam 0`.
Essa demonstração é local e não integra o Spring Boot.

## Executar o frontend

Node.js 20.19+ na série 20 ou 22.12+. O ambiente validado usa Node 22.17.1.

```powershell
cd frontend
npm run build
npm run dev
```

Em ambiente novo, executar `npm ci` com autorização para baixar as dependências.
Abrir `http://127.0.0.1:5173`. O proxy usa a FastAPI em `127.0.0.1:8000`;
`frontend/.env.example` documenta a variável `VISION_API_TARGET`.
O proxy Vite não acompanha o build de produção. [Detalhes e testes](frontend/README.md).

## Documentação e evidências

- [Plano do MVP](docs/PLANO_MVP.md): planejamento histórico e situação atual.
- [Rastreabilidade](docs/RASTREABILIDADE.md): requisitos, cobertura parcial e evidências.
- [Capacitações](docs/CAPACITACOES.md) e [validação histórica](docs/TESTES_CAPACITACOES.md).
- [Contrato IA/backend](docs/contrato-ia-backend.md): API real e proposta futura.
- [Validação da consolidação](docs/VALIDACAO_CONSOLIDACAO_2026-11-17.md).
- [Inferência real anterior](backend/fastapi/VALIDACAO_INFERENCIA_REAL_2026-11-17.md).
- [Frontend](frontend/README.md).

## Organização do trabalho

Por decisão do responsável em 17/11/2026, os componentes são centralizados na
`main`. As branches anteriores, referências de segurança e stash histórico são
preservados. Próximas mudanças devem ser pequenas, testadas e revisadas antes de
publicar. Usar caminhos explícitos ao preparar commits; não versionar dependências,
pesos, fotos locais, backups, credenciais, bancos ou relatórios gerados.

As referências de equipe e requisitos de 26/10, 28/10 e 12/11 permanecem nos
documentos históricos. Planejamento não equivale a funcionalidade implementada,
aceite coletivo ou validação portuária.

# Visão do Porto

**Plataforma de apoio à segurança portuária com visão computacional, regras por zona e registro auditável de eventos.**

> **Estado desta branch — 13/11/2026:** incremento administrativo em revisão, com cadastro de trabalhadores e capacitações testados. A `main` conferida em `8ea0b68` continha os controllers e testes de trabalhadores, mas não o arquivo `TrabalhadorService.java` necessário para compilar. Esta branch completa o serviço ausente. A solução integrada de visão computacional, regras, alertas e interface ainda está em desenvolvimento. **Não há validação operacional em ambiente portuário.**

## Sobre o projeto

O Visão do Porto busca apoiar a identificação de situações de risco em áreas operacionais por meio de câmeras, detecção de pessoas e equipamentos de proteção individual (EPIs), acompanhamento de trajetórias e aplicação de regras específicas de cada zona.

A proposta distingue três atividades que não devem ser confundidas:

1. **Detecção e rastreamento:** localizar pessoas e acompanhar trajetórias no vídeo, sem presumir sua identidade.
2. **Verificação de segurança:** avaliar capacete, colete, presença em zonas e regras configuradas, incluindo situações indeterminadas.
3. **Identidade administrativa:** manter cadastros e capacitações fictícios no piloto, com possibilidade de vínculo manual e revisão humana.

O sistema deverá produzir alertas explicáveis, acompanhados de evidências e passíveis de revisão.

## Escopo do MVP

### Núcleo previsto

- Uma câmera física no piloto de laboratório, com simulação inicial de múltiplas fontes.
- Detecção e rastreamento de pessoas.
- Detecção de **capacete e colete** e associação dos EPIs às pessoas.
- Configuração de zonas por polígonos sobre a imagem e definição de EPIs exigidos por zona.
- Avaliação de presença, intrusão e conformidade, considerando persistência temporal, oclusão e estado indeterminado.
- Alertas com evidências, justificativas, revisão humana e histórico consultável.
- Medição de desempenho, precisão, recall, latência e falsos alarmes em condições de laboratório.

### Suporte administrativo previsto

- Cadastro fictício de trabalhadores e empresas.
- Capacitações e verificação de validade.
- Vínculo manual e auditável entre cadastro e eventos, sem identificação automática de pessoas no piloto.

### Fora do recorte inicial

Reconhecimento facial, QR/RFID operacional, EPIs especializados, reconhecimento automático de cena, integração com sistemas institucionais, BI completo, implantação multicâmera física, processamento em borda e validação em operação portuária. São possibilidades de evolução, não funcionalidades entregues.

## Arquitetura proposta

```text
Câmera / vídeo de teste
        |
        v
FastAPI (Python) — detecção, rastreamento e eventos
        |
        | contrato de integração a definir
        v
Spring Boot (Java) — cadastros, capacitações,
regras administrativas, alertas, histórico e auditoria
        |
        v
Frontend — monitoramento, zonas e revisão humana
```

- **Spring Boot:** API administrativa e regras de negócio.
- **FastAPI:** serviço separado para processamento de visão computacional.
- **Frontend:** experiência de configuração, acompanhamento e revisão.
- **Banco de dados:** H2 em memória para o desenvolvimento inicial do Spring Boot; PostgreSQL é uma evolução planejada, ainda não concluída.

A comunicação entre serviços e o contrato de eventos precisam ser especificados e validados em conjunto pelas frentes.

## Estado das entregas

| Componente | Estado nesta branch, em 13/11/2026 |
| --- | --- |
| Estrutura inicial Spring Boot e FastAPI | Criada no repositório |
| Endpoint de saúde do Spring Boot | Implementado e testado manualmente |
| Cadastro de trabalhadores com JPA | Implementado e testado |
| Listagem e consulta de trabalhadores | Implementadas e testadas manualmente |
| Validação de matrícula duplicada | Implementada e testada |
| Testes automatizados do serviço | Executados com sucesso |
| Capacitações e verificação de validade | Implementadas e testadas nesta branch; integração à main depende do PR |
| Pipeline de detecção/rastreamento de vídeo | Planejado; implementação integrada não comprovada aqui |
| EPIs, zonas, regras e alertas | Planejados |
| Frontend e integração entre serviços | Planejados |
| Validação no porto | Não realizada |

A primeira entrega de backend está registrada no commit [`a6e22c4`](https://github.com/diegovitor90/visao-do-porto/commit/a6e22c4), na branch `feature/backend-diego`. A presença desse commit na história da `main` foi confirmada em 13/11/2026. O arquivo `TrabalhadorService.java`, porém, estava ausente no repositório e é completado nesta entrega.

## Incremento de capacitações (13/11/2026)

Implementado nesta branch para revisão: cadastro de capacitações fictícias, listagem por trabalhador e consulta de validade. A consulta diferencia `VALIDA`, `VENCIDA`, `AUSENTE` e `NAO_VERIFICADA`, sem conceder autorização de acesso. Inclui testes e roteiro HTTP com quatro cenários.

- [Executar e entender a API de capacitações](docs/CAPACITACOES.md).
- [Contrato proposto de integração com IA](docs/contrato-ia-backend.md).

O vínculo com ByteTrack, zonas, alertas e integração visual continuam pendentes. O módulo está em revisão e ainda não foi incorporado à `main`.

## Executando o backend Spring Boot localmente

**Pré-requisitos:** JDK compatível com o projeto, Git e acesso ao terminal PowerShell no Windows. O projeto utiliza Maven Wrapper.

Na raiz do repositório:

```powershell
cd backend/backend-springboot
.\mvnw.cmd clean test
.\mvnw.cmd spring-boot:run
```

Com a aplicação iniciada, em outro terminal:

```powershell
Invoke-RestMethod http://localhost:8080/api/health
Invoke-RestMethod http://localhost:8080/api/trabalhadores
```

Exemplo de cadastro **com dados fictícios**:

```powershell
$corpo = @{
    nome = 'João Silva'
    matricula = 'PORTO-001'
    empresa = 'Operadora Portuária A'
} | ConvertTo-Json

Invoke-RestMethod -Uri 'http://localhost:8080/api/trabalhadores' `
    -Method Post `
    -ContentType 'application/json; charset=utf-8' `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($corpo))
```

Endpoints administrativos disponíveis nesta etapa:

| Método | Caminho | Finalidade |
| --- | --- | --- |
| `GET` | `/api/health` | Verificar o serviço |
| `POST` | `/api/trabalhadores` | Cadastrar trabalhador |
| `GET` | `/api/trabalhadores` | Listar trabalhadores |
| `GET` | `/api/trabalhadores/{id}` | Consultar por UUID |
| `POST` | `/api/trabalhadores/{id}/capacitacoes` | Registrar capacitação fictícia |
| `GET` | `/api/trabalhadores/{id}/capacitacoes` | Listar capacitações do trabalhador |
| `GET` | `/api/trabalhadores/{id}/capacitacoes/{codigo}/situacao` | Consultar validade atual, sem decidir acesso |

**Validação desta entrega:** 20 testes Maven aprovados e quatro cenários conferidos contra a API HTTP iniciada. [Registro da validação](docs/TESTES_CAPACITACOES.md).

**Observações:** o H2 em memória não é persistência definitiva; registros podem desaparecer ao reiniciar a aplicação. O serviço FastAPI tem estrutura inicial, mas seu comando de inicialização e endpoints devem ser documentados após validação específica.

## Equipes

| Frente | Liderança | Integrantes |
| --- | --- | --- |
| Requisitos, Gestão e BI | Hugo Diniz | Victor Santos, Hugo Diniz e Isabelle Rodrigues |
| Frontend e UX | Jason Araujo | Luiza, Victor Santos e Jason Araujo |
| Backend | Diego Souza | Diego Souza e Sophia |
| IA e Visão Computacional | Gustavo Sousa | Isabelle Rodrigues, Gustavo Sousa e Micaelle Susy |

As lideranças não implicam atribuição automática de cada subtarefa. Responsáveis e prazos específicos devem ser definidos em conjunto.

## Planejamento e rastreabilidade

- [Plano de Ação](docs/PLANO_MVP.md) — escopo, dependências, entregas, critérios de aceite e organização do trabalho.
- [Rastreabilidade de Requisitos](docs/RASTREABILIDADE.md) — RF01–RF22, RNF01–RNF19, decisões e evidências de validação.

Os documentos acima estão na pasta `docs/`.

O planejamento utiliza as referências de tarefas **#2–#8**, que precisam ser conferidas com as Issues reais do GitHub. Uma tarefa planejada não equivale a uma funcionalidade implementada ou aprovada.

## Fluxo de contribuição

1. Criar uma branch de trabalho a partir da `main` atualizada.
2. Desenvolver uma entrega pequena e verificável.
3. Executar os testes pertinentes e registrar evidências.
4. Abrir Pull Request descrevendo alterações, requisitos afetados e critérios de aceite.
5. Solicitar revisão e integrar à `main` após aprovação.
6. Atualizar o Plano de Ação e a Rastreabilidade quando houver mudança de estado ou decisão.


---

**Referências de planejamento:** Documento de Requisitos de Software v1.0 (26/10/2026), Ata VC UNDB (28/10/2026) e revisão técnica de 12/11/2026. Este README apresenta o estado conhecido do projeto; não substitui os documentos originais nem representa aprovação coletiva de propostas ainda em discussão.

# Visão do Porto

**Plataforma de apoio à segurança portuária com visão computacional, regras por zona e registro auditável de eventos.**

> **Estado do projeto — 12/11/2026:** desenvolvimento de MVP acadêmico, com demonstração planejada em laboratório da UNDB. A API administrativa inicial em Spring Boot possui funcionalidades implementadas e testadas. A solução integrada de visão computacional, regras, alertas e interface ainda está em desenvolvimento. **Não há validação operacional em ambiente portuário.**

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

| Componente | Estado em 12/11/2026 |
| --- | --- |
| Estrutura inicial Spring Boot e FastAPI | Criada no repositório |
| Endpoint de saúde do Spring Boot | Implementado e testado manualmente |
| Cadastro de trabalhadores com JPA | Implementado e testado |
| Listagem e consulta de trabalhadores | Implementadas e testadas manualmente |
| Validação de matrícula duplicada | Implementada e testada |
| Testes automatizados do serviço | Executados com sucesso |
| Capacitações e verificação de validade | Pendentes |
| Pipeline de detecção/rastreamento de vídeo | Planejado; implementação integrada não comprovada aqui |
| EPIs, zonas, regras e alertas | Planejados |
| Frontend e integração entre serviços | Planejados |
| Validação no porto | Não realizada |

A primeira entrega de backend está registrada no commit [`a6e22c4`](https://github.com/diegovitor90/visao-do-porto/commit/a6e22c4), na branch `feature/backend-diego`. **A integração à `main` deve ser confirmada no GitHub**; não é presumida neste documento.

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

- [Plano de Ação](docs/PLANO_DE_ACAO.md) — escopo, dependências, entregas, critérios de aceite e organização do trabalho.
- [Rastreabilidade de Requisitos](docs/RASTREABILIDADE_REQUISITOS.md) — RF01–RF22, RNF01–RNF19, decisões e evidências de validação.

**Atenção:** os links acima pressupõem que os dois documentos sejam adicionados à pasta `docs/` do repositório. Se estiverem em outro local, ajuste os caminhos.

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

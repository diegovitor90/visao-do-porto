# Capacitações: primeira entrega administrativa

13/11/2026. Implementação proposta em `feature/backend-diego`, para revisão por Pull Request. Relacionada à tarefa #6; não encerra o requisito de vínculo com trajetória.

## O que este incremento permite

Cadastrar uma capacitação fictícia de um trabalhador já cadastrado, listar seus registros e consultar a situação atual de um tipo de capacitação. A implementação segue Controller → Service → Repository → Entity no Spring Boot existente. FastAPI continua reservado à visão computacional. H2 continua em memória e os dados são descartados ao encerrar o serviço.

O arquivo `TrabalhadorService.java`, importado pelo controller e pelos testes, estava ausente tanto na `main` quanto na `feature/backend-diego` consultadas. Este incremento completa esse serviço com os métodos já esperados e adiciona validação ao cadastro. Não cria outro cadastro em Python.

## Executar e demonstrar

Pré-requisitos: JDK 21, Git, acesso ao Maven Central. Python 3.10+ somente para o roteiro de demonstração, sem pacotes extras. No Windows, confira `java -version` e `JAVA_HOME`: ambos devem apontar para JDK 21.

Após obter a branch da entrega, na raiz do repositório:

```powershell
cd backend/backend-springboot
.\mvnw.cmd test
.\mvnw.cmd spring-boot:run
```

Em outro terminal, na mesma pasta:

```powershell
python scripts/demo_capacitacoes.py
```

No Linux/macOS use `sh mvnw test` e `sh mvnw spring-boot:run`. O roteiro cria quatro pessoas fictícias com matrículas diferentes a cada execução, registra exemplos e confere os quatro estados. Ao reiniciar o serviço, rode o roteiro novamente para recriar os dados.

O servidor escuta em `127.0.0.1:8080`. Autenticação e perfis ainda não foram implementados. Use apenas localmente, com dados fictícios. O campo `verificadaPor` é um rótulo de demonstração informado no corpo, não uma identidade autenticada nem uma trilha de auditoria de produção.

## API

Prefixo: `/api/trabalhadores/{trabalhadorId}/capacitacoes`. `trabalhadorId` é o UUID retornado pelo cadastro existente.

| Método | Sufixo | Resultado |
| --- | --- | --- |
| POST | nenhum | 201, registro de capacitação |
| GET | nenhum | 200, registros daquele trabalhador |
| GET | `/{codigo}/situacao` | 200, situação atual e registros usados |

Exemplo de POST (ajuste as datas para o dia da demonstração):

```json
{
  "codigo": "DEMO-ZONA-A",
  "nome": "Capacitação fictícia do laboratório",
  "realizadaEm": "2026-11-01",
  "validaAte": "2026-12-01",
  "verificada": true,
  "fonte": "Simulação, sem certificado real",
  "verificadaPor": "OPERADOR-DEMO"
}
```

`DEMO-ZONA-A` é apenas um código de curso de exemplo. Não cadastra zona, não aplica NR-29 e não comprova exigência normativa. A fonte é uma descrição, não um arquivo ou link de certificado.

Campos obrigatórios: código, nome, realização, validade, indicador de verificação e fonte. Código aceita letras maiúsculas ASCII, números, hífen e sublinhado, até 64 caracteres. Datas seguem `AAAA-MM-DD`. Não se aceita realização futura nem validade anterior à realização. Registro verificado exige verificador; registro não verificado exige verificador ausente ou vazio.

## Regra de consulta

| Situação | Interpretação |
| --- | --- |
| `VALIDA` | Existe pelo menos um registro verificado, realizado até hoje e ainda dentro da validade. |
| `NAO_VERIFICADA` | Não existe registro válido verificado, mas há algum registro sem verificação. Não comprova capacitação, mesmo que a data esteja no prazo. |
| `VENCIDA` | Existem registros e todos estão verificados e vencidos. |
| `AUSENTE` | Não há registro daquele código para aquele trabalhador cadastrado. |

A consulta usa a data atual no fuso `America/Sao_Paulo`. O último dia da validade é incluído. A situação é calculada a cada consulta, sem necessidade de alterar o registro ao vencer. Renovações são novos registros, preservando os anteriores. Um registro válido verificado prevalece sobre históricos vencidos ou pendentes; na ausência dele, pendências de verificação são exibidas de forma conservadora. Todos os registros daquele código acompanham a resposta para revisão.

`autorizacaoAcesso` permanece sempre `NAO_AVALIADA`. Treinamento válido não autoriza acesso. Não há consulta por `track_id` neste incremento. Uma trajetória sem vínculo não pode ser classificada como trabalhador sem treinamento: a identidade permanece não confirmada.

Trabalhador inexistente retorna 404; corpo/código/datas inválidos retornam 400; trabalhador inativo não recebe novo registro (409). A API não oferece edição, exclusão, revogação ou comprovação documental nesta versão. Reenvio de POST cria novo registro; o cliente não deve repetir silenciosamente uma solicitação cuja resposta se perdeu.

## Testes e limites

Os testes abrangem datas-limite, fuso, vencimento, renovação, ausência, registros não verificados, separação por pessoa/curso, validação HTTP, persistência JPA/H2 durante a execução e preservação do cadastro existente. Evidências da execução ficam na descrição do PR e em `target/surefire-reports/` após rodar Maven.

Próxima integração: definir e implementar sessão/câmera/trajetória, vínculo manual revisável, perda/invalidação do vínculo e requisitos por zona. O contrato proposto está em [contrato-ia-backend.md](contrato-ia-backend.md). Pipeline de vídeo, métricas de IA, alertas, interface, autenticação e validação portuária continuam pendentes. Este incremento não implementa o fluxo completo da demonstração visual.

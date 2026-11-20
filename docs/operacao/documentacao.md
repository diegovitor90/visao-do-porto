# Gerar, verificar e atualizar a documentação

Pipeline: **AsciiDoc + PlantUML → SVG/PNG → HTML Asciidoctor.js → PDF Chrome**.
O PDF deriva do mesmo HTML autocontido; não existe uma segunda cópia manual do texto.
Não foi configurado Maven/Spring REST Docs e nenhum endpoint de aplicação é criado.

## Ferramentas isoladas

- Java; PlantUML **1.2026.10**, JAR oficial com C4 embarcado.
- SHA-256 do JAR: `e9bc9e6b2eb715e8c0c929f3dcb5fc1923be13f37599b09c293c66d354e88686`.
- Node; `@asciidoctor/core` **3.0.4** fornecido fora das dependências da aplicação.
- Chrome/Chromium já disponível e biblioteca Playwright externa.
- Python da `.venv` existente, com FastAPI/Pydantic para extrair OpenAPI.

Asciidoctor.js foi preparado apenas na pasta temporária da conversa. PlantUML foi
obtido da [release oficial v1.2026.10](https://github.com/plantuml/plantuml/releases/tag/v1.2026.10)
e teve SHA-256 conferido. Nenhuma instalação global nem alteração nos manifestos
da aplicação foi feita. O diretório temporário não faz parte do repositório.

Em outra máquina, preparar as mesmas ferramentas em um diretório local de
documentação, com autorização de downloads. Exemplo de preparação **opcional**:

```powershell
# Não executado automaticamente por gerar.ps1; não usar instalação global.
npm install --prefix C:/ferramentas-docs --no-audit --no-fund --ignore-scripts @asciidoctor/core@3.0.4
# Fornecer PlantUML oficial e Playwright/Chrome existentes separadamente.
```

Referência HTML: [Asciidoctor.js](https://docs.asciidoctor.org/asciidoctor.js/latest/).
Renderização: PlantUML com `-Playout=smetana` dispensa Graphviz. Includes C4 usam
a biblioteca dentro do JAR, sem envio de diagramas a servidores externos.

## Gerar tudo

Compatível com Windows PowerShell 5.1: executar diretamente `.\docs\tools\gerar.ps1`. Não exige o comando `pwsh` nem instalação de PowerShell 7.

Na raiz, substituir os caminhos de ferramentas por diretórios existentes. Nenhum
caminho abaixo é arquivo de aplicação, segredo ou caminho pessoal obrigatório.

```powershell
.\docs\tools\gerar.ps1 `
  -PlantUmlJar C:/ferramentas-docs/plantuml.jar `
  -AsciidoctorModule C:/ferramentas-docs/node_modules/@asciidoctor/core `
  -ChromePath 'C:/Program Files/Google/Chrome/Application/chrome.exe' `
  -PlaywrightModule C:/ferramentas-docs/node_modules/playwright
```

`-PythonExe`, `-NodeExe` e `-JavaExe` permitem intérpretes já existentes. Por
padrão, usa a `.venv` principal para extrair schemas. O build importa somente
`main` e chama `app.openapi()`: não importa vision_detector, não inicia servidor,
não chama status, não carrega pesos e não executa inferência/testes funcionais.

Saídas versionáveis: `docs/arquitetura/diagramas/imagens/*.svg` e `*.png`;
`docs/api/gerado/` contém declarações, OpenAPI e proveniência.
`docs/arquitetura/gerado/` contém HTML, PDF e manifesto do build.
Não versionar ferramentas, node_modules, caches ou dados usados em demonstração.
Estes scripts não executam operações Git de alteração.

## Verificações separadas

```powershell
.\backend\fastapi\.venv\Scripts\python.exe -B docs/tools/verificar_docs.py --fontes
.\backend\fastapi\.venv\Scripts\python.exe -B docs/tools/extrair_contratos.py
.\backend\fastapi\.venv\Scripts\python.exe -B docs/tools/verificar_docs.py
```

O modo completo exige artefatos já gerados. Verifica links locais, includes dentro
do repositório, UTF-8, blocos PlantUML, exportações, âncoras HTML, hashes das fontes
de aplicação e presença de PDF. Não é uma auditoria de segurança nem teste de negócio.
Mensagens Asciidoctor e erros PlantUML interrompem o build; não publicar imagens de erro.

Para gerar só diagramas, após preparar o JAR:

```powershell
# Exemplo para um arquivo; repetir para os demais e para -tpng.
java '-Djava.awt.headless=true' -jar C:/ferramentas-docs/plantuml.jar `
  -Playout=smetana -tsvg -charset UTF-8 -failfast2 `
  -o ../imagens docs/arquitetura/diagramas/fontes/01-contexto-atual.puml
```

No comando individual, a saída relativa a `fontes/` deve ser `../imagens`.
No build completo, o destino é absoluto e resolvido pelo script.

## Atualizar após mudar o código

1. Atualizar teste e contrato no componente responsável.
2. Revisar APIs AsciiDoc, responsabilidades e marcações implementado/proposto.
3. Editar `.puml`; não editar SVG/PNG exportado.
4. Registrar novo ADR somente quando houver decisão aprovada. Propostas vão para pendências.
5. Regenerar tudo e verificar links/proveniência. Revisar semanticamente o diff.
6. Renderizar páginas do PDF e conferir capa, sumário, tabelas e legendas.
7. Atualizar versão/data e evidências sem transformar resultado histórico em teste novo.

A geração é reproduzível com as ferramentas/versões indicadas; metadados PDF,
versão de Chrome e fontes do sistema podem impedir igualdade byte a byte.
O manifesto registra versões e hashes, sem caminhos pessoais. Não há download
automático. Se faltar uma ferramenta, o script termina com mensagem de dependência.

## Limites desta revisão

Java: documentação derivada de controllers, DTOs e testes; não há snippets
HTTP gerados por Spring REST Docs. FastAPI: OpenAPI gerado do código, exemplos
contratuais e evidência real histórica separados. A inspeção visual do PDF
deve ser repetida quando fontes, diagramas ou estilos mudarem.

# Validação documental — 18/11/2026

Base de aplicação: main em `65c5f23b3b18f5e7e7e01a5f22c666714914194f`.
Sophia: inspeção estática em `ef88e1920bbed4feb0b0899d99eacdd184d35899`.
Nenhuma integração externa ou aplicação foi executada como parte deste build.

## Resultado

- Documento mestre AsciiDoc, HTML autocontido e PDF A4 de **28 páginas**.
- **11 diagramas PlantUML**, cada um exportado em SVG e PNG.
- Diagramas C4 usam biblioteca embarcada no JAR; sem includes ou renderização remotos.
- Sintaxe/renderização PlantUML aprovadas pelo comando com `-failfast2`.
- HTML Asciidoctor sem mensagens de erro/aviso; diagramas incorporados em data URI.
- PDF gerado do mesmo HTML. Imagens carregadas sem falhas no Chrome headless.
- Capa, sumário em duas colunas, 11 capítulos, tabelas, figuras e legendas revisados por páginas renderizadas com Poppler.
- PDF reaberto com pypdf/pdfplumber: texto e marcadores presentes, sem caracteres de substituição ou texto fora dos limites da página.
- Links relativos/includes, âncoras HTML, UTF-8, presença das exportações e proveniência verificados.
- OpenAPI 0.3.0 gerado de `app.openapi()`; confirmado que `vision_detector` não foi importado.
- Declarações Python extraídas por AST e records Java por leitura de fonte; helpers/imports omitidos.
- Hashes de **63 arquivos rastreados** comparados com a base inicial: somente README.md e docs/contrato-ia-backend.md mudaram. Todo código, testes, configurações, pesos e fotos existentes preservados.

## Ferramentas usadas

PlantUML 1.2026.10 (JAR com hash conferido), Asciidoctor.js 3.0.4, Node 22.17.1,
Python 3.11.9 da aplicação para extrair OpenAPI e Chrome 157.0.8103.79 para PDF.
Ferramentas PDF do runtime disponível foram usadas somente para inspeção.
Java e fontes do sistema influenciam o layout; manifesto de build registra hashes e versões.
A geração é reproduzível por comando, sem promessa de identidade byte a byte do PDF.

Asciidoctor.js foi instalado **somente na pasta temporária de trabalho**, com
npm local e sem scripts de instalação. PlantUML foi baixado da release oficial
para a mesma pasta. Nenhuma instalação global ou dependência da aplicação alterada.
O npm apresentou avisos de dependências transitivas antigas da ferramenta documental;
esses pacotes não foram adicionados ao projeto nem executados pelo backend.

## Comandos e verificações

Ver [geração documental](documentacao.md) para `docs/tools/gerar.ps1` e parâmetros.
O pipeline completo foi executado e reexecutado após ajustes documentais.
Checks adicionais: `git diff --check`, hashes SHA-256, abertura do PDF, extração
de texto e renderização Poppler. Git foi usado somente para consulta.

Problemas encontrados no gerador foram corrigidos antes da entrega: quoting
PowerShell do argumento Java, export default do Asciidoctor.js, delimitadores de
tabela, separação de capítulos, detecção de recursos remotos e escala/paginação
dos diagramas. Nenhuma correção de aplicação foi necessária.

## Limites e decisões pendentes

Não foram executadas suítes Java/Python/Playwright de negócio nesta tarefa:
apenas verificações pertinentes à documentação. Resultados funcionais são históricos,
identificados como tal no documento. Nenhuma nova inferência, webcam, biometria,
serviço Sophia ou migração foi executada.

Os diagramas futuros são propostas. Permanecem em aberto: cadastro oficial de
câmeras, zonas poligonais, persistência de ocorrências/evidências, revisão humana,
regras de não detecção, integração dos motores de conformidade e banco durável.
Somente o ADR-001 registra decisão aprovada nesta revisão. SQL Server é possibilidade.

O build usa Asciidoctor.js + Chrome, não Asciidoctor PDF/Ruby. Spring REST Docs
não foi configurado: os exemplos Java são contratuais, não capturas HTTP novas.
As verificações automáticas detectam problemas estruturais, mas revisão semântica
continua necessária após mudanças no código. Não houve commit, push ou troca de branch.

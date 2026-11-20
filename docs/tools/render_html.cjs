// Asciidoctor.js fornecido externamente; nenhuma instalação/download automático.
const fs = require('node:fs');
const path = require('node:path');
const [source, output, modulePath] = process.argv.slice(2);
if (!source || !output || !modulePath) throw new Error('Uso: node render_html.cjs origem destino modulo-asciidoctor');
const loader = require(path.resolve(modulePath));
const asciidoctor = (loader.default || loader)();
const logger = asciidoctor.MemoryLogger.create();
asciidoctor.LoggerManager.setLogger(logger);
const root = path.resolve(__dirname, '../..');
const stylesheet = path.join(__dirname, 'estilo.css');
fs.mkdirSync(path.dirname(output), {recursive: true});
const html = asciidoctor.convertFile(path.resolve(source), {
  safe: 'unsafe', // fontes locais auditadas; includes são checados antes pelo verificador
  standalone: true, to_file: false, doctype: 'book',
  base_dir: path.dirname(path.resolve(source)),
  attributes: {'data-uri': true, stylesheet, 'webfonts!': '', 'icons!': ''},
});
const errors = logger.getMessages();
if (errors.length) {
  for (const error of errors) console.error(error);
  throw new Error('Asciidoctor registrou mensagens: revisar includes/imagens antes de publicar.');
}
if (!html.includes('data:image/svg+xml')) throw new Error('Diagramas não foram incorporados ao HTML.');
fs.writeFileSync(path.resolve(output), html, 'utf8');
console.log('HTML autocontido gerado por Asciidoctor.js ' + asciidoctor.getVersion());

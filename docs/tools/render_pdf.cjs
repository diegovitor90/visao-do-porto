// PDF a partir do HTML canônico; usa Chrome/Chromium já disponível.
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const [html, pdf, chrome, playwrightModule] = process.argv.slice(2);
if (!html || !pdf || !chrome) throw new Error('Uso: node render_pdf.cjs html pdf chrome [modulo-playwright]');
const {chromium} = require(playwrightModule ? path.resolve(playwrightModule) : 'playwright');
(async () => {
  const browser = await chromium.launch({executablePath: chrome, headless: true});
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(path.resolve(html)).href, {waitUntil: 'load'});
    await page.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all([...document.images].map(img => img.decode()));
    });
    const defects = await page.evaluate(() => [...document.images].filter(i => !i.complete || !i.naturalWidth).length);
    if (defects) throw new Error('Há imagens não carregadas no HTML');
    await page.pdf({path: path.resolve(pdf), format: 'A4', printBackground: true,
      preferCSSPageSize: true, displayHeaderFooter: true,
      margin: {top:'18mm', right:'16mm', bottom:'20mm', left:'16mm'},
      headerTemplate: '<span></span>',
      footerTemplate: '<div style="font-family:Arial;font-size:9px;color:#526478;width:100%;margin:0 16mm;display:flex;justify-content:space-between"><span>Visão do Porto · Documento técnico 1.0 · 18/11/2026</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'});
    console.log('PDF gerado do HTML; imagens carregadas: sem falhas.');
  } finally { await browser.close(); }
})().catch(err => {console.error(err); process.exitCode = 1;});

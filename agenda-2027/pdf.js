// Convierte agenda-2027.html en PDF para imprenta.
// Uso (desde la raíz del repo): node agenda-2027/pdf.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  // Con "--revision" usa la versión liviana (una semana por mes)
  const rev = process.argv.includes('--revision');
  const src = path.resolve(__dirname, rev ? 'agenda-2027-revision.html' : 'agenda-2027.html');
  const out = path.resolve(__dirname, rev ? 'Planner-2027-revision.pdf' : 'Planner-2027-interior.pdf');
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + src);
  await p.waitForLoadState('networkidle');
  await p.evaluate(() => document.fonts.ready);
  await p.emulateMedia({ media: 'print' });
  await p.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  await b.close();
  console.log('PDF listo:', out);
})();

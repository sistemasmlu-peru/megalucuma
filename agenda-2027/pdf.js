// Convierte agenda-2027.html en PDF para imprenta.
// Uso (desde la raíz del repo): node agenda-2027/pdf.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const src = path.resolve(__dirname, 'agenda-2027.html');
  const out = path.resolve(__dirname, 'Planner-2027-interior.pdf');
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

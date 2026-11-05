import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/XUE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {chromium}=require('playwright');
const root=path.dirname(fileURLToPath(import.meta.url));
const svg=await fs.readFile(path.join(root,'fig1.svg'),'utf8');
const width=6.875,height=width*1000/2900;
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try {
  const page=await browser.newPage({viewport:{width:2900,height:1000},deviceScaleFactor:1});
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>@page{size:${width}in ${height}in;margin:0}html,body{margin:0;padding:0;width:2900px;height:1000px}svg{display:block;width:2900px;height:1000px}@media print{html,body,svg{width:${width}in;height:${height}in}}</style></head><body>${svg}</body></html>`);
  await page.evaluate(()=>document.fonts.ready);
  await page.locator('svg image').evaluateAll(async nodes=>{
    await Promise.all(nodes.map(node=>new Promise((resolve,reject)=>{const image=new Image();image.onload=resolve;image.onerror=reject;image.src=node.getAttribute('href');})));
  });
  const overflow=await page.locator('svg text').evaluateAll(nodes=>nodes.map(n=>({text:n.textContent,b:n.getBBox(),t:n.getAttribute('transform')})).filter(o=>!o.t&&(o.b.x<0||o.b.y<0||o.b.x+o.b.width>2900||o.b.y+o.b.height>1000)));
  if(overflow.length)throw new Error('Text outside figure '+JSON.stringify(overflow));
  await page.screenshot({path:path.join(root,'fig1.png'),fullPage:true});
  await page.pdf({path:path.join(root,'fig1.pdf'),preferCSSPageSize:true,printBackground:true,margin:{top:0,bottom:0,left:0,right:0}});
  const report=JSON.parse(await fs.readFile(path.join(root,'layout_report.json'),'utf8'));
  report.export={text_overflow:overflow,raster_images:await page.locator('svg image').count(),editable_texts:await page.locator('svg text').count(),preview_px:[2900,1000]};
  await fs.writeFile(path.join(root,'layout_report.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report.export));
} finally {await browser.close();}

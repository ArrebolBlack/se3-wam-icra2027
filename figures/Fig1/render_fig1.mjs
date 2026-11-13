import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require=createRequire('C:/Users/XUE/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {chromium}=require('playwright');
const root=path.dirname(fileURLToPath(import.meta.url));
const report=JSON.parse(await fs.readFile(path.join(root,'layout_report.json'),'utf8'));
const {left,right}=report.panels;
const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
try{
  for(const spec of [
    {stem:'fig1',wh:report.canvas_wh,width:report.width_in,height:report.height_in,reportKey:'export'},
    {stem:'real_scene',wh:[left.width,left.height],width:report.width_in*left.width/report.canvas_wh[0],height:report.height_in,reportKey:'real_scene_export'},
    {stem:'native_tradeoff',wh:[right.width,right.height],width:3.25,height:3.25*right.height/right.width,reportKey:'standalone_export'}
  ]){
    const [w,h]=spec.wh;
    const svg=await fs.readFile(path.join(root,`${spec.stem}.svg`),'utf8');
    const page=await browser.newPage({viewport:{width:w,height:h},deviceScaleFactor:1});
    await page.setContent(`<!doctype html><meta charset="utf-8"><style>@page{size:${spec.width}in ${spec.height}in;margin:0}html,body{margin:0;padding:0;width:${w}px;height:${h}px}svg{display:block;width:${w}px;height:${h}px}@media print{html,body,svg{width:${spec.width}in;height:${spec.height}in}}</style>${svg}`);
    await page.evaluate(()=>document.fonts.ready);
    await page.locator('svg image').evaluateAll(async nodes=>Promise.all(nodes.map(n=>new Promise((resolve,reject)=>{const i=new Image();i.onload=resolve;i.onerror=reject;i.src=n.getAttribute('href')}))));
    const texts=await page.locator('svg text').evaluateAll(nodes=>nodes.map(n=>{
      const b=n.getBBox(),m=n.getScreenCTM();const p=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
      return {text:n.textContent,x:Math.min(...p.map(v=>v.x)),y:Math.min(...p.map(v=>v.y)),right:Math.max(...p.map(v=>v.x)),bottom:Math.max(...p.map(v=>v.y))};
    }));
    const overflow=texts.filter(t=>t.x<-.1||t.y<-.1||t.right>w+.1||t.bottom>h+.1);
    if(overflow.length)throw new Error(`${spec.stem} text overflow `+JSON.stringify(overflow));
    await page.screenshot({path:path.join(root,`${spec.stem}.png`)});
    await page.pdf({path:path.join(root,`${spec.stem}.pdf`),preferCSSPageSize:true,printBackground:true,margin:{top:0,bottom:0,left:0,right:0}});
    const result={preview_px:[w,h],width_in:spec.width,height_in:spec.height,text_overflow:overflow,editable_texts:texts.length,raster_images:await page.locator('svg image').count(),text_boxes:texts};
    report[spec.reportKey]=result;
    console.log(JSON.stringify({file:spec.stem,preview_px:[w,h],text_overflow:overflow.length,editable_texts:texts.length,raster_images:result.raster_images}));
    await page.close();
  }
  await fs.writeFile(path.join(root,'layout_report.json'),JSON.stringify(report,null,2));
}finally{await browser.close()}

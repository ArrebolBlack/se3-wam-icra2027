/** Build the publication SVG as native PowerPoint objects with Artifact Tool.
 * Usage: bundled node build_fig2_pptx.mjs --work-dir ABS --runtime-modules ABS
 *        --python ABS --skill-dir ABS [--output ABS]
 * The source SVG/PDF and manuscript are never regenerated or modified.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';

const args = Object.fromEntries(Array.from({ length: (process.argv.length-2)/2 }, (_, i) =>
  [process.argv[2+2*i].replace(/^--/, ''), process.argv[3+2*i]]));
for (const key of ['work-dir', 'runtime-modules', 'python', 'skill-dir']) {
  if (!args[key]) throw new Error(`Missing --${key}`);
}
const sourceDir = path.dirname(fileURLToPath(import.meta.url));
const workspaceDir = path.resolve(args['work-dir']);
const buildDir = path.join(workspaceDir, 'build');
const outputDir = path.join(workspaceDir, 'output');
await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(outputDir, { recursive: true });
const requireRuntime = createRequire(path.join(args['runtime-modules'], '..', 'package.json'));
process.env.RUNTIME_NODE_MODULES = args['runtime-modules'];
const { Presentation, PresentationFile } = await import(pathToFileURL(requireRuntime.resolve('@oai/artifact-tool')).href);
const { finalizePresentation } = await import(pathToFileURL(path.join(args['skill-dir'], 'container_tools/artifact_tool_utils.mjs')).href);
const python = (...parameters) => console.log(execFileSync(args.python, [path.join(sourceDir, 'pptx_scene.py'), ...parameters], { encoding: 'utf8' }).trim());
const scenePath = path.join(buildDir, 'scene.json');
python('prepare', path.join(sourceDir, 'fig2_se3wam.svg'), scenePath);
const scene = JSON.parse(await fs.readFile(scenePath, 'utf8'));
const presentation = Presentation.create({ slideSize: { width: scene.width, height: scene.height } });
const slide = presentation.slides.add();
slide.background.fill = '#FFFFFF';
slide.speakerNotes.text = 'Publication refinement v21: input/output projections and Blender flow context. References: WorldBridge Fig.3 (arXiv:2610.40748v1), SelfWAM Fig.2 (2608.00725v1), LAW Fig.5 (2610.23334v2), Faster-WAM Fig.2(b) (2608.04404v1). S/M share World FFN; A uses its own FFN and two scalar-flow-time-conditioned AdaLNs. QKV and attention-output weights are shared across S/M/A. Attention permissions are S:S, M:S/M, A:S/M/A. Residuals are shown after attention output and FFN. The entire coupled layer repeats. World conditioning is differentiable during training. Inference caches each layer input projected S/M K/V and iterates only Action. RGB and flow context are Blender renderings of the recorded frame-29 state; flow vectors retain the recorded supervision and remain separate native annotations. Input encoders and output decoders represent existing learned projections/readouts, not additional backbones. The shared QKV box contains representative token blocks of the same size as input tokens. The native context scene is assets/blender/flow_context.blend. Depth, SE(3) and flow examples are recorded supervision references. Decoded geometry is not an Action input. No fixed token count, layer count or solver-step count is asserted. The adopted manuscript has not been changed.';
for (const [index, obj] of (args['reuse-native'] ? [] : scene.objects).entries()) {
  const [x, y, width, height] = obj.box;
  const position = { left: x, top: y, width: Math.max(width, 0.001), height: Math.max(height, 0.001) };
  const line = { fill: obj.stroke, width: obj.stroke === 'none' ? 0 : obj.sw, style: obj.dash.length ? 'dashed' : 'solid' };
  if (obj.kind === 'image') {
    const buffer = Buffer.from(obj.data.split(',')[1], 'base64');
    slide.images.add({ name: obj.id, alt: obj.id, blob: buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset+buffer.byteLength), contentType: 'image/png', fit: 'contain', position });
  } else if (obj.kind === 'text') {
    const shape = slide.shapes.add({ geometry: 'textbox', name: obj.id, position: { ...position, rotation: obj.rotation }, fill: 'none', line: { fill: 'none', width: 0, style: 'solid' } });
    shape.text = obj.text;
    shape.text.style = { typeface: 'Arial', fontSize: obj.size, bold: obj.bold, italic: obj.italic, color: obj.fill, alignment: 'left', verticalAlignment: 'top', wrap: 'none', autoFit: 'none', insets: 0 };
  } else if (obj.kind === 'rect' || obj.kind === 'circle') {
    slide.shapes.add({ geometry: obj.kind === 'circle' ? 'ellipse' : obj.radius ? 'roundRect' : 'rect', name: obj.id, position, fill: obj.fill, line, ...(obj.radius ? { borderRadius: obj.radius } : {}) });
  } else {
    const commands = obj.points.map(([px, py], i) => ({ [i === 0 ? 'moveTo' : 'lineTo']: { x: px-x, y: py-y } }));
    if (obj.kind === 'polygon') commands.push({ close: {} });
    slide.shapes.add({ geometry: 'custom', name: obj.id, position, fill: obj.fill, line,
      customPaths: [{ width: position.width, height: position.height, commands }] });
  }
  if ((index+1) % 2500 === 0) console.log(`Native objects: ${index+1}/${scene.objects.length}`);
}
const rawPath = path.join(buildDir, 'native-objects.pptx');
if (args['reuse-native']) await fs.copyFile(path.resolve(args['reuse-native']), rawPath);
else await (await PresentationFile.exportPptx(presentation)).save(rawPath);
const groupedPath = path.join(buildDir, 'native-grouped.pptx');
python('refine', scenePath, rawPath, groupedPath);
const finalPath = path.join(outputDir, 'fig2_se3wam.pptx');
const result = await finalizePresentation({
  workspaceDir, candidatePath: groupedPath, finalPath,
  pythonExecutable: args.python,
  integrityValidatorPath: path.join(args['skill-dir'], 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(args['skill-dir'], 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '15240000,9048750', '--validate-bullet-geometry', '--validate-heading-fit'],
  explicitTotalSlideCount: 1,
  requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: 'design', families: ['Arial'] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(buildDir, 'validation.json'),
});
python('verify', scenePath, finalPath);
if (args.output) await fs.copyFile(finalPath, path.resolve(args.output));
console.log(JSON.stringify({ finalPath, copiedTo: args.output ?? null,
  packageIntegrity: result.packageIntegrity.status,
  layoutFindings: result.presentationLayout.findingCount,
  firstPartyImport: result.firstPartyImport.passed }));

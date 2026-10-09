// Run the 3D bench's gunshot scenario without a browser and print its log.
//
//     node gunshot_run.mjs > gunshot-run.txt
//
// The bench page (../zeit-bench-3d.html) runs Lane A and Lane B as real DSP code
// at 16 kHz. This script loads the same two source files the page is built from
// (src3d/06-dsp.html and 06b-shot.html), runs the seeded shot, and prints every
// event the simulation computed. Nothing in the log is typed by hand.
//
// Lines about how long this computer took to run the simulation are left out:
// they describe the host, not the system. Firmware-link (UART) lines are left
// out too; they arrive half a second later, after the shot is over.
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const src = ['06-dsp.html', '06b-shot.html']
  .map(f => readFileSync(join(here, '..', 'src3d', f), 'utf8')).join('\n');

const driver = `
const __d = runShot();
const __strip = s => s.replace(/<[^>]+>/g, '');
const __out = [];
__out.push('ANVIL bench -- one gunshot traced through both lanes (16 kHz DSP simulation)');
__out.push('scenario  shooter ' + SHOT.RANGE + ' m | round ' + SHOT.V_BULLET + ' m/s | passes ' + SHOT.MISS + ' m from the head | seed ' + SHOT.SEED);
__out.push('');
for (const e of __d.events) {
  if (e.k === 'UART' || e.k === 'END' || /of compute per frame/.test(e.text)) continue;
  __out.push(('T+' + e.t.toFixed(2)).padStart(9) + ' ms  ' + e.k.padEnd(4) + '  ' + __strip(e.text));
}
export default __out.join('\\n');
`;
const tmp = join(mkdtempSync(join(tmpdir(), 'anvil-shot-')), 'shot.mjs');
writeFileSync(tmp, src + '\n' + driver);
const { default: log } = await import(pathToFileURL(tmp).href);
console.log(log);

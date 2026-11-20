// news-image-20261120 entry (Node 22, standard library only).
// The image is drawn in code by draw.py and shipped as entry.png beside
// this file; this program copies it to the grader's output directory.
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const source = new URL('./entry.png', import.meta.url).pathname;
const target = join(outDir, 'entry.png');
if (!existsSync(source)) {
  throw new Error(`entry.png not found next to main.ts (${source})`);
}
mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);

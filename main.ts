// news-image-20261120 — entry runner (Node 22, standard library only).
// draw.py renders entry.png next to this file; this program copies that
// image into the grader's output directory, byte for byte.
// Local check: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const entryDir = dirname(fileURLToPath(import.meta.url));
const source = join(entryDir, 'entry.png');
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

if (!existsSync(source)) {
  throw new Error(`entry.png missing next to main.ts: ${source}`);
}
// The destination directory is the target file's own parent, so the
// copy works whether the output dir already exists or not.
mkdirSync(dirname(target), { recursive: true });
copyFileSync(source, target);

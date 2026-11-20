// Entry program for the gta6-meme-x-01 bounty: copy POST.json from this
// repository to the output directory. That is all it does; the house reads
// the X post itself. No network, no clock, no files outside the repository.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? join(here, "out");
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "POST.json"), join(outDir, "POST.json"));

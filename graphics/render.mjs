import { readFile, mkdir, writeFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";
import { bundle } from "@remotion/bundler";
import { renderFrames, selectComposition } from "@remotion/renderer";

const root = path.dirname(fileURLToPath(import.meta.url));
const requests = JSON.parse(await readFile(process.argv[2], "utf8"));
const built = path.join(root, "bundle");
const serveUrl = existsSync(built)
  ? built
  : await bundle({
      entryPoint: path.join(root, "src/index.tsx"),
      enableCaching: false,
    });
for (const { props, outputDir } of requests) {
  await mkdir(outputDir, { recursive: true });
  const options = {
    serveUrl,
    id: "GraphicInsert",
    inputProps: props,
    logLevel: "error",
  };
  const composition = await selectComposition(options);
  await renderFrames({
    serveUrl,
    composition,
    inputProps: props,
    outputDir,
    imageFormat: "png",
    imageSequencePattern: "frame-[frame].[ext]",
    concurrency: 2,
    logLevel: "error",
  });
  const frames = (await readdir(outputDir))
    .filter((f) => /^frame-\d+\.png$/.test(f))
    .sort();
  if (frames.length !== composition.durationInFrames)
    throw new Error("Incomplete graphic render");
  await writeFile(
    path.join(outputDir, "manifest.json"),
    JSON.stringify({ fps: 30, frames, props, renderer: "Remotion 4.0.539" }),
  );
  process.stdout.write(
    JSON.stringify({ outputDir, frameCount: frames.length }) + "\n",
  );
}

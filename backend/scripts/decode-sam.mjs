import {readFile, writeFile, mkdir} from "node:fs/promises";
import {join} from "node:path";
import {parseVideoStream, recordsOfKind, decodeMaskToRaster} from "@meta-sam/parser";

const [inputPath, outputDir] = process.argv.slice(2);
const input = JSON.parse(await readFile(inputPath, "utf8"));
async function* events() {
  const lane = {item_id:"mask", output_index:0, content_index:0};
  yield {type:"response.output_text.delta", ...lane, delta:input.text};
  yield {type:"response.output_text.done", ...lane, text:input.text};
  yield {type:"response.completed", response:{id:"local-decode",status:"completed",output:[
    {id:"mask",type:"message",role:"assistant",content:[{type:"output_text",text:input.text}]}]}};
}
const result = await parseVideoStream(events()).finalResult;
if(result.outcome.status!=="completed" || result.diagnostics.length) {
  throw new Error("SAM returned malformed segmentation output.");
}
await mkdir(outputDir,{recursive:true});
const records=[];
for (const record of recordsOfKind(result.records,"mask")) {
  const id=String(record.objectId), frame=record.frame?.frameIndex??0;
  const mask=record.mask, bounds=record.bounds;
  if(!/^\d{1,8}$/.test(id)||frame<0||frame>=600||mask.width*mask.height>input.width*input.height*4) {
    throw new Error("Invalid SAM frame or mask dimensions.");
  }
  const raster=decodeMaskToRaster(mask);
  const filename=`${id}-${frame}.bin`;
  await writeFile(join(outputDir,filename),raster);
  records.push({id,frame,width:mask.width,height:mask.height,bounds,filename});
}
await writeFile(join(outputDir,"records.json"),JSON.stringify(records));

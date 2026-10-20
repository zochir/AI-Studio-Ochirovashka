const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');

const html = fs.readFileSync(process.argv[2], 'utf8');
assert.match(html, /APK сам по себе не содержит готовую модель для рисования/, "the UI must disclose that real image generation requires a provider or model");
assert.match(html, /Запросы к внешнему генератору начинаются только после нажатия/, "the UI must explain when external generation is triggered");
const start = html.lastIndexOf('<script>');
const end = html.indexOf('</script>', start);
assert(start >= 0 && end > start, 'Comic Studio inline script must exist');
const comicSource = html.slice(start + 8, end);
const nativeAutosaveSnippet = 'panels[0].imageUrl=String(data);render(panels);saveProject();$("comicStatus").textContent="Первый кадр создан локально на телефоне и сохранён в проекте.";';
assert.equal(comicSource.split(nativeAutosaveSnippet).length - 1, 2, 'both standalone native first-frame success handlers must save the project');
assert.equal(comicSource.includes('panels[0].imageUrl=String(data);render(panels);$("comicStatus").textContent="Первый кадр создан локально на телефоне."'), false, 'native first-frame success must not report success before autosaving');
assert.match(comicSource, /data-panel-field="title"/, 'each panel must expose an editable title');
assert.match(comicSource, /data-panel-field="scene"/, 'each panel must expose an editable scene description');
assert.match(comicSource, /data-panel-field="dialogue"/, 'each panel must expose an editable dialogue field');
assert.match(comicSource, /panels\[i\]\[field\]=input\.value/, 'panel edits must update the project data model');
assert.match(comicSource, /async function generateNativeImages\(retryOnly=false\)/, 'native generation must support retry-only mode');
assert.match(comicSource, /if\(nativeStatus==="MODEL_PRESENT"\)return generateNativeImages\(true\)/, 'retry button must route failed frames to the native generator when the local model is installed');
assert.match(comicSource, /const indices=retryOnly\?Array\.from\(failedImageFrames\)/, 'native retry must process only failed frames');

class Element {
  constructor(id) {
    this.id = id; this.value = ''; this.textContent = ''; this.innerHTML = '';
    this.listeners = {}; this.disabled = false; this.focused = false;
  }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  click() { if (this.listeners.click) return this.listeners.click({ target: this }); this.clicked = true; }
  focus() { this.focused = true; }
  getContext(kind) { if (kind !== '2d') return null; return { fillStyle: '', fillRect() {}, drawImage() {} }; }
  toBlob(callback, type) { callback(new Blob([new Uint8Array([137, 80, 78, 71])], { type })); }
}
const ids = ['comicReferenceFile', 'comicReferenceStatus', 'comicStory', 'comicCharacterName', 'comicCharacterLook', 'comicAddCharacter', 'comicCharacters', 'comicMood', 'comicComposition', 'comicCount', 'comicStyle', 'comicEndpoint', 'comicModel', 'comicKey',
  'comicImageEndpoint', 'comicImageModel', 'comicImageKey', 'comicLocalEndpoint', 'comicWorkflow', 'comicCheckLocal', 'comicBuildWorkflow', 'comicGenerateLocal', 'comicGenerate', 'comicGenerateImages',
  'comicRetryImages', 'comicSave', 'comicLoad', 'comicExportProject', 'comicImportProject', 'comicProjectFile', 'comicExport', 'comicExportPng', 'comicExportHtml', 'comicStatus', 'comicPanels'];
const els = Object.fromEntries(ids.map(id => [id, new Element(id)]));
els.comicCount.value = '4';
els.comicCharacters.value = 'Лея: рыжие короткие волосы, зелёный плащ, родинка под левым глазом.';
els.comicMood.value = 'Эпическая и масштабная';
els.comicComposition.value = 'Динамичный ракурс и движение';
els.comicLocalEndpoint.value = 'http://comfy.test:8188';
els.comicWorkflow.value = '{"1":{"inputs":{"text":"__PROMPT__"}}}';
els.comicStyle.value = 'Приключение';
const anchors = [];
const blobs = [];
const saved = new Map();
let failingImageRequests = 0;
let externalImageRequests = 0;
let confirmNext = true;
let confirmationCalls = 0;
let lastConfirmationMessage = '';
let localPromptRequests = 0;
let localLastRequest = null;
let localFailNextPrompt = false;
const document = {
  getElementById: id => els[id] || (els[id] = new Element(id)),
  createElement: tag => { const el = new Element(tag); anchors.push(el); return el; }
};
class FakeImage {
  set src(value) { this._src = value; if (this.onload) this.onload(); }
  get src() { return this._src; }
}
class FakeFileReader {
  readAsText(file) { this.result = file.content; if (this.onload) this.onload(); }
  readAsDataURL(file) { this.result = 'data:image/png;base64,cmVm'; if (this.onload) this.onload(); }
}
class FakeFormData { constructor(){this.values=[];} append(...args){this.values.push(args);} }
const context = {
  document, console, Blob, Image: FakeImage, FileReader: FakeFileReader, FormData: FakeFormData,
  confirm: (message) => { confirmationCalls++; lastConfirmationMessage = String(message); return confirmNext; },
  URL: { createObjectURL: blob => { blobs.push(blob); return 'blob:comic-test'; }, revokeObjectURL: () => {} },
  localStorage: { setItem: (k,v) => saved.set(k,v), getItem: k => saved.has(k) ? saved.get(k) : null },
  btoa: value => Buffer.from(value, 'binary').toString('base64'),
  setTimeout: (fn, ms) => { if (ms === 8000 || ms >= 10000) return 999999; fn(); return 1; }, clearTimeout: () => {},
  fetch: async (url, options) => {
    const request = options && typeof options.body === 'string' ? JSON.parse(options.body) : {};
    if (url === 'https://api.test/v1/chat/completions') {
      if (options.headers.Authorization) assert.equal(options.headers.Authorization, 'Bearer temporary-test-key');
      assert.equal(request.model, 'test-model');
      return { ok: true, json: async () => ({ choices: [{ message: { content: '[{"title":"AI panel","scene":"AI scene","dialogue":"Hello"}]' } }] }) };
    }
    if (url === 'https://images.test/v1/images/generations') {
      externalImageRequests++;
      if (options.headers.Authorization) assert.equal(options.headers.Authorization, 'Bearer image-test-key');
      assert.equal(request.model, 'image-test-model');
      assert.match(request.prompt, /AI scene/);
      assert.match(request.prompt, /Лея: рыжие короткие волосы/);
      assert.match(request.prompt, /Динамичный ракурс/);
      assert.match(request.prompt, /immutable model-sheet canon/);
      assert.match(request.prompt, /EPIC BATTLE DIRECTION/, 'epic mood should add cinematic battle direction to image prompts');
      assert.match(request.prompt, /Seed for repeatable rerenders/);
      assert.equal(Number.isInteger(request.seed), true, "image request should include a deterministic per-panel seed");
      return { ok: true, json: async () => ({ data: [{ b64_json: 'ZmFrZQ==' }] }) };
    }
    if (url === 'https://images.test/fail-first') {
      failingImageRequests++;
      if (failingImageRequests === 1) return { ok: false, status: 503, text: async () => JSON.stringify({ error: { message: 'temporary provider overload' } }) };
      if (failingImageRequests === 2) assert.match(request.prompt, /Second scene/);
      if (failingImageRequests === 3) assert.match(request.prompt, /First scene/);
      return { ok: true, json: async () => ({ data: [{ b64_json: failingImageRequests === 3 ? 'Zmlyc3Q=' : 'c2Vjb25k' }] }) };
    }
    if (url.startsWith('https://gen.pollinations.ai/image/')) {
      externalImageRequests++;
      assert.equal(options.method, 'GET');
      assert.equal(options.headers.Authorization, 'Bearer pollinations-test-key');
      assert.match(decodeURIComponent(url), /AI scene/);
      assert.match(url, /model=flux/);
      assert.match(url, /seed=\d+/);
      return { ok: true, blob: async () => new Blob([new Uint8Array([1,2,3,4])], {type:'image/jpeg'}) };
    }
    if (url === 'http://comfy.test:8188/system_stats') {
      return { ok: true, json: async () => ({ devices: [{ name: 'test-device' }] }) };
    }
    if (url === 'http://comfy.test:8188/object_info/CheckpointLoaderSimple') {
      return { ok: true, json: async () => ({ CheckpointLoaderSimple: { input: { required: { ckpt_name: [['realisticVision.safetensors', 'sd15.safetensors'], {}] } } } }) };
    }
    if (url === 'data:image/png;base64,cmVm') return { ok: true, blob: async () => new Blob([new Uint8Array([1,2,3])], {type:'image/png'}) };
    if (url === 'http://comfy.test:8188/upload/image') { assert.equal(options.method,'POST'); assert.ok(options.body instanceof FakeFormData); return {ok:true,json:async()=>({name:'character-reference.png',subfolder:''})}; }
    if (url === 'http://comfy.test:8188/prompt') {
      localPromptRequests++;
      localLastRequest = request;
      assert.match(JSON.stringify(request), /AI scene|First scene|Second scene/);
      if (localFailNextPrompt) { localFailNextPrompt = false; return { ok: false, status: 503, text: async () => 'temporary local overload' }; }
      return { ok: true, json: async () => ({ prompt_id: 'local-job-1' }) };
    }
    if (url === 'http://comfy.test:8188/history/local-job-1') {
      return { ok: true, json: async () => ({ 'local-job-1': { outputs: { '9': { images: [{ filename: 'comic.png', subfolder: '', type: 'output' }] } } } }) };
    }
    if (url === 'http://comfy.test:8188/view?filename=portable.png&subfolder=&type=output' || url === 'http://comfy.test:8188/view?filename=comic.png&subfolder=&type=output') {
      return { ok: true, blob: async () => new Blob([new Uint8Array([9,8,7,6])], {type:'image/png'}) };
    }
    throw new Error('Unexpected network endpoint: ' + url);
  },
  JSON, String, Number, Array, Math, Promise, URLSearchParams
};
vm.runInNewContext(html.slice(start + 8, end), context, { timeout: 2000 });

(async () => {
  els.comicGenerate.click();
  assert.match(els.comicStatus.textContent, /Введите идею или сюжет/);
  els.comicStory.value = 'Героиня ведёт армию через горы. Она замечает вражеский легион. Начинается сражение. Герои одерживают победу.';
  els.comicGenerate.click();
  assert.equal((els.comicPanels.innerHTML.match(/<article/g) || []).length, 4);
  assert.match(els.comicStatus.textContent, /локальн/);
  assert.match(els.comicPanels.innerHTML, /Визуальный этап сражения/, 'battle stories should become a staged cinematic combat sequence');
  await els.comicExport.click();
  assert.equal(anchors.length, 1);
  assert.equal(anchors[0].download, 'comic-storyboard.svg');
  assert.equal(anchors[0].clicked, true);
  const exportedSvg = await blobs[0].text();
  assert.match(exportedSvg, /<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg"/);
  assert.match(exportedSvg, /<tspan/);
  assert.doesNotMatch(exportedSvg, /foreignObject/, 'export should not rely on HTML foreignObject rendering');
  assert.match(exportedSvg, /Иллюстрация не создана/);
  await els.comicExportPng.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.equal(anchors.at(-1).download, 'comic-storyboard.png');
  assert.match(els.comicStatus.textContent, /Экспорт PNG подготовлен/);
  assert.ok(blobs.some(blob => blob.type === 'image/png'), 'PNG export should create an image/png blob');

  els.comicEndpoint.value = 'https://api.test/v1/chat/completions';
  els.comicModel.value = 'test-model';
  els.comicKey.value = 'temporary-test-key';
  els.comicGenerate.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(els.comicPanels.innerHTML, /AI panel/);
  assert.match(els.comicStatus.textContent, /Сценарий создан ИИ/);
  // Test external image generation without the configured local ComfyUI endpoint.
  els.comicLocalEndpoint.value = '';
  els.comicWorkflow.value = '';
  els.comicImageEndpoint.value = 'https://images.test/v1/images/generations';
  els.comicImageModel.value = 'image-test-model';
  els.comicImageKey.value = 'image-test-key';
  els.comicGenerateImages.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(els.comicPanels.innerHTML, /data:image\/png;base64,ZmFrZQ==/);
  assert.match(els.comicStatus.textContent, /создано 1 изображений/);
  assert.equal(confirmationCalls, 1, 'external image generation must ask for explicit confirmation');
  assert.match(lastConfirmationMessage, /1 запрос\(ов\) генерации/, 'confirmation must disclose the number of frame requests');
  assert.match(lastConfirmationMessage, /могут расходовать кредиты или быть платными/, 'confirmation must disclose possible costs');
  const requestsBeforeDecline = externalImageRequests;
  confirmNext = false;
  await els.comicGenerateImages.click();
  assert.equal(externalImageRequests, requestsBeforeDecline, 'declining cost confirmation must send no external image requests');
  assert.match(els.comicStatus.textContent, /Генерация отменена: запросы не отправлялись/);
  confirmNext = true;
  await els.comicExport.click();
  const exportedImageSvg = await blobs[blobs.length - 1].text();
  assert.match(exportedImageSvg, /<image[^>]+href="data:image\/png;base64,ZmFrZQ=="/);
  assert.match(exportedImageSvg, /Hello/);
  // Restore optional local-provider settings before verifying they survive project save/load.
  els.comicLocalEndpoint.value = 'http://comfy.test:8188';
  els.comicWorkflow.value = '{"1":{"inputs":{"text":"__PROMPT__"}}}';
  els.comicSave.click();
  assert.match(els.comicStatus.textContent, /Проект сохранён/);
  const storedProject = [...saved.values()][0];
  assert.match(storedProject, /images\.test/);
  assert.match(storedProject, /comfy\.test/);
  assert.match(storedProject, /Лея: рыжие короткие волосы/);
  assert.match(storedProject, /Эпическая и масштабная/);
  assert.doesNotMatch(storedProject, /temporary-test-key|image-test-key/);
  els.comicImageEndpoint.value = '';
  els.comicLocalEndpoint.value = '';
  els.comicWorkflow.value = '';
  els.comicStory.value = 'перезаписанный сюжет';
  els.comicPanels.innerHTML = '';
  els.comicLoad.click();
  assert.equal(els.comicStory.value, 'Героиня ведёт армию через горы. Она замечает вражеский легион. Начинается сражение. Герои одерживают победу.');
  assert.equal(els.comicImageEndpoint.value, 'https://images.test/v1/images/generations');
  assert.equal(els.comicLocalEndpoint.value, 'http://comfy.test:8188');
  assert.equal(els.comicWorkflow.value, '{"1":{"inputs":{"text":"__PROMPT__"}}}');
  assert.equal(els.comicCharacters.value, 'Лея: рыжие короткие волосы, зелёный плащ, родинка под левым глазом.');
  assert.equal(els.comicMood.value, 'Эпическая и масштабная');
  assert.equal(els.comicComposition.value, 'Динамичный ракурс и движение');
  assert.match(els.comicPanels.innerHTML, /data:image\/png;base64,ZmFrZQ==/);
  assert.match(els.comicStatus.textContent, /Проект загружен/);
  els.comicCheckLocal.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(els.comicStatus.textContent, /ComfyUI доступен/);
  await els.comicBuildWorkflow.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  const generatedWorkflow = JSON.parse(els.comicWorkflow.value);
  assert.equal(generatedWorkflow['1'].class_type, 'CheckpointLoaderSimple');
  assert.equal(generatedWorkflow['1'].inputs.ckpt_name, 'realisticVision.safetensors');
  assert.equal(generatedWorkflow['2'].inputs.text, '__PROMPT__');
  assert.equal(generatedWorkflow['5'].inputs.seed, '__SEED__');
  assert.equal(generatedWorkflow['7'].class_type, 'SaveImage');
  assert.match(els.comicStatus.textContent, /Базовый workflow создан/);
  els.comicWorkflow.value = '{"1":{"inputs":{"text":"static prompt"}}}';
  els.comicGenerateLocal.click();
  assert.match(els.comicStatus.textContent, /не содержит __PROMPT__/);
  els.comicWorkflow.value = '{"1":{"inputs":{"text":"__PROMPT__"}}}';
  els.comicReferenceFile.files = [{type:'image/png',size:10}];
  els.comicReferenceFile.listeners.change({target:els.comicReferenceFile});
  els.comicWorkflow.value = '{"1":{"inputs":{"image":"__CHARACTER_REFERENCE__","text":"__PROMPT__","seed":"__SEED__"}}}';
  els.comicGenerateLocal.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  console.log('LOCAL STATUS:', els.comicStatus.textContent);
  assert.match(JSON.stringify(localLastRequest), /character-reference\.png/);
  assert.match(els.comicPanels.innerHTML, /data:image\/png;base64,CQgHBg==/);
  assert.match(els.comicStatus.textContent, /ComfyUI завершил генерацию/);
  // Local OpenAI-compatible endpoints may not require API keys.
  els.comicKey.value = '';
  els.comicGenerate.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(els.comicStatus.textContent, /Сценарий создан ИИ/);
  els.comicImageKey.value = '';
  // Keep this assertion on the external API path; the local-first path is tested below.
  els.comicLocalEndpoint.value = '';
  els.comicWorkflow.value = '';
  els.comicGenerateImages.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(els.comicStatus.textContent, /создано 1 изображений/);
  els.comicImageEndpoint.value = 'https://gen.pollinations.ai/image/';
  els.comicImageModel.value = 'flux';
  els.comicImageKey.value = 'pollinations-test-key';
  await els.comicGenerateImages.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(els.comicStatus.textContent, /создано 1 изображений/);
  assert.ok(els.comicPanels.innerHTML.includes('data:image/jpeg;base64,AQIDBA=='));
  assert.equal(els.comicImageEndpoint.value, 'https://gen.pollinations.ai/image/');

  els.comicCharacterName.value = 'Тар';
  els.comicCharacterLook.value = 'синяя броня, серебряные глаза, шрам над бровью';
  els.comicAddCharacter.click();
  assert.match(els.comicCharacters.value, /Тар — синяя броня, серебряные глаза, шрам над бровью/);
  assert.match(els.comicStatus.textContent, /Карточка персонажа «Тар» добавлена/);
  await els.comicExportProject.click();
  assert.match(els.comicStatus.textContent, /Проект JSON экспортирован/);
  assert.equal(anchors.at(-1).download, 'comic-project.json');
  const portable = {format:'ai-comic-studio-project',version:1,story:'Импортированный сюжет',characters:'Герой — плащ',mood:'Меланхоличная',composition:'Портрет и эмоции',count:'3',style:'Манга',panels:[{title:'Первый кадр',scene:'Проверка импорта',dialogue:'Готово',imageUrl:'data:image/png;base64,ZmFrZQ=='}]};
  els.comicProjectFile.listeners.change({target:{files:[{content:JSON.stringify(portable)}],value:'selected.json'}});
  assert.equal(els.comicStory.value, 'Импортированный сюжет');
  assert.match(els.comicPanels.innerHTML, /Проверка импорта/);
  assert.match(els.comicStatus.textContent, /Проект импортирован: 1 кадров/);
  els.comicProjectFile.listeners.change({target:{files:[{content:'{}'}],value:'bad.json'}});
  assert.match(els.comicStatus.textContent, /неподдерживаемый формат/);
  els.comicLocalEndpoint.value = '';
  els.comicWorkflow.value = '';
  const retryProject = {format:'ai-comic-studio-project',version:1,story:'Two scenes',characters:'Hero',mood:'Adventure',composition:'Wide',count:'2',style:'Comic',panels:[{title:'First',scene:'First scene',dialogue:'',imageUrl:''},{title:'Second',scene:'Second scene',dialogue:'',imageUrl:''}]};
  els.comicProjectFile.listeners.change({target:{files:[{content:JSON.stringify(retryProject)}],value:'retry.json'}});
  els.comicImageEndpoint.value = 'https://images.test/fail-first';
  els.comicImageModel.value = 'test-model';
  await els.comicGenerateImages.click();
  assert.equal(failingImageRequests, 2, 'queue must continue after the first frame fails');
  assert.match(els.comicStatus.textContent, /завершена частично: в этом запуске готово 1 из 2/);
  assert.match(els.comicStatus.textContent, /temporary provider overload/);
  assert.match(els.comicPanels.innerHTML, /data:image\/png;base64,c2Vjb25k/);
  assert.equal(els.comicRetryImages.disabled, false, 'retry button should enable after a frame failure');
  await els.comicRetryImages.click();
  assert.equal(failingImageRequests, 3, 'retry action must request only the failed first frame');
  assert.match(els.comicStatus.textContent, /создано 1 изображений. Неудачных кадров осталось: 0/);
  assert.equal(els.comicRetryImages.disabled, true, 'retry button should disable when no failed frames remain');
  // ComfyUI retries must use the local provider and only requeue failed local frames.
  els.comicLocalEndpoint.value = 'http://comfy.test:8188';
  els.comicWorkflow.value = '{"1":{"inputs":{"text":"__PROMPT__","seed":"__SEED__"}}}';
  const beforeLocalQueue = localPromptRequests;
  localFailNextPrompt = true;
  await els.comicGenerateLocal.click();
  assert.equal(localPromptRequests, beforeLocalQueue + 2, 'local queue should attempt both frames even if the first fails');
  assert.match(els.comicStatus.textContent, /завершена частично/);
  assert.equal(els.comicRetryImages.disabled, false, 'local failure should enable retry');
  const beforeLocalRetry = localPromptRequests;
  await els.comicRetryImages.click();
  assert.equal(localPromptRequests, beforeLocalRetry + 1, 'local retry should request only the failed frame');
  assert.match(els.comicStatus.textContent, /Повтор локальных кадров завершён/);
  assert.equal(typeof localLastRequest.prompt["1"].inputs.seed, "number", "ComfyUI __SEED__ marker must become a numeric sampler seed");
  assert.notEqual(localLastRequest.prompt["1"].inputs.seed, "__SEED__");
  assert.equal(els.comicRetryImages.disabled, true, 'local retry button should disable when failures are cleared');
  els.comicAddCharacter.click();
  assert.match(els.comicStatus.textContent, /укажите имя и описание внешности/);
  const externalImageProject = {format:'ai-comic-studio-project',version:1,story:'Portable image test',characters:'Hero',mood:'Adventure',composition:'Wide',count:'1',style:'Comic',panels:[{title:'Local frame',scene:'Local generated image',dialogue:'Сохрани этот момент',imageUrl:'http://comfy.test:8188/view?filename=portable.png&subfolder=&type=output'}]};
  els.comicProjectFile.listeners.change({target:{files:[{content:JSON.stringify(externalImageProject)}],value:'external.json'}});
  await els.comicExportProject.click();
  const portableJson = await blobs.at(-1).text();
  assert.match(portableJson, /data:image\/png;base64,CQgHBg==/, 'portable project export should embed accessible ComfyUI images');
  assert.match(els.comicPanels.innerHTML, /comfy\.test:8188\/view\?/, 'export should not mutate the live project image URL');
  assert.match(els.comicStatus.textContent, /Все доступные изображения перенесены внутрь файла/);
  await els.comicExportHtml.click();
  const htmlComic = await blobs.at(-1).text();
  assert.equal(anchors.at(-1).download, 'comic-reader.html');
  assert.match(htmlComic, /data:image\/png;base64,CQgHBg==/, 'standalone HTML comic should embed accessible local images');
  assert.match(htmlComic, /Local generated image/);
  assert.match(htmlComic, /@media print/, 'HTML comic should provide print-to-PDF styles');
  assert.match(htmlComic, /Печать \/ сохранить в PDF/, 'standalone HTML should provide an explicit print-to-PDF button');
  assert.match(htmlComic, /onclick="window\.print\(\)"/, 'print button should invoke the browser print dialog');
  assert.match(htmlComic, /\.toolbar\{display:none!important\}/, 'print toolbar should not appear in printed pages');
  assert.match(htmlComic, /<blockquote>/);
  assert.match(els.comicStatus.textContent, /Автономный HTML-комикс экспортирован/);
  console.log('PASS: storyboard, character bible, OpenAI-compatible and Pollinations image APIs, ComfyUI adapter, SVG and portable JSON/HTML export with embedded local images and print styles');
})().catch(error => { console.error(error); process.exit(1); });

const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');

const html = fs.readFileSync(process.argv[2], 'utf8');
const start = html.lastIndexOf('<script>');
const end = html.indexOf('</script>', start);
assert(start >= 0 && end > start, 'Comic Studio inline script must exist');

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
const ids = ['comicStory', 'comicCharacterName', 'comicCharacterLook', 'comicAddCharacter', 'comicCharacters', 'comicMood', 'comicComposition', 'comicCount', 'comicStyle', 'comicEndpoint', 'comicModel', 'comicKey',
  'comicImageEndpoint', 'comicImageModel', 'comicImageKey', 'comicLocalEndpoint', 'comicWorkflow', 'comicCheckLocal', 'comicGenerateLocal', 'comicGenerate', 'comicGenerateImages',
  'comicRetryImages', 'comicSave', 'comicLoad', 'comicExportProject', 'comicImportProject', 'comicProjectFile', 'comicExport', 'comicExportPng', 'comicStatus', 'comicPanels'];
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
let localPromptRequests = 0;
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
}
const context = {
  document, console, Blob, Image: FakeImage, FileReader: FakeFileReader,
  URL: { createObjectURL: blob => { blobs.push(blob); return 'blob:comic-test'; }, revokeObjectURL: () => {} },
  localStorage: { setItem: (k,v) => saved.set(k,v), getItem: k => saved.has(k) ? saved.get(k) : null },
  btoa: value => Buffer.from(value, 'binary').toString('base64'),
  setTimeout: (fn, ms) => { if (ms === 8000 || ms >= 10000) return 999999; fn(); return 1; }, clearTimeout: () => {},
  fetch: async (url, options) => {
    const request = options && options.body ? JSON.parse(options.body) : {};
    if (url === 'https://api.test/v1/chat/completions') {
      if (options.headers.Authorization) assert.equal(options.headers.Authorization, 'Bearer temporary-test-key');
      assert.equal(request.model, 'test-model');
      return { ok: true, json: async () => ({ choices: [{ message: { content: '[{"title":"AI panel","scene":"AI scene","dialogue":"Hello"}]' } }] }) };
    }
    if (url === 'https://images.test/v1/images/generations') {
      if (options.headers.Authorization) assert.equal(options.headers.Authorization, 'Bearer image-test-key');
      assert.equal(request.model, 'image-test-model');
      assert.match(request.prompt, /AI scene/);
      assert.match(request.prompt, /Лея: рыжие короткие волосы/);
      assert.match(request.prompt, /Динамичный ракурс/);
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
      assert.equal(options.method, 'GET');
      assert.equal(options.headers.Authorization, 'Bearer pollinations-test-key');
      assert.match(decodeURIComponent(url), /AI scene/);
      assert.match(url, /model=flux/);
      return { ok: true, blob: async () => new Blob([new Uint8Array([1,2,3,4])], {type:'image/jpeg'}) };
    }
    if (url === 'http://comfy.test:8188/system_stats') {
      return { ok: true, json: async () => ({ devices: [{ name: 'test-device' }] }) };
    }
    if (url === 'http://comfy.test:8188/prompt') {
      localPromptRequests++;
      assert.match(JSON.stringify(request), /AI scene|First scene|Second scene/);
      if (localFailNextPrompt) { localFailNextPrompt = false; return { ok: false, status: 503, text: async () => 'temporary local overload' }; }
      return { ok: true, json: async () => ({ prompt_id: 'local-job-1' }) };
    }
    if (url === 'http://comfy.test:8188/history/local-job-1') {
      return { ok: true, json: async () => ({ 'local-job-1': { outputs: { '9': { images: [{ filename: 'comic.png', subfolder: '', type: 'output' }] } } } }) };
    }
    throw new Error('Unexpected network endpoint: ' + url);
  },
  JSON, String, Number, Array, Math, Promise, URLSearchParams
};
vm.runInNewContext(html.slice(start + 8, end), context, { timeout: 2000 });

(async () => {
  els.comicGenerate.click();
  assert.match(els.comicStatus.textContent, /Введите идею или сюжет/);
  els.comicStory.value = 'Героиня отправляется в горы. Она замечает загадочный свет. Находит древнюю дверь. Дверь открывается.';
  els.comicGenerate.click();
  assert.equal((els.comicPanels.innerHTML.match(/<article/g) || []).length, 4);
  assert.match(els.comicStatus.textContent, /локальн/);
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
  els.comicImageEndpoint.value = 'https://images.test/v1/images/generations';
  els.comicImageModel.value = 'image-test-model';
  els.comicImageKey.value = 'image-test-key';
  els.comicGenerateImages.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(els.comicPanels.innerHTML, /data:image\/png;base64,ZmFrZQ==/);
  assert.match(els.comicStatus.textContent, /создано 1 изображений/);
  await els.comicExport.click();
  const exportedImageSvg = await blobs[blobs.length - 1].text();
  assert.match(exportedImageSvg, /<image[^>]+href="data:image\/png;base64,ZmFrZQ=="/);
  assert.match(exportedImageSvg, /Hello/);
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
  assert.equal(els.comicStory.value, 'Героиня отправляется в горы. Она замечает загадочный свет. Находит древнюю дверь. Дверь открывается.');
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
  els.comicWorkflow.value = '{"1":{"inputs":{"text":"static prompt"}}}';
  els.comicGenerateLocal.click();
  assert.match(els.comicStatus.textContent, /не содержит __PROMPT__/);
  els.comicWorkflow.value = '{"1":{"inputs":{"text":"__PROMPT__"}}}';
  els.comicGenerateLocal.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  console.log('LOCAL STATUS:', els.comicStatus.textContent);
  assert.match(els.comicPanels.innerHTML, /comfy\.test:8188\/view\?/);
  assert.match(els.comicStatus.textContent, /ComfyUI завершил генерацию/);
  // Local OpenAI-compatible endpoints may not require API keys.
  els.comicKey.value = '';
  els.comicGenerate.click();
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.match(els.comicStatus.textContent, /Сценарий создан ИИ/);
  els.comicImageKey.value = '';
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
  els.comicWorkflow.value = '{"1":{"inputs":{"text":"__PROMPT__"}}}';
  localFailNextPrompt = true;
  await els.comicGenerateLocal.click();
  assert.equal(localPromptRequests, 2, 'local queue should attempt both frames even if the first fails');
  assert.match(els.comicStatus.textContent, /завершена частично/);
  assert.equal(els.comicRetryImages.disabled, false, 'local failure should enable retry');
  const beforeLocalRetry = localPromptRequests;
  await els.comicRetryImages.click();
  assert.equal(localPromptRequests, beforeLocalRetry + 1, 'local retry should request only the failed frame');
  assert.match(els.comicStatus.textContent, /Повтор локальных кадров завершён/);
  assert.equal(els.comicRetryImages.disabled, true, 'local retry button should disable when failures are cleared');
  els.comicAddCharacter.click();
  assert.match(els.comicStatus.textContent, /укажите имя и описание внешности/);
  console.log('PASS: storyboard, character bible, OpenAI-compatible and Pollinations image APIs, ComfyUI adapter, SVG and portable JSON import/export');
})().catch(error => { console.error(error); process.exit(1); });

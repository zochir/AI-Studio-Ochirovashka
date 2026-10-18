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
}
const ids = ['comicStory', 'comicCharacters', 'comicMood', 'comicComposition', 'comicCount', 'comicStyle', 'comicEndpoint', 'comicModel', 'comicKey',
  'comicImageEndpoint', 'comicImageModel', 'comicImageKey', 'comicLocalEndpoint', 'comicWorkflow', 'comicCheckLocal', 'comicGenerateLocal', 'comicGenerate', 'comicGenerateImages',
  'comicSave', 'comicLoad', 'comicExport', 'comicStatus', 'comicPanels'];
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
const document = {
  getElementById: id => els[id] || (els[id] = new Element(id)),
  createElement: tag => { const el = new Element(tag); anchors.push(el); return el; }
};
const context = {
  document, console, Blob,
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
    if (url === 'http://comfy.test:8188/system_stats') {
      return { ok: true, json: async () => ({ devices: [{ name: 'test-device' }] }) };
    }
    if (url === 'http://comfy.test:8188/prompt') {
      assert.match(JSON.stringify(request), /AI scene/);
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
  assert.match(els.comicStatus.textContent, /изображения получены для 1 из 1 кадров/);
  await els.comicExport.click();
  const exportedSvg = await blobs[blobs.length - 1].text();
  assert.match(exportedSvg, /<image[^>]+href="data:image\/png;base64,ZmFrZQ=="/);
  assert.match(exportedSvg, /Hello/);
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
  assert.match(els.comicStatus.textContent, /изображения получены для 1 из 1 кадров/);
  console.log('PASS: storyboard, character bible persistence, visual variation controls, keyed/keyless text and image APIs, ComfyUI validation/integration, SVG export');
})().catch(error => { console.error(error); process.exit(1); });

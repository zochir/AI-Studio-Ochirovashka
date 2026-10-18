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
const ids = ['comicStory', 'comicCount', 'comicStyle', 'comicEndpoint', 'comicModel', 'comicKey',
  'comicImageEndpoint', 'comicImageModel', 'comicImageKey', 'comicGenerate', 'comicGenerateImages',
  'comicExport', 'comicStatus', 'comicPanels'];
const els = Object.fromEntries(ids.map(id => [id, new Element(id)]));
els.comicCount.value = '4';
els.comicStyle.value = 'Приключение';
const anchors = [];
const document = {
  getElementById: id => els[id] || (els[id] = new Element(id)),
  createElement: tag => { const el = new Element(tag); anchors.push(el); return el; }
};
const context = {
  document, console, Blob,
  URL: { createObjectURL: () => 'blob:comic-test', revokeObjectURL: () => {} },
  setTimeout: fn => fn(), clearTimeout,
  fetch: async (url, options) => {
    const request = JSON.parse(options.body);
    if (url === 'https://api.test/v1/chat/completions') {
      assert.equal(options.headers.Authorization, 'Bearer temporary-test-key');
      assert.equal(request.model, 'test-model');
      return { ok: true, json: async () => ({ choices: [{ message: { content: '[{"title":"AI panel","scene":"AI scene","dialogue":"Hello"}]' } }] }) };
    }
    if (url === 'https://images.test/v1/images/generations') {
      assert.equal(options.headers.Authorization, 'Bearer image-test-key');
      assert.equal(request.model, 'image-test-model');
      assert.match(request.prompt, /AI scene/);
      return { ok: true, json: async () => ({ data: [{ b64_json: 'ZmFrZQ==' }] }) };
    }
    throw new Error('Unexpected network endpoint: ' + url);
  },
  JSON, String, Number, Array, Math, Promise
};
vm.runInNewContext(html.slice(start + 8, end), context, { timeout: 2000 });

(async () => {
  els.comicGenerate.click();
  assert.match(els.comicStatus.textContent, /Введите идею или сюжет/);
  els.comicStory.value = 'Героиня отправляется в горы. Она замечает загадочный свет. Находит древнюю дверь. Дверь открывается.';
  els.comicGenerate.click();
  assert.equal((els.comicPanels.innerHTML.match(/<article/g) || []).length, 4);
  assert.match(els.comicStatus.textContent, /локальн/);
  els.comicExport.click();
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
  console.log('PASS: local storyboard, text API, image API request/response, rendered image, SVG export');
})().catch(error => { console.error(error); process.exit(1); });

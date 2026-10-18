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
  'comicGenerate', 'comicExport', 'comicStatus', 'comicPanels'];
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
    assert.equal(url, 'https://api.test/v1/chat/completions');
    assert.equal(options.headers.Authorization, 'Bearer temporary-test-key');
    const request = JSON.parse(options.body);
    assert.equal(request.model, 'test-model');
    return { ok: true, json: async () => ({ choices: [{ message: { content: '[{"title":"AI panel","scene":"AI scene","dialogue":"Hello"}]' } }] }) };
  },
  JSON, String, Number, Array, Math, Promise
};
vm.runInNewContext(html.slice(start + 8, end), context, { timeout: 2000 });

(async () => {
  els.comicGenerate.click();
  assert.match(els.comicStatus.textContent, /Введите сюжет/);
  els.comicStory.value = 'Героиня отправляется в горы. Она замечает загадочный свет. Находит древнюю дверь. Дверь открывается.';
  els.comicGenerate.click();
  assert.equal((els.comicPanels.innerHTML.match(/<article/g) || []).length, 4);
  assert.match(els.comicStatus.textContent, /локально/);
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
  assert.match(els.comicStatus.textContent, /через ИИ API/);
  console.log('PASS: local storyboard, four-panel render, SVG export, optional OpenAI-compatible script API');
})().catch(error => { console.error(error); process.exit(1); });

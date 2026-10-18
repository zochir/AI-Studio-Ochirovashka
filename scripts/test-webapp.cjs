const fs = require('fs');
const vm = require('vm');
const assert = require('assert/strict');

const html = fs.readFileSync(process.argv[2], 'utf8');
const scriptStart = html.indexOf('<script>');
const scriptEnd = html.indexOf('</script>', scriptStart);
assert(scriptStart >= 0 && scriptEnd > scriptStart, 'inline script must exist');
const script = html.slice(scriptStart + '<script>'.length, scriptEnd);
const elements = new Map();
const defaults = {
  title: 'Новости Калмыкии', script: 'Тестовая новость', voice: '', rate: '1', rateValue: '1.0×',
  speak: '▶ Прослушать текст', stop: '■ Остановить', ttsHint: '', avatarFile: '', model: 'none',
  bg: 'blue', caption: 'Главные события региона', preview: '', placeholder: '', avatarPreview: '',
  captionSmall: 'Главные события региона', titlePreview: 'Новости Калмыкии', engineStatus: '',
  saveProject: '', loadProject: '', reset: ''
};

class FakeElement {
  constructor(id = '') {
    this.id = id;
    this.value = defaults[id] ?? '';
    this.textContent = defaults[id] ?? '';
    this.disabled = false;
    this.style = {};
    this.dataset = {};
    this.options = [];
    this.files = [];
    this.listeners = {};
    this.onclick = null;
    this.onchange = null;
    this.oninput = null;
    this.src = '';
    this.download = '';
    this.href = '';
    this.children = [];
    this._innerHTML = '';
  }
  set innerHTML(value) {
    this._innerHTML = value;
    this.options = [];
  }
  get innerHTML() { return this._innerHTML; }
  appendChild(child) {
    this.children.push(child);
    if (child.tagName === 'OPTION') this.options.push(child);
    return child;
  }
  addEventListener(type, fn) { this.listeners[type] = fn; }
  dispatchEvent(event) {
    const fn = this.listeners[event.type] ||
      (event.type === 'change' ? this.onchange : null) ||
      (event.type === 'input' ? this.oninput : null);
    if (fn) return fn(event);
  }
  click() {
    if (this.onclick) return this.onclick({ target: this });
    this.clicked = true;
  }
  get selectedOptions() {
    const option = this.options.find(item => String(item.value) === String(this.value));
    return option ? [option] : (this.options.length ? [this.options[0]] : []);
  }
}

for (const id of Object.keys(defaults)) elements.set(id, new FakeElement(id));
const document = {
  getElementById: id => {
    if (!elements.has(id)) elements.set(id, new FakeElement(id));
    return elements.get(id);
  },
  createElement: tag => {
    const element = new FakeElement();
    element.tagName = tag.toUpperCase();
    return element;
  }
};

const calls = { getVoices: 0, speak: [], stop: 0, alerts: [], confirms: [], downloads: [] };
const voiceList = [
  { name: 'ru-RU-test', lang: 'ru-RU', default: true },
  { name: 'en-US-test', lang: 'en-US', default: false }
];
const bridge = {
  getVoicesJson() { calls.getVoices++; return JSON.stringify(voiceList); },
  speak(...args) { calls.speak.push(args); },
  stop() { calls.stop++; }
};
const window = { AndroidTTS: bridge };
class FakeReader {
  readAsDataURL(file) {
    this.result = 'data:image/png;base64,TEST';
    setImmediate(() => this.onload && this.onload());
  }
}
class FakeEvent { constructor(type) { this.type = type; } }
const fakeURL = {
  createObjectURL(blob) { calls.lastBlob = blob; return 'blob:test'; },
  revokeObjectURL(url) { calls.revoked = url; }
};
const context = {
  window, document, AndroidTTS: bridge, FileReader: FakeReader, Event: FakeEvent,
  URL: fakeURL, alert: message => calls.alerts.push(message),
  confirm: message => (calls.confirms.push(message), true),
  setTimeout, clearTimeout, console, Blob, JSON, Number, String, Array, Math, Date, Promise
};

vm.runInNewContext(script, context, { timeout: 2000 });

(async () => {
  assert.equal(calls.getVoices, 1, 'native voices queried');
  assert.equal(elements.get('voice').options.length, 2, 'voice selector populated');
  assert.equal(elements.get('voice').value, '0', 'Russian voice preferred');

  elements.get('speak').click();
  assert.equal(calls.speak.length, 1, 'speak calls Android bridge');
  assert.equal(calls.speak[0][0], 'Тестовая новость');
  assert.equal(calls.speak[0][1], 'ru-RU-test');
  assert.equal(calls.speak[0][2], 1);
  elements.get('stop').click();
  assert.equal(calls.stop, 1, 'stop calls Android bridge');

  elements.get('title').value = 'Новый заголовок';
  elements.get('title').oninput();
  assert.equal(elements.get('titlePreview').textContent, 'Новый заголовок');
  elements.get('caption').value = 'Новая подпись';
  elements.get('caption').oninput();
  assert.equal(elements.get('captionSmall').textContent, 'Новая подпись');
  elements.get('rate').value = '1.2';
  elements.get('rate').dispatchEvent({ type: 'input' });
  assert.equal(elements.get('rateValue').textContent, '1.20×');
  elements.get('bg').value = 'dark';
  elements.get('bg').dispatchEvent(new FakeEvent('change'));
  assert.match(elements.get('preview').style.background, /30343d/);

  elements.get('saveProject').click();
  const saved = JSON.parse(await calls.lastBlob.text());
  assert.equal(saved.format, 'ai-news-studio-project');
  assert.equal(saved.title, 'Новый заголовок');
  assert.equal(saved.studio.caption, 'Новая подпись');
  assert.equal(saved.voice.rate, 1.2);
  assert.equal(saved.avatar.embedded, false);

  elements.get('avatarFile').files = [{ name: 'host.png', type: 'image/png' }];
  elements.get('avatarFile').onchange({ target: elements.get('avatarFile') });
  await new Promise(resolve => setTimeout(resolve, 10));
  assert.equal(elements.get('avatarPreview').src, 'data:image/png;base64,TEST');
  assert.equal(elements.get('avatarPreview').style.display, 'block');

  elements.get('loadProject').files = [{
    name: 'project.json',
    text: async () => JSON.stringify({
      format: 'ai-news-studio-project', title: 'Loaded title', script: 'Loaded script',
      voice: { rate: 0.9 }, avatarEngine: 'none',
      studio: { background: 'plain', caption: 'Loaded caption' }
    })
  }];
  await elements.get('loadProject').onchange({ target: elements.get('loadProject') });
  assert.equal(elements.get('title').value, 'Loaded title');
  assert.equal(elements.get('script').value, 'Loaded script');
  assert.equal(elements.get('captionSmall').textContent, 'Loaded caption');

  elements.get('reset').click();
  assert.equal(elements.get('title').value, 'Новости Калмыкии');
  assert.equal(elements.get('script').value, '');
  assert.equal(calls.stop, 2, 'reset stops speech');

  console.log('PASS: native TTS bridge wiring, voice selection, speak/stop, title/caption/rate/theme previews, project save/load, avatar preview, reset');
})().catch(error => {
  console.error(error);
  process.exit(1);
});

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

class Element {
  constructor() {
    this.listeners = {};
    this.attributes = {};
    this.classList = {add() {}, remove() {}, toggle() {}};
    this.options = [{value: 'all'}];
    this.value = '';
  }
  addEventListener(type, callback) { this.listeners[type] = callback; }
  setAttribute(name, value) { this.attributes[name] = value; }
  replaceChildren() { this.innerHTML = ''; this.textContent = ''; }
  append() {}
  focus() {}
}

function runPage(file, {url, api, data = {}}) {
  const elements = new Map();
  const get = selector => {
    if (!elements.has(selector)) elements.set(selector, new Element());
    return elements.get(selector);
  };
  const tabs = ['guides', 'summaries'].map(value => {
    const tab = new Element(); tab.dataset = {tab: value}; return tab;
  });
  const document = {
    title: '', querySelector: get, querySelectorAll: () => tabs,
    createElement: () => new Element(), createTextNode: text => ({textContent: text})
  };
  const window = {
    location: {href: url}, history: {replaceState() {}}, CourseApi: api, CourseData: data
  };
  const source = fs.readFileSync(path.join(__dirname, '../public/js', file), 'utf8');
  vm.runInNewContext(source, {window, document, URL, URLSearchParams, AbortController, setTimeout, clearTimeout});
  return {elements, get};
}

function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return {promise, resolve};
}

test('course search page keeps the newest response when an older search finishes last', async () => {
  const old = deferred();
  const calls = [];
  const api = {searchCourses(query) {
    calls.push(query);
    return query === '' ? Promise.resolve([]) : query === 'old' ? old.promise
      : Promise.resolve([{id: 902, code: 'CS902', name: 'Newest API course'}]);
  }};
  const {get} = runPage('courses.js', {url: 'http://frontend/courses.html', api});
  await new Promise(resolve => setImmediate(resolve));

  const input = get('#course-search');
  const form = get('#course-search-form');
  input.value = 'old';
  form.listeners.submit({preventDefault() {}});
  input.value = 'new';
  form.listeners.submit({preventDefault() {}});
  await new Promise(resolve => setImmediate(resolve));
  old.resolve([{id: 901, code: 'CS901', name: 'Stale API course'}]);
  await new Promise(resolve => setImmediate(resolve));

  assert.deepEqual(calls, ['', 'old', 'new']);
  assert.match(get('#course-grid').innerHTML, /Newest API course/);
  assert.doesNotMatch(get('#course-grid').innerHTML, /Stale API course/);
});

test('course detail page renders an API course outside the legacy catalog with a Thai name', async () => {
  const apiCourse = {id: 902, code: 'CS902', name: 'วิศวกรรมซอฟต์แวร์ขั้นสูง'};
  const calls = [];
  const api = {
    getCourse: async id => { calls.push(id); return apiCourse; },
    searchCourses: async () => []
  };
  const data = {
    escapeHtml: value => String(value), loadExams: () => [], semesterLabel: value => value,
    publisherName: () => '', subscribe() {}
  };
  const {get} = runPage('choose-courses.js', {
    url: 'http://frontend/choose-courses.html?courseId=902&course=CS902', api, data
  });
  await new Promise(resolve => setImmediate(resolve));

  assert.deepEqual(calls, ['902']);
  assert.match(get('#courseHeading').textContent, /CS902/);
  assert.match(get('#courseName').textContent, /วิศวกรรมซอฟต์แวร์ขั้นสูง/);
  assert.equal(get('#documentList').innerHTML, '');
});

test('course search page renders a Thai API result even when it is absent from the catalog', async () => {
  const calls = [];
  const api = {searchCourses: async query => {
    calls.push(query);
    return query === 'วิศวกรรม' ? [{id: 902, code: 'CS902', name: 'วิศวกรรมซอฟต์แวร์ขั้นสูง'}] : [];
  }};
  const {get} = runPage('courses.js', {url: 'http://frontend/courses.html', api});
  await new Promise(resolve => setImmediate(resolve));
  const input = get('#course-search'); input.value = 'วิศวกรรม';
  get('#course-search-form').listeners.submit({preventDefault() {}});
  await new Promise(resolve => setImmediate(resolve));

  assert.deepEqual(calls, ['', 'วิศวกรรม']);
  assert.match(get('#course-grid').innerHTML, /วิศวกรรมซอฟต์แวร์ขั้นสูง/);
  assert.match(get('#course-grid').innerHTML, /CS902/);
});

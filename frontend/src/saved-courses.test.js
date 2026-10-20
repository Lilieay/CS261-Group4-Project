const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const tick = () => new Promise(resolve => setImmediate(resolve));

function page({saved = async () => [], savedState = async () => false, user = {username: 'one'}} = {}) {
  const elements = new Map(), events = {}, redirects = [];
  const get = selector => {
    if (!elements.has(selector)) elements.set(selector, {
      value: '', dataset: {}, listeners: {}, setAttribute() {}, focus() {},
      addEventListener(type, callback) { this.listeners[type] = callback; }
    });
    return elements.get(selector);
  };
  const window = {currentUserReady: Promise.resolve(user), GuideApi: {saved, savedState},
    CourseData: {escapeHtml: value => String(value).replaceAll('<', '&lt;'), semesterLabel: String},
    addEventListener: (type, callback) => { events[type] = callback; },
    location: {replace: value => redirects.push(value)}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../public/js/saved-courses.js'), 'utf8'),
    {window, document: {querySelector: get}, URLSearchParams});
  return {get, events, redirects};
}

const row = {id: '12', course_id: 4, course_code: 'CS261', course_name: 'Software Engineering',
  title: '<Saved title>', topics: 'Requirements', year: '2568', semester: '1', period: 'กลางภาค'};

test('saved page reads API data, escapes text, filters, and links to the API reading page', async () => {
  const {get} = page({saved: async () => [row]});
  await tick();
  assert.match(get('#saved-list').innerHTML, /&lt;Saved title>/);
  assert.match(get('#saved-list').innerHTML, /source=api/);
  assert.match(get('#saved-list').innerHTML, /courseId=4/);
  assert.match(get('#saved-count').textContent, /1 รายการ/);
  get('#saved-search').value = 'unmatched';
  get('#saved-search').listeners.input();
  assert.match(get('#saved-list').innerHTML, /ไม่พบรายการที่ตรง/);
});

test('saved page prevents duplicate removal and removes a row only after API success', async () => {
  let resolve, calls = 0;
  const {get} = page({saved: async () => [row], savedState: (id, value) => {
    assert.equal(id, '12'); assert.equal(value, false); calls++;
    return new Promise(done => { resolve = done; });
  }});
  await tick();
  const click = {target: {closest: selector => selector === '[data-unsave]' ? {dataset: {unsave: '12'}} : null}};
  const pending = get('#saved-list').listeners.click(click);
  get('#saved-list').listeners.click(click);
  assert.equal(calls, 1);
  assert.match(get('#saved-count').textContent, /1 รายการ/);
  resolve(false); await pending;
  assert.match(get('#saved-list').innerHTML, /ยังไม่มีรายการที่บันทึก/);
});

test('saved page rejects stale refreshes and reloads an uncertain removal', async () => {
  let calls = 0, resolveOld;
  const {get, events} = page({saved: () => {
    calls++;
    if (calls === 2) return new Promise(resolve => { resolveOld = resolve; });
    return Promise.resolve(calls === 1 ? [row] : []);
  }});
  await tick();
  const old = events.focus();
  const newest = events.focus();
  await newest;
  resolveOld([row]); await old;
  assert.match(get('#saved-list').innerHTML, /ยังไม่มีรายการที่บันทึก/);
  let uncertainReads = 0;
  const uncertain = page({saved: async () => (++uncertainReads === 1 ? [row] : []),
    savedState: async () => { throw new Error('uncertain'); }});
  await tick();
  await uncertain.get('#saved-list').listeners.click({target: {closest: selector =>
    selector === '[data-unsave]' ? {dataset: {unsave: '12'}} : null}});
  assert.match(uncertain.get('#saved-status').textContent, /uncertain/);
  assert.match(uncertain.get('#saved-list').innerHTML, /ยังไม่มีรายการที่บันทึก/);
});

test('saved page requires login and provides retry on API failure', async () => {
  let reads = 0;
  const loggedOut = page({user: null, saved: async () => { reads++; return []; }});
  await tick(); assert.deepEqual(loggedOut.redirects, ['login.html']); assert.equal(reads, 0);
  const failed = page({saved: async () => { throw new Error('API unavailable'); }});
  await tick();
  assert.match(failed.get('#saved-list').innerHTML, /API unavailable/);
  assert.match(failed.get('#saved-list').innerHTML, /saved-retry/);
});

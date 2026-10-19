const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

class Element {
  constructor() {
    this.listeners = {};
    this.attributes = {};
    this.classList = {toggle() {}};
    this.hidden = false;
    this.value = '';
    this.innerHTML = '';
  }
  addEventListener(type, callback) { this.listeners[type] = callback; }
  setAttribute(name, value) { this.attributes[name] = value; }
  getAttribute(name) { return this.attributes[name]; }
  focus() {}
}

function runPage({mine, user = {username: 'student'}}) {
  const elements = new Map();
  const get = selector => {
    if (!elements.has(selector)) elements.set(selector, new Element());
    return elements.get(selector);
  };
  const panes = new Map([['exams-panel', new Element()], ['summaries-panel', new Element()]]);
  const redirects = [];
  const navigations = [];
  const document = {
    querySelector: get,
    getElementById: id => panes.get(id) || get('#' + id)
  };
  const window = {
    currentUserReady: Promise.resolve(user),
    GuideApi: {mine},
    location: {replace: value => redirects.push(value), assign: value => navigations.push(value)}
  };
  const source = fs.readFileSync(path.join(__dirname, '../public/js/shared-courses.js'), 'utf8');
  vm.runInNewContext(source, {window, document, URLSearchParams});
  return {get, redirects, navigations};
}

const ownGuide = {
  id: '41', course_id: 902, course_code: 'CS902', course_name: 'วิชานอก catalog',
  instructor_name: null, title: 'แนวจริง', year: '2568', semester: '1', period: 'กลางภาค',
  formats: ['ปรนัย'], topics: 'กราฟ', notes: '', objective_count: 12, essay_count: null
};

test('my guides page renders API rows, filters them, and opens the exact guide', async () => {
  const {get, navigations} = runPage({mine: async () => [ownGuide]});
  await new Promise(resolve => setImmediate(resolve));

  assert.match(get('#exam-list').innerHTML, /CS902/);
  assert.match(get('#exam-list').innerHTML, /วิชานอก catalog/);
  assert.doesNotMatch(get('#exam-list').innerHTML, /undefined|NaN|คะแนนรีวิว|ดาวน์โหลด|อัปเดตเมื่อ/);
  assert.match(get('#course-filter').innerHTML, /CS902/);

  get('#search').value = 'missing';
  get('#search').listeners.input();
  assert.match(get('#exam-list').innerHTML, /ไม่พบแนวข้อสอบที่ตรงกับการค้นหา/);
  get('#search').value = '';
  get('#exam-list').listeners.click({target: {closest: selector => selector === '[data-action="read"]'
    ? {dataset: {action: 'read', id: '41'}} : null}});

  const params = new URLSearchParams(navigations[0].split('?')[1]);
  assert.equal(navigations.length, 1);
  assert.equal(params.get('guide'), '41');
  assert.equal(params.get('course'), 'CS902');
  assert.equal(params.get('courseId'), '902');
  assert.equal(params.get('source'), 'api');
  assert.equal(params.get('returnTo'), 'shared-courses.html');
});

test('my guides page distinguishes empty results from errors and retries failures', async () => {
  const empty = runPage({mine: async () => []});
  await new Promise(resolve => setImmediate(resolve));
  assert.match(empty.get('#exam-list').innerHTML, /คุณยังไม่ได้เผยแพร่แนวข้อสอบ/);

  let calls = 0;
  const failed = runPage({mine: async () => {
    calls += 1;
    if (calls === 1) throw new Error('backend down');
    return [ownGuide];
  }});
  await new Promise(resolve => setImmediate(resolve));
  assert.match(failed.get('#exam-list').innerHTML, /โหลดรายการไม่สำเร็จ/);
  assert.doesNotMatch(failed.get('#exam-list').innerHTML, /คุณยังไม่ได้เผยแพร่/);
  failed.get('#exam-list').listeners.click({target: {closest: selector => selector === '#retry-load' ? {} : null}});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(calls, 2);
  assert.match(failed.get('#exam-list').innerHTML, /แนวจริง/);
});

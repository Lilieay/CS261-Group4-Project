const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, '../public/js/guide-api.js'), 'utf8');

function loadGuideApi({token = 'test-token', mode = 'preview', apiBaseUrl = 'http://127.0.0.1:8000',
  fetchImpl = async () => new Response('{}')} = {}) {
  const values = new Map(token ? [['access_token', token]] : []);
  const calls = [];
  const redirects = [];
  const window = {
    GuidePublishConfig: {mode, apiBaseUrl, tokenStorageKey: 'access_token',
      mePath: '/api/auth/me', coursesPath: '/courses', publishPath: '/guides', timeoutMs: 15000},
    LoginConfig: {tokenStorageKey: 'access_token'},
    location: {origin: 'http://frontend', replace: url => redirects.push(url)}
  };
  const context = {
    window,
    sessionStorage: {
      getItem: key => values.get(key) ?? null,
      removeItem: key => values.delete(key)
    },
    localStorage: {
      getItem: key => values.get(key) ?? null,
      removeItem: key => values.delete(key)
    },
    fetch: (...args) => { calls.push(args); return fetchImpl(...args); },
    URL, URLSearchParams, AbortController, Response, setTimeout, clearTimeout
  };
  vm.runInNewContext(source, context, {filename: 'guide-api.js'});
  return {api: window.GuideApi, calls, redirects, values};
}

test('guide read client uses the same-origin proxy while publish remains in preview mode', async () => {
  const client = loadGuideApi({fetchImpl: async () => new Response(JSON.stringify({
    id: 12, title: 'แนวข้อสอบ', academic_year: 2568, semester: 1, exam_period: 'midterm',
    publisher_name: 'ผู้เผยแพร่', course: {id: 4, course_code: 'CS261', course_name: 'วิชา', instructor_names: 'อาจารย์'},
    topics: 'หัวข้อ', exam_format: 'mixed', objective_count: 10, subjective_count: 2,
    additional_advice: null
  }))});

  const detail = await client.api.read(12, 'CS261');
  assert.equal(detail.course.course_code, 'CS261');
  assert.equal(client.calls[0][0], '/api/guides/guides/12');
  assert.equal(client.calls[0][1].headers.Authorization, 'Bearer test-token');
  await assert.rejects(client.api.publish({}, 'CS261'), /ยังไม่ได้เปิดโหมด API/);
});

test('guide list client sends database filters and maps rows without preview data', async () => {
  const client = loadGuideApi({fetchImpl: async () => new Response(JSON.stringify({
    course_id: 27,
    items: [{id: 31, title: 'กลางภาค', academic_year: 2568, semester: 1,
      exam_period: 'midterm', publisher_name: 'ผู้เผยแพร่'}]
  }))});

  const rows = await client.api.list(27, {academic_year: '2568', semester: '1', exam_period: 'midterm'});
  assert.deepEqual(JSON.parse(JSON.stringify(rows)), [{
    id: '31', title: 'กลางภาค', year: '2568', semester: '1',
    period: 'กลางภาค', publisher_name: 'ผู้เผยแพร่'
  }]);
  assert.equal(client.calls[0][0], '/api/guides/courses/27/guides?academic_year=2568&semester=1&exam_period=midterm');
});

test('guide client keeps auth and course reads on their existing proxies and keeps publish on the configured API', async () => {
  const client = loadGuideApi({mode: 'api', fetchImpl: async url => {
    if (url === '/api/auth/me') return new Response('{"id":8,"username":"student"}');
    if (url === '/api/courses') return new Response('[{"id":4,"course_code":"CS261","course_name":"วิชา"}]');
    return new Response(JSON.stringify({
      id: 32, title: 'แนวข้อสอบ', academic_year: 2568, semester: 1, exam_period: 'midterm',
      publisher_name: 'ผู้เผยแพร่', course: {id: 4, course_code: 'CS261', course_name: 'วิชา', instructor_names: null},
      topics: 'หัวข้อ', exam_format: 'objective', objective_count: 10, subjective_count: null,
      additional_advice: null
    }), {status: 201});
  }});
  await client.api.currentUser();
  await client.api.courses();
  await client.api.publish({course_id: 4}, 'CS261');
  assert.equal(client.calls[0][0], '/api/auth/me');
  assert.equal(client.calls[1][0], '/api/courses');
  assert.equal(client.calls[2][0], 'http://127.0.0.1:8000/guides');
});

test('guide client redirects when login is missing and clears an expired token', async () => {
  const missing = loadGuideApi({token: ''});
  await assert.rejects(missing.api.filterOptions(27), error => error.status === 401);
  assert.deepEqual(missing.redirects, ['login.html']);

  const expired = loadGuideApi({fetchImpl: async () => new Response('{"error":{"code":"AUTH_REQUIRED"}}', {status: 401})});
  await assert.rejects(expired.api.read(31, 'CS261'), error => error.status === 401);
  assert.deepEqual(expired.redirects, ['login.html']);
  assert.equal(expired.values.has('access_token'), false);
});

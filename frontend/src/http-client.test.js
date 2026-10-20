const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function client(fetch) {
  const window = {};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../public/js/http-client.js'), 'utf8'), {
    window, fetch, AbortController, setTimeout, clearTimeout,
    sessionStorage: {getItem: () => 'session-token'}, localStorage: {getItem: () => 'legacy-token'}
  });
  return window.HttpClient;
}

test('transport preserves caller headers, bearer auth, HTTP errors and malformed response payloads', async () => {
  const calls = [];
  const api = client(async (url, init) => {
    calls.push([url, init]);
    return new Response(url === '/invalid' ? '<html>Unavailable</html>' : '{"detail":"Invalid"}', {status: 422});
  });
  const {response, payload} = await api.request('/api', {token: 'session', headers: {'X-Test': 'value'}});
  assert.equal(response.status, 422);
  assert.equal(payload.detail, 'Invalid');
  assert.equal(calls[0][1].headers.Authorization, 'Bearer session');
  assert.equal(calls[0][1].headers['X-Test'], 'value');
  assert.equal(calls[0][1].cache, 'no-store');
  assert.equal((await api.request('/invalid')).payload, null);
});

test('transport timeout covers response-body reading and callers can still cancel', async () => {
  const api = client(async (_, init) => ({text: () => new Promise((_, reject) => {
    init.signal.addEventListener('abort', () => reject(new Error('aborted')), {once: true});
  })}));
  await assert.rejects(api.request('/slow-body', {timeoutMs: 10}), /aborted/);
  const controller = new AbortController();
  const pending = api.request('/cancel', {timeoutMs: 1000, signal: controller.signal});
  await new Promise(resolve => setImmediate(resolve));
  controller.abort();
  await assert.rejects(pending, /aborted/);
});

const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const {createApp} = require('./server');

async function withServer(run) {
  const server = createApp({backendUrl: 'http://backend:8000'}).listen(0);
  await new Promise(resolve => server.once('listening', resolve));
  try {
    await run(server.address().port);
  } finally {
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
}

function request(port, path, method = 'GET', headers = {}, body = '') {
  return new Promise((resolve, reject) => {
    const req = http.request({host: '127.0.0.1', port, path, method, headers}, res => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', chunk => { body += chunk; });
      res.on('end', () => resolve({status: res.statusCode, headers: res.headers, body}));
    });
    req.on('error', reject);
    req.end(body);
  });
}

test('course list proxy pins the backend path and forwards search and authorization', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let target;
  let init;
  global.fetch = async (url, options) => {
    target = url;
    init = options;
    return new Response('[{"id":4}]', {status: 200, headers: {'content-type': 'application/json'}});
  };

  await withServer(async port => {
    const response = await request(port, '/api/courses?search=CS%20261', 'GET', {Authorization: 'Bearer safe-test-token'});
    assert.equal(response.status, 200);
    assert.equal(response.body, '[{"id":4}]');
    assert.equal(response.headers['cache-control'], 'no-store');
    assert.equal(target.href, 'http://backend:8000/courses?search=CS+261');
    assert.equal(init.headers.Authorization, 'Bearer safe-test-token');
    assert.equal(init.method, 'GET');
  });
});

test('my guides proxy pins the backend path, forwards authorization, and preserves an empty result', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let target;
  let init;
  global.fetch = async (url, options) => {
    target = url;
    init = options;
    return new Response('[]', {status: 200, headers: {'content-type': 'application/json'}});
  };

  await withServer(async port => {
    const response = await request(port, '/api/my-guides?username=other', 'GET', {Authorization: 'Bearer test-token'});
    assert.equal(response.status, 200);
    assert.equal(response.body, '[]');
    assert.equal(response.headers['cache-control'], 'no-store');
    assert.equal(target.href, 'http://backend:8000/api/my-guides');
    assert.equal(init.method, 'GET');
    assert.equal(init.headers.Authorization, 'Bearer test-token');
    assert.equal(init.headers.Accept, 'application/json');
    assert.equal(init.cache, 'no-store');
    assert.equal(init.redirect, 'manual');
  });
});

test('my guides proxy preserves backend errors and returns 502 when unavailable', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  global.fetch = async () => new Response('{"detail":"unauthorized"}', {
    status: 401, headers: {'content-type': 'application/json'}
  });
  await withServer(async port => {
    const response = await request(port, '/api/my-guides');
    assert.equal(response.status, 401);
    assert.deepEqual(JSON.parse(response.body), {detail: 'unauthorized'});
  });

  global.fetch = async () => { throw new Error('backend unavailable'); };
  await withServer(async port => {
    const response = await request(port, '/api/my-guides');
    assert.equal(response.status, 502);
  });
});

test('course detail proxy forwards bearer authorization and preserves API errors', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let target;
  let authorization;
  global.fetch = async (url, options) => {
    target = url;
    authorization = options.headers.Authorization;
    return new Response('{"error":{"code":"COURSE_NOT_FOUND"}}', {
      status: 404, headers: {'content-type': 'application/json'}
    });
  };

  await withServer(async port => {
    const response = await request(port, '/api/courses/27', 'GET', {Authorization: 'Bearer safe-test-token'});
    assert.equal(response.status, 404);
    assert.deepEqual(JSON.parse(response.body), {error: {code: 'COURSE_NOT_FOUND'}});
    assert.equal(target.href, 'http://backend:8000/courses/27');
    assert.equal(authorization, 'Bearer safe-test-token');
  });
});

test('course detail proxy rejects malformed IDs before constructing or calling the upstream URL', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let calls = 0;
  global.fetch = async () => { calls += 1; return new Response('unexpected'); };

  await withServer(async port => {
    const response = await request(port, '/api/courses/%2E%2E');
    assert.equal(response.status, 422);
    assert.equal(JSON.parse(response.body).error.code, 'INVALID_PARAMETERS');
    assert.equal(calls, 0);
  });
});

test('course proxy preserves invalid-parameter status from the API', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let authorization;
  global.fetch = async (_url, options) => {
    authorization = options.headers.Authorization;
    return new Response('{"error":{"code":"INVALID_PARAMETERS"}}', {status: 422});
  };

  await withServer(async port => {
    const response = await request(port, '/api/courses?search=CS261', 'GET', {Authorization: 'Bearer safe-test-token'});
    assert.equal(response.status, 422);
    assert.equal(authorization, 'Bearer safe-test-token');
  });
});

test('course proxy preserves the authentication-required status and response', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  global.fetch = async () => new Response('{"error":{"code":"AUTH_REQUIRED"}}', {
    status: 401, headers: {'content-type': 'application/json'}
  });

  await withServer(async port => {
    const response = await request(port, '/api/courses');
    assert.equal(response.status, 401);
    assert.deepEqual(JSON.parse(response.body), {error: {code: 'AUTH_REQUIRED'}});
  });
});

test('course proxy returns a bounded gateway error when the backend is unavailable', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  global.fetch = async () => { throw new Error('backend unavailable'); };

  await withServer(async port => {
    const response = await request(port, '/api/courses');
    assert.equal(response.status, 502);
    assert.match(JSON.parse(response.body).detail, /บริการรายวิชา/);
  });
});

test('guide proxy forwards guide paths, filters, bearer authorization and disables caching', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let target;
  let init;
  global.fetch = async (url, options) => {
    target = url;
    init = options;
    return new Response('{"course_id":27,"items":[]}', {
      status: 200, headers: {'content-type': 'application/json'}
    });
  };

  await withServer(async port => {
    const response = await request(port,
      '/api/guides/courses/27/guides?academic_year=2568&semester=1',
      'GET', {Authorization: 'Bearer safe-test-token'});
    assert.equal(response.status, 200);
    assert.equal(response.headers['cache-control'], 'no-store');
    assert.equal(target.href, 'http://backend:8000/courses/27/guides?academic_year=2568&semester=1');
    assert.equal(init.headers.Authorization, 'Bearer safe-test-token');
    assert.equal(init.method, 'GET');
  });
});

test('publish proxy pins POST to the guide endpoint and forwards JSON and authorization', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let target;
  let init;
  global.fetch = async (url, options) => {
    target = url;
    init = options;
    return new Response('{"id":32}', {
      status: 201, headers: {'content-type': 'application/json'}
    });
  };
  const payload = JSON.stringify({course_id: 4, title: 'แนวข้อสอบ'});

  await withServer(async port => {
    const response = await request(port, '/api/guides', 'POST', {
      Authorization: 'Bearer safe-test-token', 'Content-Type': 'application/json'
    }, payload);
    assert.equal(response.status, 201);
    assert.equal(response.body, '{"id":32}');
    assert.equal(response.headers['cache-control'], 'no-store');
    assert.equal(target.href, 'http://backend:8000/guides');
    assert.equal(init.method, 'POST');
    assert.deepEqual(JSON.parse(init.body), JSON.parse(payload));
    assert.equal(init.headers.Authorization, 'Bearer safe-test-token');
  });
});

test('publish proxy rejects non-JSON bodies before calling the backend', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let calls = 0;
  global.fetch = async () => { calls += 1; return new Response('{}'); };

  await withServer(async port => {
    const response = await request(port, '/api/guides', 'POST', {
      'Content-Type': 'text/plain'
    }, 'not-json');
    assert.equal(response.status, 400);
    assert.equal(calls, 0);
  });
});

test('guide proxy preserves backend authentication and missing-record responses', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  global.fetch = async () => new Response('{"error":{"code":"AUTH_REQUIRED"}}', {
    status: 401, headers: {'content-type': 'application/json'}
  });

  await withServer(async port => {
    const response = await request(port, '/api/guides/guides/123');
    assert.equal(response.status, 401);
    assert.deepEqual(JSON.parse(response.body), {error: {code: 'AUTH_REQUIRED'}});
  });
});

test('guide proxy rejects backend paths outside the read API allowlist', async t => {
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  let calls = 0;
  global.fetch = async () => { calls += 1; return new Response('{}'); };

  await withServer(async port => {
    const response = await request(port, '/api/guides/my-guides');
    assert.equal(response.status, 404);
    assert.equal(calls, 0);
  });
});

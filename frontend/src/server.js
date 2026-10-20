const express = require('express');
const path = require('node:path');

const validId = value => /^[1-9]\d*$/.test(value)
  && Number.isSafeInteger(Number(value)) && Number(value) <= 2147483647;

function createApp({backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000'} = {}) {
  const app = express();
  app.disable('x-powered-by');

  async function proxy(req, res, upstreamPath, {body, onResponse, errorMessage} = {}) {
    res.set('Cache-Control', 'no-store');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const base = new URL(backendUrl);
      if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
      const headers = {Accept: 'application/json'};
      if (req.get('authorization')) headers.Authorization = req.get('authorization');
      if (body !== undefined) headers['Content-Type'] = 'application/json';
      const response = await fetch(new URL(upstreamPath, base), {
        method: req.method, headers, signal: controller.signal, cache: 'no-store', redirect: 'manual',
        ...(body === undefined ? {} : {body: JSON.stringify(body)})
      });
      if (onResponse) return await onResponse(response);
      const text = await response.text();
      if (response.headers.get('content-type')) res.set('Content-Type', response.headers.get('content-type'));
      return res.status(response.status).send(text);
    } catch (_) {
      return res.status(502).json({detail: errorMessage});
    } finally { clearTimeout(timer); }
  }

  app.use('/api/auth', express.json({limit: '8kb'}));
  for (const [method, route] of [['post', '/login'], ['get', '/status'], ['get', '/me'], ['post', '/logout']]) {
    app[method](`/api/auth${route}`, (req, res) => {
      res.set('Cache-Control', 'no-store');
      let body;
      if (route === '/login') {
        if (!req.body || typeof req.body.username !== 'string' || typeof req.body.password !== 'string') {
          return res.status(422).json({detail: 'กรุณากรอกข้อมูลเข้าสู่ระบบให้ครบ'});
        }
        body = {username: req.body.username, password: req.body.password};
      }
      return proxy(req, res, `/api/auth${route}`, {
        body, errorMessage: 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง',
        onResponse: async response => {
          if (!response.ok) {
            const status = response.status >= 400 && response.status <= 599 ? response.status : 502;
            return res.status(status).json({detail: 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง'});
          }
          const payload = await response.json();
          const user = value => value && ({id: value.id, username: value.username,
            display_name: value.display_name, role: value.role});
          if (route === '/login') return res.status(response.status).json({message: 'เข้าสู่ระบบสำเร็จ',
            access_token: payload.access_token, token_type: payload.token_type, user: user(payload.user)});
          if (route === '/me') return res.status(response.status).json(user(payload));
          if (route === '/status') return res.status(response.status).json({logged_in: payload.logged_in, user: user(payload.user)});
          return res.status(response.status).json({message: 'ออกจากระบบสำเร็จ'});
        }
      });
    });
  }

  app.all(['/api/saved-guides', '/api/saved-guides/:guideId'], (req, res) => {
    res.set('Cache-Control', 'no-store');
    const id = req.params.guideId;
    if (!['GET', 'PUT', 'DELETE'].includes(req.method) || (!id && req.method !== 'GET')) {
      return res.status(405).json({detail: 'METHOD_NOT_ALLOWED'});
    }
    if (id !== undefined && !validId(id)) return res.status(422).json({detail: 'GUIDE_ID_INVALID'});
    if (Object.keys(req.query).length) return res.status(422).json({detail: 'QUERY_NOT_ALLOWED'});
    return proxy(req, res, `/api/saved-guides${id ? `/${id}` : ''}`, {
      errorMessage: 'ตรวจสอบรายการที่บันทึกไม่ได้ กรุณาลองใหม่'
    });
  });

  app.get(['/api/courses', '/api/courses/:courseId'], (req, res) => {
    res.set('Cache-Control', 'no-store');
    const id = req.params.courseId;
    if (id !== undefined && !validId(id)) {
      return res.status(422).json({error: {code: 'INVALID_PARAMETERS', message: 'Invalid course ID', fields: []}});
    }
    const query = new URLSearchParams();
    if (id === undefined) {
      for (const value of new URL(req.originalUrl, 'http://frontend').searchParams.getAll('search')) query.append('search', value);
    }
    const target = id === undefined ? `/courses${query.size ? `?${query}` : ''}` : `/courses/${id}`;
    return proxy(req, res, target, {errorMessage: 'ไม่สามารถเชื่อมต่อบริการรายวิชาได้ กรุณาลองใหม่อีกครั้ง'});
  });

  app.get('/api/my-guides', (req, res) => proxy(req, res, '/api/my-guides', {
    errorMessage: 'ไม่สามารถโหลดรายการแนวข้อสอบได้ กรุณาลองใหม่อีกครั้ง'
  }));

  app.put('/api/my-guides/:guideId', express.json({limit: '16kb'}), (req, res) => {
    res.set('Cache-Control', 'no-store');
    const id = req.params.guideId;
    if (!validId(id)) return res.status(422).json({detail: 'GUIDE_ID_INVALID'});
    if (!isJsonObject(req)) return res.status(400).json({detail: 'ข้อมูลแก้ไขไม่ถูกต้อง'});
    return proxy(req, res, `/api/my-guides/${id}`, {
      body: req.body, errorMessage: 'ยืนยันผลการแก้ไขไม่ได้ กรุณาโหลดรายการใหม่เพื่อตรวจสอบ'
    });
  });

  app.delete('/api/my-guides/:guideId', (req, res) => {
    res.set('Cache-Control', 'no-store');
    const id = req.params.guideId;
    if (!validId(id)) return res.status(422).json({detail: 'GUIDE_ID_INVALID'});
    return proxy(req, res, `/api/my-guides/${id}`, {
      errorMessage: 'ยืนยันผลการลบไม่ได้ กรุณาโหลดรายการใหม่เพื่อตรวจสอบ'
    });
  });

  app.use('/api/guides', express.json({limit: '16kb'}));
  app.post('/api/guides', (req, res) => {
    res.set('Cache-Control', 'no-store');
    if (!isJsonObject(req)) return res.status(400).json({detail: 'ข้อมูลเผยแพร่ไม่ถูกต้อง'});
    return proxy(req, res, '/guides', {
      body: req.body, errorMessage: 'ไม่สามารถเผยแพร่แนวข้อสอบได้ กรุณาลองใหม่อีกครั้ง'
    });
  });

  app.get('/api/guides/*path', (req, res) => {
    res.set('Cache-Control', 'no-store');
    const upstreamPath = Array.isArray(req.params.path) ? req.params.path.join('/') : req.params.path;
    const listPath = /^courses\/[1-9]\d*\/guides$/.test(upstreamPath);
    const allowedPath = listPath || /^courses\/[1-9]\d*\/guides\/filter-options$/.test(upstreamPath)
      || /^guides\/[1-9]\d*$/.test(upstreamPath);
    const query = new URL(req.originalUrl, 'http://frontend').searchParams;
    if (!allowedPath || (!listPath && query.size)) return res.status(404).json({detail: 'ไม่พบเส้นทางแนวข้อสอบ'});
    return proxy(req, res, `/${upstreamPath}${query.size ? `?${query}` : ''}`, {
      errorMessage: 'ไม่สามารถเชื่อมต่อบริการแนวข้อสอบได้ กรุณาลองใหม่อีกครั้ง'
    });
  });

  const publicRoot = path.join(__dirname, '../public');
  const pages = ['index', 'login', 'courses', 'choose-courses', 'read-courses',
    'shared-courses', 'saved-courses', 'upload'];
  // Keep a single URL for each page even when opened through its folder path.
  app.get(pages.map(page => `/pages/${page}.html`), (req, res) => {
    res.redirect(302, req.originalUrl.replace(/^\/pages/, ''));
  });
  app.use(express.static(path.join(publicRoot, 'pages')));
  app.use(express.static(publicRoot));
  app.use((error, req, res, next) => {
    if (req.path.startsWith('/api/auth') || req.path === '/api/guides' || req.path.startsWith('/api/my-guides/')) {
      return res.status(error.status === 413 ? 413 : 400).json({detail: 'ข้อมูลคำขอไม่ถูกต้อง'});
    }
    next(error);
  });
  return app;
}

function isJsonObject(req) {
  return req.is('application/json') && req.body && typeof req.body === 'object' && !Array.isArray(req.body);
}

if (require.main === module) {
  createApp().listen(5000, process.env.HOST || '127.0.0.1', () => console.log('Frontend: http://127.0.0.1:5000'));
}
module.exports = {createApp};

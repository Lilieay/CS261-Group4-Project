const express = require('express');
const path = require('node:path');

function createApp({backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000'} = {}) {
  const app = express();
  app.disable('x-powered-by');
  app.use('/api/auth', express.json({limit: '8kb'}));
  const authRoutes = [['post', '/login'], ['get', '/status'], ['get', '/me'], ['post', '/logout']];

  for (const [method, route] of authRoutes) {
    app[method](`/api/auth${route}`, async (req, res) => {
      res.set('Cache-Control', 'no-store');
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 12000);
      try {
        const base = new URL(backendUrl);
        if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
        const headers = {Accept: 'application/json'};
        if (req.get('authorization')) headers.Authorization = req.get('authorization');
        let body;
        if (route === '/login') {
          if (!req.body || typeof req.body.username !== 'string' || typeof req.body.password !== 'string') {
            return res.status(422).json({detail: 'กรุณากรอกข้อมูลเข้าสู่ระบบให้ครบ'});
          }
          headers['Content-Type'] = 'application/json';
          body = JSON.stringify({username: req.body.username, password: req.body.password});
        }
        const response = await fetch(new URL(`/api/auth${route}`, base), {
          method: method.toUpperCase(), headers, signal: controller.signal,
          cache: 'no-store', redirect: 'manual', ...(body === undefined ? {} : {body})
        });
        if (!response.ok) {
          const status = response.status >= 400 && response.status <= 599 ? response.status : 502;
          return res.status(status).json({detail: 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง'});
        }
        const payload = await response.json();
        const user = value => value && ({id: value.id, username: value.username,
          display_name: value.display_name, role: value.role});
        if (route === '/login') {
          return res.status(response.status).json({message: 'เข้าสู่ระบบสำเร็จ',
            access_token: payload.access_token, token_type: payload.token_type, user: user(payload.user)});
        }
        if (route === '/me') return res.status(response.status).json(user(payload));
        if (route === '/status') return res.status(response.status).json({logged_in: payload.logged_in, user: user(payload.user)});
        return res.status(response.status).json({message: 'ออกจากระบบสำเร็จ'});
      } catch (_) {
        return res.status(502).json({detail: 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง'});
      } finally { clearTimeout(timer); }
    });
  }

  app.all(['/api/saved-guides', '/api/saved-guides/:guideId'], async (req, res) => {
    res.set('Cache-Control', 'no-store');
    const id = req.params.guideId;
    if (!['GET', 'PUT', 'DELETE'].includes(req.method) || (!id && req.method !== 'GET')) {
      return res.status(405).json({detail: 'METHOD_NOT_ALLOWED'});
    }
    if (id !== undefined && (!/^[1-9]\d*$/.test(id) || Number(id) > 2147483647)) {
      return res.status(422).json({detail: 'GUIDE_ID_INVALID'});
    }
    if (Object.keys(req.query).length) return res.status(422).json({detail: 'QUERY_NOT_ALLOWED'});
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const base = new URL(backendUrl);
      if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
      const headers = {Accept: 'application/json'};
      if (req.get('authorization')) headers.Authorization = req.get('authorization');
      const response = await fetch(new URL(`/api/saved-guides${id ? `/${id}` : ''}`, base), {
        method: req.method, headers, signal: controller.signal, cache: 'no-store', redirect: 'manual'
      });
      const body = await response.text();
      if (response.headers.get('content-type')) res.set('Content-Type', response.headers.get('content-type'));
      return res.status(response.status).send(body);
    } catch (_) {
      return res.status(502).json({detail: 'ตรวจสอบรายการที่บันทึกไม่ได้ กรุณาลองใหม่'});
    } finally { clearTimeout(timer); }
  });

  app.get(['/api/courses', '/api/courses/:courseId'], async (req, res) => {
    res.set('Cache-Control', 'no-store');
    const courseId = req.params.courseId;
    if (courseId !== undefined
      && (!/^[1-9]\d*$/.test(courseId) || !Number.isSafeInteger(Number(courseId)) || Number(courseId) > 2147483647)) {
      return res.status(422).json({error: {
        code: 'INVALID_PARAMETERS', message: 'Invalid course ID', fields: []
      }});
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const base = new URL(backendUrl);
      if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
      const headers = {Accept: 'application/json'};
      if (req.get('authorization')) headers.Authorization = req.get('authorization');
      const target = courseId === undefined
        ? new URL('/courses', base)
        : new URL(`/courses/${courseId}`, base);
      if (courseId === undefined) {
        const incoming = new URL(req.originalUrl, 'http://frontend').searchParams;
        for (const value of incoming.getAll('search')) target.searchParams.append('search', value);
      }
      const response = await fetch(target, {
        method: 'GET', headers, signal: controller.signal,
        cache: 'no-store', redirect: 'manual'
      });
      const body = await response.text();
      if (response.headers.get('content-type')) res.set('Content-Type', response.headers.get('content-type'));
      return res.status(response.status).send(body);
    } catch (_) {
      return res.status(502).json({detail: 'ไม่สามารถเชื่อมต่อบริการรายวิชาได้ กรุณาลองใหม่อีกครั้ง'});
    } finally { clearTimeout(timer); }
  });

  app.get('/api/my-guides', async (req, res) => {
    res.set('Cache-Control', 'no-store');
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const base = new URL(backendUrl);
      if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
      const headers = {Accept: 'application/json'};
      if (req.get('authorization')) headers.Authorization = req.get('authorization');
      const response = await fetch(new URL('/api/my-guides', base), {
        method: 'GET', headers, signal: controller.signal,
        cache: 'no-store', redirect: 'manual'
      });
      const body = await response.text();
      if (response.headers.get('content-type')) res.set('Content-Type', response.headers.get('content-type'));
      return res.status(response.status).send(body);
    } catch (_) {
      return res.status(502).json({detail: 'ไม่สามารถโหลดรายการแนวข้อสอบได้ กรุณาลองใหม่อีกครั้ง'});
    } finally { clearTimeout(timer); }
  });

  app.put('/api/my-guides/:guideId', express.json({limit: '16kb'}), async (req, res) => {
    res.set('Cache-Control', 'no-store');
    const id = req.params.guideId;
    if (!/^[1-9]\d*$/.test(id) || !Number.isSafeInteger(Number(id)) || Number(id) > 2147483647) {
      return res.status(422).json({detail: 'GUIDE_ID_INVALID'});
    }
    if (!req.is('application/json') || !req.body || typeof req.body !== 'object' || Array.isArray(req.body)) {
      return res.status(400).json({detail: 'ข้อมูลแก้ไขไม่ถูกต้อง'});
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const base = new URL(backendUrl);
      if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
      const headers = {Accept: 'application/json', 'Content-Type': 'application/json'};
      if (req.get('authorization')) headers.Authorization = req.get('authorization');
      const response = await fetch(new URL(`/api/my-guides/${id}`, base), {
        method: 'PUT', headers, body: JSON.stringify(req.body), signal: controller.signal,
        cache: 'no-store', redirect: 'manual'
      });
      const body = await response.text();
      if (response.headers.get('content-type')) res.set('Content-Type', response.headers.get('content-type'));
      return res.status(response.status).send(body);
    } catch (_) {
      return res.status(502).json({detail: 'ยืนยันผลการแก้ไขไม่ได้ กรุณาโหลดรายการใหม่เพื่อตรวจสอบ'});
    } finally { clearTimeout(timer); }
  });

  app.delete('/api/my-guides/:guideId', async (req, res) => {
    res.set('Cache-Control', 'no-store');
    const id = req.params.guideId;
    if (!/^[1-9]\d*$/.test(id) || !Number.isSafeInteger(Number(id)) || Number(id) > 2147483647) {
      return res.status(422).json({detail: 'GUIDE_ID_INVALID'});
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const base = new URL(backendUrl);
      if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
      const headers = {Accept: 'application/json'};
      if (req.get('authorization')) headers.Authorization = req.get('authorization');
      const response = await fetch(new URL(`/api/my-guides/${id}`, base), {
        method: 'DELETE', headers, signal: controller.signal,
        cache: 'no-store', redirect: 'manual'
      });
      const body = await response.text();
      if (response.headers.get('content-type')) res.set('Content-Type', response.headers.get('content-type'));
      return res.status(response.status).send(body);
    } catch (_) {
      return res.status(502).json({detail: 'ยืนยันผลการลบไม่ได้ กรุณาโหลดรายการใหม่เพื่อตรวจสอบ'});
    } finally { clearTimeout(timer); }
  });

  app.use('/api/guides', express.json({limit: '16kb'}));

  app.post('/api/guides', async (req, res) => {
    res.set('Cache-Control', 'no-store');
    if (!req.is('application/json') || !req.body || typeof req.body !== 'object' || Array.isArray(req.body)) {
      return res.status(400).json({detail: 'ข้อมูลเผยแพร่ไม่ถูกต้อง'});
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const base = new URL(backendUrl);
      if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
      const headers = {Accept: 'application/json', 'Content-Type': 'application/json'};
      if (req.get('authorization')) headers.Authorization = req.get('authorization');
      const response = await fetch(new URL('/guides', base), {
        method: 'POST', headers, body: JSON.stringify(req.body), signal: controller.signal,
        cache: 'no-store', redirect: 'manual'
      });
      const body = await response.text();
      if (response.headers.get('content-type')) res.set('Content-Type', response.headers.get('content-type'));
      return res.status(response.status).send(body);
    } catch (_) {
      return res.status(502).json({detail: 'ไม่สามารถเผยแพร่แนวข้อสอบได้ กรุณาลองใหม่อีกครั้ง'});
    } finally { clearTimeout(timer); }
  });

  app.get('/api/guides/*path', async (req, res) => {
    res.set('Cache-Control', 'no-store');
    const upstreamPath = Array.isArray(req.params.path) ? req.params.path.join('/') : req.params.path;
    const listPath = /^courses\/[1-9]\d*\/guides$/.test(upstreamPath);
    const allowedPath = listPath
      || /^courses\/[1-9]\d*\/guides\/filter-options$/.test(upstreamPath)
      || /^guides\/[1-9]\d*$/.test(upstreamPath);
    const queryKeys = [...new URL(req.originalUrl, 'http://frontend').searchParams.keys()];
    if (!allowedPath || (!listPath && queryKeys.length)) {
      return res.status(404).json({detail: 'ไม่พบเส้นทางแนวข้อสอบ'});
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const base = new URL(backendUrl);
      if (!['http:', 'https:'].includes(base.protocol)) throw new Error('Invalid backend protocol');
      const target = new URL(`/${upstreamPath}`, base);
      for (const [key, value] of new URL(req.originalUrl, 'http://frontend').searchParams) {
        target.searchParams.append(key, value);
      }
      const headers = {Accept: 'application/json'};
      if (req.get('authorization')) headers.Authorization = req.get('authorization');
      const response = await fetch(target, {
        method: 'GET', headers, signal: controller.signal,
        cache: 'no-store', redirect: 'manual'
      });
      const body = await response.text();
      if (response.headers.get('content-type')) res.set('Content-Type', response.headers.get('content-type'));
      return res.status(response.status).send(body);
    } catch (_) {
      return res.status(502).json({detail: 'ไม่สามารถเชื่อมต่อบริการแนวข้อสอบได้ กรุณาลองใหม่อีกครั้ง'});
    } finally { clearTimeout(timer); }
  });

  app.use(express.static(path.join(__dirname, '../public')));
  app.use((error, req, res, next) => {
    if (req.path.startsWith('/api/auth') || req.path === '/api/guides' || req.path.startsWith('/api/my-guides/')) {
      return res.status(error.status === 413 ? 413 : 400).json({detail: 'ข้อมูลคำขอไม่ถูกต้อง'});
    }
    next(error);
  });
  return app;
}

if (require.main === module) {
  createApp().listen(5000, process.env.HOST || '127.0.0.1', () => {
    console.log('Frontend: http://127.0.0.1:5000');
  });
}

module.exports = {createApp};

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

  app.use(express.static(path.join(__dirname, '../public')));
  app.use((error, req, res, next) => {
    if (req.path.startsWith('/api/auth')) {
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

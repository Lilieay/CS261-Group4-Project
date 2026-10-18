// Login uses the same-origin /api/auth proxy in frontend/src/server.js.
// Keep tokenStorageKey aligned with upload-config.js.
window.LoginConfig = Object.freeze({
  apiBaseUrl: '',
  loginPath: '/api/auth/login',
  tokenStorageKey: 'access_token',
  successUrl: 'courses.html',
  timeoutMs: 15000
});

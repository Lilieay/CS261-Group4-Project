// Upload uses the authenticated API and same-origin frontend proxies.
window.GuidePublishConfig = Object.freeze({
  mode: 'api', // 'preview' | 'api'; API errors never fall back to preview.
  apiBaseUrl: window.location.origin,
  coursesPath: '/courses',
  publishPath: '/guides',
  mePath: '/api/auth/me',
  tokenStorageKey: 'access_token', // Login must store its access_token here.
  academicYears: [2569, 2568, 2567, 2566],
  timeoutMs: 15000
});

// Use preview with the existing localStorage pages. Change to api only when
// the publishing endpoint, course endpoint, and Login integration are ready.
window.GuidePublishConfig = Object.freeze({
  mode: 'preview', // 'preview' | 'api'; API errors never fall back to preview.
  apiBaseUrl: 'http://127.0.0.1:8000',
  coursesPath: '/courses',
  publishPath: '/guides',
  mePath: '/api/auth/me',
  tokenStorageKey: 'access_token', // Login must store its access_token here.
  academicYears: [2569, 2568, 2567, 2566],
  timeoutMs: 15000
});

(() => {
  'use strict';

  async function loadUser() {
    const token = sessionStorage.getItem('access_token');
    if (!token) return null;
    const response = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' },
      cache: 'no-store',
      signal: AbortSignal.timeout(10000)
    });
    if (response.status === 401) {
      sessionStorage.removeItem('access_token');
      return null;
    }
    if (!response.ok) throw new Error('โหลดข้อมูลผู้ใช้ไม่สำเร็จ');
    const user = await response.json();
    if (typeof user.username !== 'string' || typeof user.display_name !== 'string') {
      throw new Error('ข้อมูลผู้ใช้ไม่ถูกต้อง');
    }
    return user;
  }

  window.currentUserReady = loadUser();

  async function renderProfile() {
    try {
      const user = await window.currentUserReady;
      if (!user) {
        document.querySelectorAll('[data-user-name]').forEach(el => { el.textContent = 'เข้าสู่ระบบ'; });
        document.querySelectorAll('[data-profile-link]').forEach(el => { el.href = 'login.html'; });
        if (document.body.dataset.page === 'profile') window.location.replace('login.html');
        return;
      }
      const name = user.display_name.trim() || user.username;
      document.querySelectorAll('[data-user-name]').forEach(el => { el.textContent = name; });
      document.querySelectorAll('[data-user-id]').forEach(el => { el.textContent = user.username; });
      document.querySelectorAll('[data-user-avatar]').forEach(el => { el.textContent = Array.from(name)[0] || '?'; });
    } catch (_) {
      document.querySelectorAll('[data-user-name]').forEach(el => { el.textContent = 'โหลดข้อมูลไม่ได้'; });
      const status = document.getElementById('profile-status');
      if (status) status.textContent = 'โหลดข้อมูลไม่ได้ กรุณารีเฟรชหน้าเพื่อลองใหม่';
    }
  }
  renderProfile();
})();

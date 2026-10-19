(() => {
  'use strict';

  class CourseApiError extends Error {
    constructor(message, status = 0, payload = null) {
      super(message);
      this.name = 'CourseApiError';
      this.status = status;
      this.payload = payload;
    }
  }

  function login() {
    sessionStorage.removeItem(window.LoginConfig.tokenStorageKey);
    window.location.replace('login.html');
  }

  async function request(path, options = {}) {
    const token = sessionStorage.getItem(window.LoginConfig.tokenStorageKey);
    if (!token) {
      login();
      throw new CourseApiError('กรุณาเข้าสู่ระบบก่อนค้นหารายวิชา', 401);
    }

    let response;
    try {
      response = await fetch(`/api/courses${path}`, {
        ...options,
        headers: {...options.headers, Authorization: `Bearer ${token}`, Accept: 'application/json'},
        cache: 'no-store'
      });
    } catch (_) {
      throw new CourseApiError('เชื่อมต่อบริการรายวิชาไม่ได้ กรุณาลองใหม่');
    }

    let payload;
    try { payload = await response.json(); }
    catch (_) { payload = null; }
    if (response.status === 401) {
      login();
      throw new CourseApiError('เซสชันหมดอายุ กรุณาเข้าสู่ระบบใหม่', 401, payload);
    }
    if (!response.ok) {
      const detail = payload?.error?.message || payload?.detail || 'โหลดข้อมูลรายวิชาไม่สำเร็จ';
      throw new CourseApiError(detail, response.status, payload);
    }
    return payload;
  }

  function normalizeCourse(value) {
    if (!value || !Number.isSafeInteger(value.id) || value.id <= 0
        || typeof value.course_code !== 'string' || !value.course_code.startsWith('CS')
        || typeof value.course_name !== 'string') {
      throw new CourseApiError('รูปแบบข้อมูลรายวิชาจากบริการไม่ถูกต้อง');
    }
    return {
      id: value.id,
      code: value.course_code,
      name: value.course_name,
      instructorName: value.instructor_name ?? null,
      description: value.description ?? null
    };
  }

  async function searchCourses(search = '', options = {}) {
    const query = new URLSearchParams({search: search.trim()});
    const result = await request(`?${query}`, options);
    if (!Array.isArray(result)) throw new CourseApiError('รูปแบบรายการรายวิชาจากบริการไม่ถูกต้อง');
    return result.map(normalizeCourse);
  }

  async function getCourse(id, options = {}) {
    if (!/^[1-9]\d*$/.test(String(id))) {
      throw new CourseApiError('รหัสรายวิชาไม่ถูกต้อง', 422);
    }
    return normalizeCourse(await request(`/${encodeURIComponent(id)}`, options));
  }

  window.CourseApi = Object.freeze({CourseApiError, searchCourses, getCourse});
})();

(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  let courses = [];
  let requestNumber = 0;
  let controller = null;
  let debounceTimer = null;

  const {escapeHtml} = window.UiUtils;

  function courseCard(course) {
    const params = new URLSearchParams({courseId: String(course.id), course: course.code});
    const description = course.description || 'ยังไม่มีคำอธิบายรายวิชาจากระบบ';
    return `<article class="course-card"><div class="card-top"><span class="course-code-badge">${escapeHtml(course.code)}</span><span class="semester-text">รายวิชา</span></div><h2 class="course-name">${escapeHtml(course.name)}</h2><p class="course-desc">${escapeHtml(description)}</p><div class="card-footer"><a class="btn-open-course" href="choose-courses.html?${params}" aria-label="เปิดคลัง ${escapeHtml(course.code)}">เปิดคลัง <span aria-hidden="true">→</span></a></div></article>`;
  }

  function render() {
    const grid = $('#course-grid');
    grid.setAttribute('aria-busy', 'false');
    grid.innerHTML = courses.length
      ? courses.map(courseCard).join('')
      : '<div class="course-empty"><h2>ไม่พบรายวิชาที่ตรงกับคำค้น</h2><p>ลองค้นหาด้วยรหัสวิชาหรือชื่อวิชาอื่น</p></div>';
    $('#view-all').hidden = true;
  }

  function showError(error, search) {
    const status = $('#course-status');
    status.classList.add('error');
    status.replaceChildren(document.createTextNode(`${error.message} `));
    const retry = document.createElement('button');
    retry.type = 'button';
    retry.textContent = 'ลองอีกครั้ง';
    retry.addEventListener('click', () => loadCourses(search));
    status.append(retry);
  }

  async function loadCourses(search = $('#course-search').value) {
    const normalizedSearch = search.trim();
    const currentRequest = ++requestNumber;
    if (controller) controller.abort();
    controller = new AbortController();
    const status = $('#course-status');
    status.classList.remove('error');
    status.textContent = 'กำลังโหลดรายวิชา…';
    $('#course-grid').setAttribute('aria-busy', 'true');
    $('#course-grid').replaceChildren();
    try {
      const result = await window.CourseApi.searchCourses(normalizedSearch, {signal: controller.signal});
      if (currentRequest !== requestNumber) return;
      courses = result;
      render();
      status.textContent = `พบ ${courses.length} รายวิชา`;
    } catch (error) {
      if (currentRequest !== requestNumber || error.name === 'AbortError') return;
      if (error.status === 401) return;
      courses = [];
      $('#course-grid').setAttribute('aria-busy', 'false');
      $('#course-grid').replaceChildren();
      showError(error, normalizedSearch);
    }
  }

  function scheduleSearch() {
    clearTimeout(debounceTimer);
    requestNumber += 1;
    if (controller) controller.abort();
    debounceTimer = setTimeout(() => loadCourses(), 250);
  }

  function start() {
    $('#course-search-form').addEventListener('submit', event => {
      event.preventDefault();
      clearTimeout(debounceTimer);
      loadCourses();
    });
    $('#course-search').addEventListener('input', scheduleSearch);
    $('#view-all').addEventListener('click', () => {
      $('#course-search').value = '';
      loadCourses('');
    });
    loadCourses('');
  }

  start();
})();

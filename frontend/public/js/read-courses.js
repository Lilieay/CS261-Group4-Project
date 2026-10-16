(() => {
  'use strict';
  const data = window.CourseData;
  const e = data.escapeHtml;
  const params = new URL(window.location.href).searchParams;
  const course = data.findCourse(params.get('course'));
  const guideId = params.get('guide');
  const content = document.querySelector('#readingContent');
  const back = document.querySelector('#readingBack');

  function safeReturnUrl(candidate, code) {
    const fallback = code ? `choose-courses.html?${new URLSearchParams({course:code})}` : 'courses.html';
    if (!candidate) return fallback;
    try {
      const url = new URL(candidate, window.location.href);
      const expected = new URL('choose-courses.html', window.location.href);
      if (url.origin !== expected.origin || url.pathname !== expected.pathname || url.searchParams.get('course') !== code) return fallback;
      return `choose-courses.html${url.search}${url.hash}`;
    } catch (_) { return fallback; }
  }

  function render() {
    back.href = safeReturnUrl(params.get('returnTo'), course?.code);
    let row = null;
    let error = '';
    try { row = course && guideId ? data.loadExams().find(item => item.id === guideId && item.course_code === course.code) : null; }
    catch (failure) { error = failure.message; }
    if (!row) {
      document.title = 'ไม่พบแนวข้อสอบ';
      content.innerHTML = `<section class="reading-empty" role="status"><h1>${error ? 'โหลดข้อมูลไม่สำเร็จ' : 'ไม่พบแนวข้อสอบ'}</h1><p>${e(error || 'รายการไม่มีอยู่หรือถูกลบแล้ว')}</p><a class="reading-back-button" href="${e(back.href)}">กลับหน้ารายวิชา</a></section>`;
      return;
    }
    document.title = `${row.title} | อ่านแนวข้อสอบ`;
    const counts = data.questionCounts(row);
    const format = row.formats.join(' / ') || 'ไม่ระบุ';
    const count = value => value == null ? 'ไม่ระบุ' : `${value} ข้อ`;
    content.innerHTML = `<h1>${e(row.title)}</h1><div class="subheading"><p>แบ่งปันโดย ${e(data.publisherName(row))}</p></div><p class="reading-course-name">${e(course.code)} ${e(course.name)}</p><div class="meta-grid"><div>รายวิชา : <strong>${e(course.code)}</strong></div><div>ปีการศึกษา: <strong>${e(row.year)}</strong></div><div>ภาคเรียน: <strong>${e(data.semesterLabel(row.semester))}</strong></div><div>ช่วงสอบ : <strong>${e(row.period)}</strong></div></div><section class="info-card topics-card"><h2>หัวข้อที่เคยออกสอบ</h2><p class="reading-text">${e(row.topics || 'ไม่ระบุ')}</p></section><section class="info-card format-card"><h2>รูปแบบแนวข้อสอบ — ${e(format)}</h2><div class="format-grid"><div>ปรนัย : <strong>${e(count(counts.objective))}</strong></div><div>อัตนัย : <strong>${e(count(counts.essay))}</strong></div></div></section><section class="info-card advice-card"><h2>คำแนะนำเพิ่มเติม</h2><p class="reading-text">${e(String(row.notes || '').trim() || 'ไม่ระบุ')}</p></section><p class="reading-preview">ข้อมูลตัวอย่างร่วมกับหน้ารายวิชาที่แบ่งปัน</p><div class="actions"><button class="save-button" type="button"><svg class="icon" aria-hidden="true"><use href="#i-save"/></svg> บันทึก</button><button class="review-button" type="button"><span aria-hidden="true">★</span> รีวิว</button></div>`;
  }
  render();
  window.addEventListener('storage', event => { if (event.key === data.storageKey || event.key === null) render(); });
  window.addEventListener('focus', render);
})();

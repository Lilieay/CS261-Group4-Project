(() => {
  'use strict';
  const data = window.CourseData;
  const e = data.escapeHtml;
  const $ = selector => document.querySelector(selector);
  function render() {
    try {
      const rows = data.listSaved();
      const query = $('#saved-search').value.trim().toLocaleLowerCase();
      const filtered = rows.filter(row => `${row.course_code} ${data.findCourse(row.course_code)?.name || ''} ${row.title} ${row.topics}`.toLocaleLowerCase().includes(query));
      $('#saved-count').textContent = `บันทึกไว้ ${rows.length} รายการ`;
      $('#saved-list').innerHTML = filtered.length ? filtered.map(row => {
        const query = new URLSearchParams({course: row.course_code, guide: row.id, returnTo: 'saved-courses.html'});
        return `<article class="saved-card"><div class="saved-card-heading"><span class="saved-code">${e(row.course_code)}</span><span>ปี ${e(row.year)} · ภาคเรียน${e(data.semesterLabel(row.semester))} · ${e(row.period)}</span></div><h2>${e(row.title)}</h2><p>${e(row.topics)}</p><div class="saved-card-bottom"><span>${row.rating == null ? 'ยังไม่มีรีวิว' : `★ ${e(row.rating)} (${e(row.reviews)} รีวิว)`}</span><div><a href="read-courses.html?${e(query.toString())}">เปิดอ่าน →</a><button type="button" data-unsave="${e(row.id)}" aria-label="นำ ${e(row.title)} ออกจากรายการที่บันทึก">นำออก</button></div></div></article>`;
      }).join('') : `<div class="reading-empty"><h2>${rows.length ? 'ไม่พบรายการที่ตรงกับการค้นหา' : 'ยังไม่มีรายการที่บันทึก'}</h2><p>${rows.length ? 'ลองเปลี่ยนคำค้นหาหรือล้างคำค้นหา' : 'เปิดอ่านแนวข้อสอบแล้วกดบันทึก เพื่อกลับมาอ่านภายหลัง'}</p>${rows.length ? '<button id="saved-clear" type="button">ล้างคำค้นหา</button>' : '<a class="reading-back-button" href="courses.html">ค้นหารายวิชา</a>'}</div>`;
    } catch (error) {
      $('#saved-count').textContent = '';
      $('#saved-list').innerHTML = `<div class="reading-empty" role="alert"><h2>โหลดรายการไม่สำเร็จ</h2><p>${e(error.message)}</p></div>`;
    }
  }
  $('#saved-search').addEventListener('input', render);
  $('#saved-search-form').addEventListener('submit', event => { event.preventDefault(); render(); });
  $('#saved-list').addEventListener('click', event => {
    if (event.target.closest('#saved-clear')) { $('#saved-search').value = ''; render(); $('#saved-search').focus(); return; }
    const button = event.target.closest('[data-unsave]');
    if (!button) return;
    try {
      // Recheck after an external tab may have changed the bookmark.
      const row = data.getExam(button.dataset.unsave);
      if (row.saved) data.toggleSaved(row.id);
      else render();
      $('#saved-status').textContent = 'นำรายการออกแล้ว';
      $('#saved-search').focus();
    } catch (error) { $('#saved-status').textContent = error.message || 'นำรายการออกไม่สำเร็จ'; }
  });
  render();
  data.subscribe(render);
})();

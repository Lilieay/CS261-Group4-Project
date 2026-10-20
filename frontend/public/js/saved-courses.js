(() => {
  'use strict';
  const data = window.UiUtils;
  const e = data.escapeHtml;
  const $ = selector => document.querySelector(selector);
  let rows = [];
  let loading = true;
  let failure = '';
  let version = 0;
  let removing = false;

  function render() {
    $('#saved-list').setAttribute('aria-busy', String(loading || removing));
    $('#saved-count').textContent = loading || failure ? '' : `บันทึกไว้ ${rows.length} รายการ`;
    if (loading) { $('#saved-list').innerHTML = '<p role="status">กำลังโหลดรายการที่บันทึก…</p>'; return; }
    if (failure) {
      $('#saved-list').innerHTML = `<div class="reading-empty" role="alert"><h2>โหลดรายการไม่สำเร็จ</h2><p>${e(failure)}</p><button type="button" id="saved-retry">ลองอีกครั้ง</button></div>`;
      return;
    }
    const query = $('#saved-search').value.trim().toLocaleLowerCase();
    const filtered = rows.filter(row => `${row.course_code} ${row.course_name} ${row.title} ${row.topics}`.toLocaleLowerCase().includes(query));
    $('#saved-list').innerHTML = filtered.length ? filtered.map(row => {
      const query = new URLSearchParams({course: row.course_code, courseId: row.course_id,
        guide: row.id, source: 'api', returnTo: 'saved-courses.html'});
      return `<article class="saved-card"><div class="saved-card-heading"><span class="saved-code">${e(row.course_code)}</span><span>ปี ${e(row.year)} · ภาคเรียน${e(data.semesterLabel(row.semester))} · ${e(row.period)}</span></div><h2>${e(row.title)}</h2><p>${e(row.topics)}</p><div class="saved-card-bottom"><span>${e(row.course_name)}</span><div><a href="read-courses.html?${e(query.toString())}">เปิดอ่าน →</a><button type="button" data-unsave="${e(row.id)}" ${removing ? 'disabled' : ''} aria-label="นำ ${e(row.title)} ออกจากรายการที่บันทึก">นำออก</button></div></div></article>`;
    }).join('') : `<div class="reading-empty"><h2>${rows.length ? 'ไม่พบรายการที่ตรงกับการค้นหา' : 'ยังไม่มีรายการที่บันทึก'}</h2><p>${rows.length ? 'ลองเปลี่ยนคำค้นหาหรือล้างคำค้นหา' : 'เปิดอ่านแนวข้อสอบแล้วกดบันทึก เพื่อกลับมาอ่านภายหลัง'}</p>${rows.length ? '<button id="saved-clear" type="button">ล้างคำค้นหา</button>' : '<a class="reading-back-button" href="courses.html">ค้นหารายวิชา</a>'}</div>`;
  }

  async function load() {
    if (removing) return;
    const current = ++version;
    loading = true; failure = ''; rows = []; render();
    try {
      const user = await window.currentUserReady;
      if (!user) { window.location.replace('login.html'); return; }
      const result = await window.GuideApi.saved();
      if (current !== version) return;
      rows = result;
    } catch (error) {
      if (current !== version) return;
      failure = error.message || 'ติดต่อเซิร์ฟเวอร์ไม่ได้';
    }
    if (current !== version) return;
    loading = false; render();
  }

  $('#saved-search').addEventListener('input', render);
  $('#saved-search-form').addEventListener('submit', event => { event.preventDefault(); render(); });
  $('#saved-list').addEventListener('click', async event => {
    if (event.target.closest('#saved-retry')) { load(); return; }
    if (event.target.closest('#saved-clear')) { $('#saved-search').value = ''; render(); $('#saved-search').focus(); return; }
    const button = event.target.closest('[data-unsave]');
    if (!button || removing || loading) return;
    removing = true;
    ++version;
    render();
    $('#saved-status').textContent = 'กำลังนำรายการออก…';
    try {
      await window.GuideApi.savedState(button.dataset.unsave, false);
      rows = rows.filter(row => row.id !== button.dataset.unsave);
      $('#saved-status').textContent = 'นำรายการออกแล้ว';
    } catch (error) {
      $('#saved-status').textContent = error.message || 'นำรายการออกไม่สำเร็จ';
      // Reload because a timed out request may already have succeeded.
      removing = false;
      await load();
    } finally {
      removing = false; render(); $('#saved-search').focus();
    }
  });
  load();
  window.addEventListener('focus', load);
})();

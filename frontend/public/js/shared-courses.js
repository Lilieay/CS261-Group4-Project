'use strict';
// The preview pages share one repository. Login/API authorization remains a separate integration.
const COURSE_CATALOG = window.CourseData.catalog;
const CURRENT_USER = window.CourseData.currentUser;
const STORAGE_KEY = window.CourseData.storageKey;
const $ = selector => document.querySelector(selector);
const escapeHtml = window.CourseData.escapeHtml;
const courseName = code => window.CourseData.findCourse(code)?.name ?? code;
const repository = {
  list() { return window.CourseData.listMine().sort((a, b) => (Date.parse(b.created_at || b.updated_at) || 0) - (Date.parse(a.created_at || a.updated_at) || 0)); },
  get(id) { const row = this.list().find(row => row.id === id); if (!row) throw new Error('ไม่พบรายการหรือรายการถูกลบแล้ว'); return row; },
  update(id, changes) { window.CourseData.updateExam(id, changes); },
  remove(id) { window.CourseData.removeExam(id); }
};
let editingId = null;
let deletingId = null;
let readingId = null;
const icon = name => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
function notify(message, error = false) { $('#status').textContent = message; $('#status').classList.toggle('error', error); }
function safely(fn) { try { fn(); } catch (error) { notify(error.message || 'ดำเนินการไม่สำเร็จ ข้อมูลเดิมยังไม่เปลี่ยนแปลง', true); } }
function questionBreakdown(row) {
  const parts = [];
  if (row.essay_count != null) parts.push(`อัตนัย ${row.essay_count} ข้อ`);
  if (row.objective_count != null) parts.push(`ปรนัย ${row.objective_count} ข้อ`);
  return parts.join(' / ');
}
function cardQuestionCounts(row) {
  const validCount = value => Number.isSafeInteger(value) && value >= 0 ? value : null;
  // Current preview uses essay_count; the design document calls it subjective_count.
  const hasSplit = ['essay_count', 'subjective_count', 'objective_count']
    .some(key => Object.hasOwn(row, key));
  if (hasSplit) {
    return {
      essay: validCount(Object.hasOwn(row, 'essay_count') ? row.essay_count : row.subjective_count),
      objective: validCount(row.objective_count)
    };
  }
  // Old records only have a total. Infer a count only for a single known format.
  const single = row.formats.length === 1 ? row.formats[0] : '';
  return {
    essay: single === 'อัตนัย' ? validCount(row.question_count) : null,
    objective: single === 'ปรนัย' ? validCount(row.question_count) : null
  };
}

function formatQuestionCount(count) {
  return count === null ? 'ไม่ระบุ' : `${count} ข้อ`;
}

function compactExamTitle(row) {
  const title = String(row.title ?? '').trim();
  const course = courseName(row.course_code);
  const automaticTitle = `แนวข้อสอบ${row.period} ${row.course_code} ${course} ปีการศึกษา ${row.year}`;
  const normalize = value => value.replace(/\s+/gu, '').toLocaleLowerCase();
  // Only shorten the standard generated title; preserve custom exam names.
  return normalize(title) === normalize(automaticTitle)
    ? `แนวข้อสอบ${row.period} — ${course}`
    : title;
}

function card(row) {
  const e = escapeHtml;
  const counts = cardQuestionCounts(row);
  return `<article class="exam-card"><div><div class="badges"><span class="badge code">${e(row.course_code)}</span><span class="badge">ปีการศึกษา ${e(row.year)}</span><span class="badge semester">ภาคเรียนที่ ${e(row.semester)}</span><span class="badge period">● ${e(row.period)}</span></div><h3 class="exam-card-title" title="${e(row.title)}">${e(compactExamTitle(row))}</h3><p class="description">แนวข้อสอบที่รวบรวมจากหัวข้อ ${e(row.topics)}${String(row.notes ?? "").trim() ? `<br>${e(row.notes)}` : ""}</p><div class="metadata"><div><span>รูปแบบข้อสอบ:</span><b>${e(row.formats.join(' / ') || 'ไม่ระบุ')}</b></div><div><span>อัตนัย:</span><b>${e(formatQuestionCount(counts.essay))}</b></div><div><span>ปรนัย:</span><b>${e(formatQuestionCount(counts.objective))}</b></div></div></div><aside class="card-side"><dl class="stats"><div><dt><span class="star">★</span>คะแนนรีวิว</dt><dd>${row.rating == null ? 'ยังไม่มีรีวิว' : e(row.rating)}<small>( ${e(row.reviews)} รีวิว)</small></dd></div><div><dt>${icon('eye')}ผู้เปิดอ่าน</dt><dd>${e(row.views)} ครั้ง</dd></div><div><dt>${icon('download')}ดาวน์โหลด</dt><dd>${e(row.downloads)} ครั้ง</dd></div></dl><p class="updated">อัปเดตเมื่อ: ${e(new Date(row.updated_at).toLocaleDateString('th-TH', { day: 'numeric', month: 'short', year: 'numeric' }))}</p><div class="card-actions"><button class="open" data-action="read" data-id="${e(row.id)}">${icon('book')}เปิดอ่านแนวข้อสอบ</button><button data-action="edit" data-id="${e(row.id)}">${icon('edit')}แก้ไขข้อมูล</button><button class="delete" data-action="delete" data-id="${e(row.id)}">${icon('trash')}ลบรายการ</button></div></aside></article>`;
}
function render() {
  const rows = repository.list();
  const query = $('#search').value.trim().toLocaleLowerCase();
  const course = $('#course-filter').value;
  const year = $('#year-filter').value;
  const filtered = rows.filter(row => (!course || row.course_code === course) && (!year || row.year === year) && `${row.course_code} ${courseName(row.course_code)} ${row.title} ${row.year}`.toLocaleLowerCase().includes(query));
  $('#exam-list').innerHTML = filtered.length ? filtered.map(card).join('') : `<div class="empty"><h3>${rows.length ? 'ไม่พบแนวข้อสอบที่ตรงกับการค้นหา' : 'คุณยังไม่ได้เผยแพร่แนวข้อสอบ'}</h3><p>${rows.length ? 'ลองเปลี่ยนคำค้นหาหรือล้างตัวกรอง' : 'เริ่มแบ่งปันแนวข้อสอบให้เพื่อนในรายวิชา'}</p>${rows.length ? '<button id="clear-filters" class="primary">ล้างตัวกรอง</button>' : '<a href="upload.html" class="primary">เผยแพร่แนวข้อสอบ</a>'}</div>`;
  $('#chips').innerHTML = [course && ['course', course], year && ['year', year]].filter(Boolean).map(([type, value]) => `<button data-clear="${type}" aria-label="ล้างตัวกรอง ${escapeHtml(value)}">${escapeHtml(value)} ×</button>`).join('');
}
function refreshOptions() {
  const rows = repository.list();
  const year = $('#year-filter').value;
  $('#year-filter').innerHTML = '<option value="">ทุกปีการศึกษา</option>' + [...new Set(rows.map(row => row.year))].sort().reverse().map(y => `<option>${escapeHtml(y)}</option>`).join('');
  if ([...$('#year-filter').options].some(option => option.value === year)) $('#year-filter').value = year;
}
function showReader(id) {
  const row = repository.get(id);
  window.location.assign(`read-courses.html?${new URLSearchParams({course: row.course_code, guide: row.id})}`);
}

$('#exam-list').addEventListener('click', event => safely(() => {
  if (event.target.closest('#clear-filters')) { $('#search').value = ''; $('#course-filter').value = ''; $('#year-filter').value = ''; render(); return; }
  const button = event.target.closest('[data-action]'); if (!button) return;
  const row = repository.get(button.dataset.id);
  if (button.dataset.action === 'read') showReader(row.id);
  if (button.dataset.action === 'edit') showEditor(row.id);
  if (button.dataset.action === 'delete') { deletingId = row.id; $('#delete-title').textContent = row.title; $('#delete-dialog').showModal(); }
}));

$('#confirm-delete').addEventListener('click', () => safely(() => { repository.remove(deletingId); $('#delete-dialog').close(); refreshOptions(); render(); notify('ลบรายการตัวอย่างในเบราว์เซอร์แล้ว'); }));
document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => document.getElementById(button.dataset.close).close()));
$('#search-form').addEventListener('submit', event => { event.preventDefault(); safely(render); });
$('#search').addEventListener('input', () => safely(render));
function setFiltersOpen(open) {
  $('#filters').hidden = !open;
  $('#filter-toggle').setAttribute('aria-expanded', String(open));
}
$('#filter-toggle').addEventListener('click', () => {
  setFiltersOpen($('#filters').hidden);
});
for (const selector of ['#course-filter', '#year-filter']) {
  $(selector).addEventListener('change', () => {
    safely(() => {
      render();
      setFiltersOpen(false);
      $('#filter-toggle').focus();
    });
  });
}
$('#chips').addEventListener('click', event => { const button = event.target.closest('[data-clear]'); if (button) { $(button.dataset.clear === 'course' ? '#course-filter' : '#year-filter').value = ''; safely(render); } });
$('#reset-demo').addEventListener('click', () => safely(() => { window.CourseData.resetDemo(); $('#course-filter').value = ''; refreshOptions(); render(); notify('คืนค่าข้อมูลตัวอย่างแล้ว'); }));
const tabs = [$('#exams-tab'), $('#summaries-tab')];
function selectTab(selected) { tabs.forEach((tab, index) => { const active = index === selected; tab.setAttribute('aria-selected', String(active)); tab.tabIndex = active ? 0 : -1; document.getElementById(tab.getAttribute('aria-controls')).hidden = !active; }); }
tabs.forEach((tab, index) => { tab.addEventListener('click', () => selectTab(index)); tab.addEventListener('keydown', event => { if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) { event.preventDefault(); const next = event.key === 'Home' ? 0 : event.key === 'End' ? 1 : 1 - index; selectTab(next); tabs[next].focus(); } }); });
window.CourseData.subscribe(() => safely(() => {
  const ids = new Set(window.CourseData.loadExams().map(row => row.id));
  for (const [dialog, id] of [['reader', readingId], ['editor', editingId], ['delete-dialog', deletingId]]) {
    if (document.getElementById(dialog).open && id && !ids.has(id)) {
      document.getElementById(dialog).close();
      notify('รายการนี้ถูกลบแล้ว');
    }
  }
  refreshOptions(); render();
}));
safely(() => {
  const options = COURSE_CATALOG.map(course => `<option value="${escapeHtml(course.code)}">${escapeHtml(course.code + ' ' + course.name)}</option>`).join('');
  $('#course-filter').insertAdjacentHTML('beforeend', options); $('#edit-course').innerHTML = options;
  $('#course-filter').value = ''; refreshOptions(); render();
});


const COURSE_CATALOG = [{ "code": "CS100", "name": "BASIC WEB DEVELOPMENT" }, { "code": "CS101", "name": "DISCRETE STRUCTURES" }, { "code": "CS102", "name": "PROBLEM SOLVING BASICS AND COMPUTER PROGRAMMING" }, { "code": "CS103", "name": "INTRODUCTION TO COMPUTER PROGRAMMING" }, { "code": "CS104", "name": "INTRODUCTION TO COMPUTER PROGRAMMING USING PYTHON" }, { "code": "CS213", "name": "DATA STRUCTURES" }, { "code": "CS221", "name": "INTRODUCTION TO COMPUTER SYSTEM AND ORGANIZATION" }, { "code": "CS223", "name": "VIRTUALIZATION TECHNOLOGY" }, { "code": "CS224", "name": "LINUX ADMINISTRATION AND PERFORMANCE MONITORING" }, { "code": "CS240", "name": "PRINCIPLES OF DATA SCIENCE" }, { "code": "CS241", "name": "PROGRAMMING LANGUAGES AND PARADIGMS" }, { "code": "CS261", "name": "INTRODUCTION TO SOFTWARE ENGINEERING" }, { "code": "CS263", "name": "SOFTWARE REQUIREMENT SPECIFICATION" }, { "code": "CS265", "name": "BASIC MOBILE DEVELOPMENT" }, { "code": "CS301", "name": "PREPARATION FOR SENIOR PROJECTS AND CO-OPERATIVE EDUCATION" }, { "code": "CS303", "name": "SPECIAL PROJECTS 1" }, { "code": "CS331", "name": "NET-CENTRIC COMPUTING" }, { "code": "CS341", "name": "BIG DATA ENGINEERING" }, { "code": "CS345", "name": "PRACTICAL MACHINE LEARNING" }, { "code": "CS346", "name": "BIG DATA APPLICATIONS AND ANALYTICS" }, { "code": "CS361", "name": "CLOUD-BASED SOFTWARE ARCHITECTING" }, { "code": "CS364", "name": "MOBILE APPLICATION DEVELOPMENT" }, { "code": "CS373", "name": "ADVANCED SEARCH STRATEGIES" }, { "code": "CS374", "name": "NATURAL LANGUAGE PROCESSING" }, { "code": "CS384", "name": "HUMAN \\- COMPUTER INTERACTION" }, { "code": "CS403", "name": "SPECIAL PROJECTS 2" }, { "code": "CS404", "name": "CO-OPERATIVE EDUCATION 2" }, { "code": "CS440", "name": "SELECTED TOPICS IN DATA SCIENCE" }];
'use strict';
// PREVIEW ONLY. Replace the repository methods with the team's authenticated API.
// The server must enforce owner authorization for every read/update/delete request.
const CURRENT_USER = 'demo-owner';
const STORAGE_KEY = 'cs261-u5-preview-v1';
const $ = selector => document.querySelector(selector);
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const courseName = code => COURSE_CATALOG.find(course => course.code === code)?.name ?? code;
const seed = () => [2567, 2568].map((year, index) => ({
  id: `demo-exam-${index + 1}`, owner_id: CURRENT_USER, course_code: 'CS261',
  title: `แนวข้อสอบกลางภาค CS261 ${courseName('CS261')} ปีการศึกษา ${year}`,
  year: String(year), semester: '1', period: 'กลางภาค',
  topics: 'Software Process, Requirements Engineering, Use Case, UML และการออกแบบซอฟต์แวร์',
  notes: 'ตัวอย่างสำหรับทดลอง UI: ทบทวนแนวคิดจากบทเรียนและฝึกวิเคราะห์กรณีศึกษา ข้อมูลนี้ไม่ใช่แนวข้อสอบที่ผู้ใช้เผยแพร่จริง',
  formats: ['อัตนัย'], question_count: 6, instructor: 'ยังไม่มีข้อมูลผู้สอน',
  rating: '4.9', reviews: 18, views: 340, downloads: 128, updated_at: '2024-09-18T12:00:00Z'
}));
function readStore() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === null) return seed();
  const rows = JSON.parse(stored);
  if (!Array.isArray(rows) || rows.some(row => !row || typeof row.id !== 'string' || !Array.isArray(row.formats))) throw new Error('ข้อมูลตัวอย่างไม่ถูกต้อง กรุณากดคืนค่าข้อมูลตัวอย่าง');
  return rows;
}
// Re-read storage on every mutation to avoid resurrecting records deleted in another tab.
const repository = {
  list() { return readStore().filter(row => row.owner_id === CURRENT_USER); },
  get(id) { const row = this.list().find(row => row.id === id); if (!row) throw new Error('ไม่พบรายการหรือรายการถูกลบแล้ว'); return row; },
  update(id, changes) { const rows = readStore(); const i = rows.findIndex(row => row.id === id && row.owner_id === CURRENT_USER); if (i < 0) throw new Error('ไม่พบรายการหรือรายการถูกลบแล้ว'); rows[i] = { ...rows[i], ...changes, id: rows[i].id, owner_id: rows[i].owner_id, updated_at: new Date().toISOString() }; localStorage.setItem(STORAGE_KEY, JSON.stringify(rows)); },
  remove(id) { this.get(id); const rows = readStore(); localStorage.setItem(STORAGE_KEY, JSON.stringify(rows.filter(row => !(row.id === id && row.owner_id === CURRENT_USER)))); }
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
  return `<article class="exam-card"><div><div class="badges"><span class="badge code">${e(row.course_code)}</span><span class="badge">ปีการศึกษา ${e(row.year)}</span><span class="badge semester">ภาคเรียนที่ ${e(row.semester)}</span><span class="badge period">● ${e(row.period)}</span></div><h3 class="exam-card-title" title="${e(row.title)}">${e(compactExamTitle(row))}</h3><p class="description">แนวข้อสอบที่รวบรวมจากหัวข้อ ${e(row.topics)}${String(row.notes ?? "").trim() ? `<br>${e(row.notes)}` : ""}</p><div class="metadata"><div><span>รูปแบบข้อสอบ:</span><b>${e(row.formats.join(' / ') || 'ไม่ระบุ')}</b></div><div><span>อัตนัย:</span><b>${e(formatQuestionCount(counts.essay))}</b></div><div><span>ปรนัย:</span><b>${e(formatQuestionCount(counts.objective))}</b></div></div></div><aside class="card-side"><dl class="stats"><div><dt><span class="star">★</span>คะแนนรีวิว</dt><dd>${e(row.rating)}<small>( ${e(row.reviews)} รีวิว)</small></dd></div><div><dt>${icon('eye')}ผู้เปิดอ่าน</dt><dd>${e(row.views)} ครั้ง</dd></div><div><dt>${icon('download')}ดาวน์โหลด</dt><dd>${e(row.downloads)} ครั้ง</dd></div></dl><p class="updated">อัปเดตเมื่อ: ${e(new Date(row.updated_at).toLocaleDateString('th-TH', { day: 'numeric', month: 'short', year: 'numeric' }))}</p><div class="card-actions"><button class="open" data-action="read" data-id="${e(row.id)}">${icon('book')}เปิดอ่านแนวข้อสอบ</button><button data-action="edit" data-id="${e(row.id)}">${icon('edit')}แก้ไขข้อมูล</button><button class="delete" data-action="delete" data-id="${e(row.id)}">${icon('trash')}ลบรายการ</button></div></aside></article>`;
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
  const row = repository.get(id); readingId = id;
  const fields = [['รายวิชา', `${row.course_code} ${courseName(row.course_code)}`], ['ชื่อแนวข้อสอบ', row.title], ['ปี / ภาคเรียน', `${row.year} / ${row.semester}`], ['ช่วงสอบ', row.period], ['หัวข้อ', row.topics], ['รูปแบบ', row.formats.join(' / ')], ['จำนวนข้อ', row.question_count ?? 'ไม่ระบุ'], ['แยกจำนวนข้อ', questionBreakdown(row) || 'ไม่ระบุ'], ['ผู้สอน', row.instructor], ['ข้อมูลเสริม', row.notes || 'ไม่ระบุ']];
  $('#reader-content').innerHTML = `<dl class="reader-grid">${fields.map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd>`).join('')}</dl>`;
  $('#reader').showModal();
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
$('#reset-demo').addEventListener('click', () => safely(() => { localStorage.setItem(STORAGE_KEY, JSON.stringify(seed())); $('#course-filter').value = 'CS261'; refreshOptions(); render(); notify('คืนค่าข้อมูลตัวอย่างแล้ว'); }));
const tabs = [$('#exams-tab'), $('#summaries-tab')];
function selectTab(selected) { tabs.forEach((tab, index) => { const active = index === selected; tab.setAttribute('aria-selected', String(active)); tab.tabIndex = active ? 0 : -1; document.getElementById(tab.getAttribute('aria-controls')).hidden = !active; }); }
tabs.forEach((tab, index) => { tab.addEventListener('click', () => selectTab(index)); tab.addEventListener('keydown', event => { if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) { event.preventDefault(); const next = event.key === 'Home' ? 0 : event.key === 'End' ? 1 : 1 - index; selectTab(next); tabs[next].focus(); } }); });
window.addEventListener('storage', event => { if (event.key === STORAGE_KEY || event.key === null) safely(() => { for (const [dialog, id] of [['reader', readingId], ['editor', editingId], ['delete-dialog', deletingId]]) { if (document.getElementById(dialog).open) { document.getElementById(dialog).close(); notify('ข้อมูลเปลี่ยนจากหน้าต่างอื่น กรุณาเปิดรายการใหม่'); } } refreshOptions(); render(); }); });
safely(() => {
  const options = COURSE_CATALOG.map(course => `<option value="${escapeHtml(course.code)}">${escapeHtml(course.code + ' ' + course.name)}</option>`).join('');
  $('#course-filter').insertAdjacentHTML('beforeend', options); $('#edit-course').innerHTML = options;
  $('#course-filter').value = 'CS261'; refreshOptions(); render();
});


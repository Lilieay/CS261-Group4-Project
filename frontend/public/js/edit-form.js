'use strict';
// Load after shared-courses.js. Reuses the preview repository and current record ID.
let editorTopics = [];
const editFieldIds = {course_code:'edit-course', title:'edit-title', year:'edit-year', semester:'edit-semester', period:'edit-period', formats:'edit-formats', question_count:'edit-count', topics:'edit-tags'};
const editErrorIds = {course_code:'edit-course-error', title:'edit-title-error', year:'edit-year-error', semester:'edit-semester-error', period:'edit-period-error', formats:'edit-formats-error', question_count:'edit-count-error', topics:'edit-topics-error'};
const TITLE_ERROR = 'กรุณากรอกชื่อแนวข้อสอบ ห้ามเว้นว่างหรือใส่เฉพาะช่องว่าง';

function normalizeEditorTopics(values) {
  const found = new Set();
  return values.map(value => String(value).trim()).filter(value => {
    const key = value.toLocaleLowerCase();
    if (!value || found.has(key)) return false;
    found.add(key); return true;
  });
}

function validateEditValues(values, courses) {
  const errors = {};
  if (!courses.some(course => course.code === values.course_code)) errors.course_code = 'กรุณาเลือกรายวิชาที่มีอยู่ในระบบ';
  if (!values.title.trim()) errors.title = TITLE_ERROR;
  else if (values.title.length > 255) errors.title = 'ชื่อแนวข้อสอบต้องไม่เกิน 255 ตัวอักษร';
  if (!['2566','2567','2568','2569'].includes(values.year)) errors.year = 'กรุณาเลือกปีการศึกษา';
  if (!['1','2','ฤดูร้อน'].includes(values.semester)) errors.semester = 'กรุณาเลือกภาคเรียน';
  if (!['กลางภาค','ปลายภาค'].includes(values.period)) errors.period = 'กรุณาเลือกช่วงการสอบ';
  if (!values.formats.length || values.formats.some(value => !['ปรนัย','อัตนัย','ผสม','อื่น ๆ'].includes(value))) errors.formats = 'กรุณาเลือกรูปแบบข้อสอบ';
  if (!values.topics.trim()) errors.topics = 'กรุณาเพิ่มหัวข้อที่เคยออกสอบอย่างน้อยหนึ่งหัวข้อ';
  if (values.question_count !== null && (!Number.isInteger(values.question_count) || values.question_count <= 0)) errors.question_count = 'จำนวนข้อต้องเป็นจำนวนเต็มมากกว่า 0 หรือเว้นว่าง';
  return errors;
}

function showEditorFieldError(key, message = '') {
  const control = document.getElementById(editFieldIds[key]);
  const error = document.getElementById(editErrorIds[key]);
  control.setAttribute('aria-invalid', String(Boolean(message)));
  error.textContent = message;
  error.hidden = !message;
  if (key === 'topics') $('#edit-tag-input').setAttribute('aria-invalid', String(Boolean(message)));
}

function clearEditorErrors() {
  Object.keys(editFieldIds).forEach(key => showEditorFieldError(key));
  $('#edit-error').hidden = true; $('#edit-error').textContent = '';
}

function renderEditorTopics() {
  $('#edit-tag-list').innerHTML = editorTopics.map((topic, index) => `<span class="edit-topic-tag"><span>${escapeHtml(topic)}</span><button type="button" data-remove-topic="${index}" aria-label="ลบแท็ก ${escapeHtml(topic)}">×</button></span>`).join('');
}

function commitEditorTopic() {
  const text = $('#edit-tag-input').value.trim();
  if (!text) return;
  editorTopics = normalizeEditorTopics([...editorTopics, ...text.split(/[,\n]+/)]);
  $('#edit-tag-input').value = '';
  renderEditorTopics();
  if (editorTopics.length) showEditorFieldError('topics');
}

function readEditorValues() {
  const form = $('#edit-form');
  const value = key => String(form.elements.namedItem(key).value ?? '').trim();
  const count = value('question_count');
  return {course_code:value('course_code'), title:value('title'), year:value('year'), semester:value('semester'), period:value('period'), formats:value('formats').split('|').filter(Boolean), question_count:count === '' ? null : Number(count), topics:editorTopics.join(', '), notes:value('notes')};
}

function showEditor(id) {
  const row = repository.get(id); editingId = id;
  const form = $('#edit-form'); form.reset(); clearEditorErrors();
  for (const key of ['course_code','title','year','semester','period','question_count','notes']) form.elements.namedItem(key).value = row[key] ?? '';
  const formatsSelect = $('#edit-formats');
  formatsSelect.querySelectorAll('[data-preserved-formats]').forEach(option => option.remove());
  if (row.formats.length > 1) {
    const option = document.createElement('option');
    option.value = row.formats.join('|'); option.textContent = row.formats.join(' / ');
    option.dataset.preservedFormats = 'true'; formatsSelect.append(option);
  }
  formatsSelect.value = row.formats.join('|');
  editorTopics = normalizeEditorTopics(String(row.topics ?? '').split(/[,\n]+/));
  $('#edit-tag-input').value = ''; renderEditorTopics();
  $('#edit-instructor').value = row.instructor || 'ยังไม่มีข้อมูลผู้สอน';
  $('#editor').showModal();
  $('#editor .edit-body').scrollTop = 0;
  $('#edit-course').focus();
}

$('#edit-tag-input').addEventListener('keydown', event => {
  if (event.isComposing) return;
  if (event.key === 'Enter' || event.key === ',') { event.preventDefault(); commitEditorTopic(); }
});
$('#edit-tag-input').addEventListener('blur', commitEditorTopic);
$('#edit-tag-list').addEventListener('click', event => {
  const button = event.target.closest('[data-remove-topic]'); if (!button) return;
  editorTopics.splice(Number(button.dataset.removeTopic), 1); renderEditorTopics(); $('#edit-tag-input').focus();
});
$('#edit-course').addEventListener('change', () => safely(() => {
  const row = repository.get(editingId);
  // No teacher catalog/API exists in this preview. Never keep a teacher from a different course.
  $('#edit-instructor').value = $('#edit-course').value === row.course_code ? row.instructor || 'ยังไม่มีข้อมูลผู้สอน' : 'ยังไม่มีข้อมูลผู้สอน';
}));

for (const key of Object.keys(editFieldIds).filter(key => key !== 'topics')) {
  const control = document.getElementById(editFieldIds[key]);
  control.addEventListener('blur', () => {
    const errors = validateEditValues(readEditorValues(), COURSE_CATALOG);
    showEditorFieldError(key, errors[key]);
  });
  control.addEventListener('input', () => {
    if (control.getAttribute('aria-invalid') === 'true') {
      showEditorFieldError(key, validateEditValues(readEditorValues(), COURSE_CATALOG)[key]);
    }
  });
}

$('#edit-form').addEventListener('submit', event => {
  event.preventDefault(); commitEditorTopic(); clearEditorErrors();
  const changes = readEditorValues();
  const errors = validateEditValues(changes, COURSE_CATALOG);
  if ($('#edit-count').validity.badInput) errors.question_count = 'กรุณากรอกจำนวนข้อเป็นตัวเลข';
  const entries = Object.entries(errors);
  if (entries.length) {
    entries.forEach(([key, message]) => showEditorFieldError(key, message));
    $('#edit-error').innerHTML = '<strong>กรุณาตรวจสอบข้อมูลก่อนบันทึก</strong>' + entries.map(([key, message]) => `<a href="#${key === 'topics' ? 'edit-tag-input' : editFieldIds[key]}">${escapeHtml(message)}</a>`).join('');
    $('#edit-error').hidden = false; $('#edit-error').focus(); return;
  }
  try {
    const row = repository.get(editingId);
    if (changes.course_code !== row.course_code) changes.instructor = 'ยังไม่มีข้อมูลผู้สอน';
    repository.update(editingId, changes);
    $('#editor').close(); refreshOptions(); render(); notify('บันทึกการแก้ไขข้อมูลตัวอย่างในเบราว์เซอร์แล้ว');
  } catch (error) {
    $('#edit-error').textContent = error.message || 'บันทึกไม่สำเร็จ ข้อมูลเดิมยังไม่เปลี่ยนแปลง';
    $('#edit-error').hidden = false; $('#edit-error').focus();
  }
});

$('#edit-error').addEventListener('click', event => {
  const link = event.target.closest('a[href^="#"]'); if (!link) return;
  const control = document.getElementById(link.getAttribute('href').slice(1));
  if (control) { event.preventDefault(); control.focus(); }
});

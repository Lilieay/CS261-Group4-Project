'use strict';
// Preview editor. Load after shared-courses.js.
const editFieldIds = {
  course_code: 'edit-course', title: 'edit-title', year: 'edit-year',
  semester: 'edit-semester', period: 'edit-period', formats: 'edit-formats',
  essay_count: 'edit-essay-count', objective_count: 'edit-objective-count', topics: 'edit-topics'
};
const TITLE_ERROR = 'กรุณากรอกชื่อแนวข้อสอบ ห้ามเว้นว่างหรือใส่เฉพาะช่องว่าง';
let legacyEditorTotal = null;

function getEditorCounts(row) {
  const hasSplit = Object.hasOwn(row, 'essay_count') || Object.hasOwn(row, 'objective_count');
  if (hasSplit) return { essay: row.essay_count ?? null, objective: row.objective_count ?? null, legacy: null };
  if (row.formats.length === 1 && row.formats[0] === 'อัตนัย') return { essay: row.question_count ?? null, objective: null, legacy: null };
  if (row.formats.length === 1 && row.formats[0] === 'ปรนัย') return { essay: null, objective: row.question_count ?? null, legacy: null };
  return { essay: null, objective: null, legacy: row.question_count ?? null };
}

function calculateEditorTotal(essay, objective, legacy = null) {
  return essay === null && objective === null ? legacy : (essay ?? 0) + (objective ?? 0);
}

function validateEditValues(values, courses) {
  const errors = {};
  if (!courses.some(course => course.code === values.course_code)) errors.course_code = 'กรุณาเลือกรายวิชาที่มีอยู่ในระบบ';
  if (!values.title.trim()) errors.title = TITLE_ERROR;
  else if (values.title.length > 255) errors.title = 'ชื่อแนวข้อสอบต้องไม่เกิน 255 ตัวอักษร';
  if (!['2566', '2567', '2568', '2569'].includes(values.year)) errors.year = 'กรุณาเลือกปีการศึกษา';
  if (!['1', '2', 'ฤดูร้อน'].includes(values.semester)) errors.semester = 'กรุณาเลือกภาคเรียน';
  if (!['กลางภาค', 'ปลายภาค'].includes(values.period)) errors.period = 'กรุณาเลือกช่วงการสอบ';
  if (!values.formats.length || values.formats.some(value => !['ปรนัย', 'อัตนัย', 'ผสม', 'อื่น ๆ'].includes(value))) errors.formats = 'กรุณาเลือกรูปแบบข้อสอบ';
  if (!values.topics.trim()) errors.topics = 'กรุณากรอกหัวข้อเนื้อหาที่ครอบคลุม';
  for (const key of ['essay_count', 'objective_count']) {
    const count = values[key];
    if (count !== null && (!Number.isSafeInteger(count) || count < 0)) errors[key] = 'กรุณาระบุจำนวนเต็มตั้งแต่ 0 ขึ้นไป หรือเว้นว่าง';
  }
  if (!errors.essay_count && !errors.objective_count && values.question_count !== null && (!Number.isSafeInteger(values.question_count) || values.question_count <= 0)) {
    const target = values.formats.length === 1 && values.formats[0] === 'ปรนัย'
      ? 'objective_count' : 'essay_count';
    errors[target] = 'จำนวนข้อสอบรวมต้องมากกว่า 0 หรือเว้นว่างทั้งสองช่อง';
  }
  return errors;
}

function showEditorFieldError(key, message = '') {
  const control = document.getElementById(editFieldIds[key]);
  const error = document.getElementById(editFieldIds[key] + '-error');
  control.setAttribute('aria-invalid', String(Boolean(message)));
  error.textContent = message;
  error.hidden = !message;
}

function clearEditorErrors() {
  Object.keys(editFieldIds).forEach(key => showEditorFieldError(key));
  $('#edit-error').hidden = true;
  $('#edit-error').textContent = '';
}

function readEditorValues() {
  const form = $('#edit-form');
  const value = key => String(form.elements.namedItem(key).value ?? '').trim();
  const count = key => {
    const input = form.elements.namedItem(key);
    const text = String(input.value ?? '').trim();
    return input.disabled || text === '' ? null : Number(text);
  };
  const essay = count('essay_count');
  const objective = count('objective_count');
  return {
    course_code: value('course_code'), title: value('title'), year: value('year'),
    semester: value('semester'), period: value('period'),
    formats: value('formats').split('|').filter(Boolean),
    essay_count: essay, objective_count: objective,
    question_count: calculateEditorTotal(essay, objective, legacyEditorTotal),
    topics: value('topics'), notes: value('notes')
  };
}

function showEditor(id) {
  const row = repository.get(id);
  editingId = id;
  const form = $('#edit-form');
  form.reset();
  clearEditorErrors();
  for (const key of ['course_code', 'title', 'year', 'semester', 'period', 'topics', 'notes']) {
    form.elements.namedItem(key).value = row[key] ?? '';
  }
  const formats = $('#edit-formats');
  formats.querySelectorAll('[data-preserved-formats]').forEach(option => option.remove());
  if (row.formats.length > 1) {
    const option = document.createElement('option');
    option.value = row.formats.join('|');
    option.textContent = row.formats.join(' / ');
    option.dataset.preservedFormats = 'true';
    formats.append(option);
  }
  formats.value = row.formats.join('|');
  const counts = getEditorCounts(row);
  $('#edit-essay-count').value = counts.essay ?? '';
  $('#edit-objective-count').value = counts.objective ?? '';
  legacyEditorTotal = counts.legacy;
  $('#edit-count-hint').textContent = counts.legacy === null ? '' : `ข้อมูลเดิมระบุรวม ${counts.legacy} ข้อ โดยยังไม่แยกประเภท หากเว้นว่างทั้งสองช่องจะเก็บจำนวนเดิมไว้`;
  $('#edit-count-hint').hidden = counts.legacy === null;
  syncExamCountFields();
  $('#editor').showModal();
  $('#editor .edit-body').scrollTop = 0;
  $('#edit-course').focus();
}

for (const key of Object.keys(editFieldIds)) {
  const control = document.getElementById(editFieldIds[key]);
  const validateField = () => {
    const errors = validateEditValues(readEditorValues(), COURSE_CATALOG);
    if (!control.disabled && control.validity.badInput) errors[key] = 'กรุณากรอกจำนวนข้อเป็นตัวเลข';
    showEditorFieldError(key, errors[key]);
    if (key === 'essay_count' || key === 'objective_count') {
      const other = key === 'essay_count' ? 'objective_count' : 'essay_count';
      if (!document.getElementById(editFieldIds[other]).validity.badInput) showEditorFieldError(other, errors[other]);
    }
  };
  control.addEventListener('blur', validateField);
  control.addEventListener('input', () => {
    if (control.getAttribute('aria-invalid') === 'true' || key.endsWith('_count')) validateField();
  });
}

$('#edit-form').addEventListener('submit', event => {
  event.preventDefault();
  syncExamCountFields();
  clearEditorErrors();
  const changes = readEditorValues();
  const errors = validateEditValues(changes, COURSE_CATALOG);
  for (const key of ['essay_count', 'objective_count']) {
    if (!document.getElementById(editFieldIds[key]).disabled && document.getElementById(editFieldIds[key]).validity.badInput) errors[key] = 'กรุณากรอกจำนวนข้อเป็นตัวเลข';
  }
  const entries = Object.entries(errors);
  if (entries.length) {
    entries.forEach(([key, message]) => showEditorFieldError(key, message));
    const summary = $('#edit-error');
    // Match the reference: one field error stays directly below its field.
    // For multiple invalid fields, also provide a focusable summary.
    if (entries.length > 1) {
      summary.innerHTML = '<strong>กรุณาตรวจสอบข้อมูลก่อนบันทึก</strong>' + entries.map(([key, message]) => `<a href="#${editFieldIds[key]}">${escapeHtml(message)}</a>`).join('');
      summary.hidden = false;
      summary.focus();
    } else {
      document.getElementById(editFieldIds[entries[0][0]]).focus();
    }
    return;
  }
  try {
    const row = repository.get(editingId);
    if (changes.course_code !== row.course_code) changes.instructor = 'ยังไม่มีข้อมูลผู้สอน';
    // A legacy mixed exam may only have a total: do not claim it has split counts.
    if (changes.essay_count === null && changes.objective_count === null && legacyEditorTotal !== null) {
      delete changes.essay_count;
      delete changes.objective_count;
    }
    repository.update(editingId, changes);
    $('#editor').close();
    refreshOptions();
    render();
    notify('บันทึกการแก้ไขข้อมูลตัวอย่างในเบราว์เซอร์แล้ว');
  } catch (error) {
    $('#edit-error').textContent = error.message || 'บันทึกไม่สำเร็จ ข้อมูลเดิมยังไม่เปลี่ยนแปลง';
    $('#edit-error').hidden = false;
    $('#edit-error').focus();
  }
});

$('#edit-error').addEventListener('click', event => {
  const link = event.target.closest('a[href^="#"]');
  if (!link) return;
  const control = document.getElementById(link.getAttribute('href').slice(1));
  if (control) { event.preventDefault(); control.focus(); }
});


function syncExamCountFields() {
  const formats = $('#edit-formats').value.split('|').filter(Boolean);
  const onlyEssay = formats.length === 1 && formats[0] === 'อัตนัย';
  const onlyObjective = formats.length === 1 && formats[0] === 'ปรนัย';
  const controls = [
    ['edit-essay-count', onlyObjective, 'essay_count'],
    ['edit-objective-count', onlyEssay, 'objective_count']
  ];
  for (const [id, disabled, key] of controls) {
    const input = document.getElementById(id);
    input.disabled = disabled;
    input.placeholder = disabled ? 'ไม่ใช้กับรูปแบบนี้' : 'จำนวนข้อ';
    if (disabled) {
      input.value = '';
      showEditorFieldError(key);
    }
  }
}

$('#edit-formats').addEventListener('change', () => {
  legacyEditorTotal = null;
  $('#edit-count-hint').hidden = true;
  syncExamCountFields();
});

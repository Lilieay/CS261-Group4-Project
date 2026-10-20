(() => {
  'use strict';
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g,
    character => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[character]));
  const semesterLabel = value => ['3', 'ฤดูร้อน', 'ซัมเมอร์'].includes(String(value)) ? 'ซัมเมอร์' : `ที่ ${value}`;

  function publisherName(row) {
    const publisher = row.publisher || {};
    return publisher.displayname_th || publisher.displayname_en || row.publisher_name || 'ไม่ระบุชื่อ';
  }

  function questionCounts(row) {
    const valid = value => Number.isSafeInteger(value) && value >= 0 ? value : null;
    if (['essay_count', 'subjective_count', 'objective_count'].some(key => Object.hasOwn(row, key))) {
      return {essay: valid(Object.hasOwn(row, 'essay_count') ? row.essay_count : row.subjective_count), objective: valid(row.objective_count)};
    }
    const single = row.formats.length === 1 ? row.formats[0] : '';
    return {essay: single === 'อัตนัย' ? valid(row.question_count) : null, objective: single === 'ปรนัย' ? valid(row.question_count) : null};
  }

  window.UiUtils = Object.freeze({escapeHtml, semesterLabel, publisherName, questionCounts});
})();

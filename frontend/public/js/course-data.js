(() => {
  'use strict';
  const COURSE_CATALOG = [{"code": "CS100", "name": "BASIC WEB DEVELOPMENT"}, {"code": "CS101", "name": "DISCRETE STRUCTURES"}, {"code": "CS102", "name": "PROBLEM SOLVING BASICS AND COMPUTER PROGRAMMING"}, {"code": "CS103", "name": "INTRODUCTION TO COMPUTER PROGRAMMING"}, {"code": "CS104", "name": "INTRODUCTION TO COMPUTER PROGRAMMING USING PYTHON"}, {"code": "CS213", "name": "DATA STRUCTURES"}, {"code": "CS221", "name": "INTRODUCTION TO COMPUTER SYSTEM AND ORGANIZATION"}, {"code": "CS223", "name": "VIRTUALIZATION TECHNOLOGY"}, {"code": "CS224", "name": "LINUX ADMINISTRATION AND PERFORMANCE MONITORING"}, {"code": "CS240", "name": "PRINCIPLES OF DATA SCIENCE"}, {"code": "CS241", "name": "PROGRAMMING LANGUAGES AND PARADIGMS"}, {"code": "CS261", "name": "INTRODUCTION TO SOFTWARE ENGINEERING"}, {"code": "CS263", "name": "SOFTWARE REQUIREMENT SPECIFICATION"}, {"code": "CS265", "name": "BASIC MOBILE DEVELOPMENT"}, {"code": "CS301", "name": "PREPARATION FOR SENIOR PROJECTS AND CO-OPERATIVE EDUCATION"}, {"code": "CS303", "name": "SPECIAL PROJECTS 1"}, {"code": "CS331", "name": "NET-CENTRIC COMPUTING"}, {"code": "CS341", "name": "BIG DATA ENGINEERING"}, {"code": "CS345", "name": "PRACTICAL MACHINE LEARNING"}, {"code": "CS346", "name": "BIG DATA APPLICATIONS AND ANALYTICS"}, {"code": "CS361", "name": "CLOUD-BASED SOFTWARE ARCHITECTING"}, {"code": "CS364", "name": "MOBILE APPLICATION DEVELOPMENT"}, {"code": "CS373", "name": "ADVANCED SEARCH STRATEGIES"}, {"code": "CS374", "name": "NATURAL LANGUAGE PROCESSING"}, {"code": "CS384", "name": "HUMAN - COMPUTER INTERACTION"}, {"code": "CS403", "name": "SPECIAL PROJECTS 2"}, {"code": "CS404", "name": "CO-OPERATIVE EDUCATION 2"}, {"code": "CS440", "name": "SELECTED TOPICS IN DATA SCIENCE"}];
  const {escapeHtml, semesterLabel, publisherName, questionCounts} = window.UiUtils;
  const CURRENT_USER = 'demo-owner';
  const STORAGE_KEY = 'cs261-u5-preview-v1';
  const courseName = code => COURSE_CATALOG.find(course => course.code === code)?.name ?? code;
  const seed = () => [2567, 2568].map((year, index) => ({
  id: `demo-exam-${index + 1}`, owner_id: CURRENT_USER, course_code: 'CS261',
  title: `แนวข้อสอบกลางภาค CS261 ${courseName('CS261')} ปีการศึกษา ${year}`,
  year: String(year), semester: '1', period: 'กลางภาค',
  topics: 'Software Process, Requirements Engineering, Use Case, UML และการออกแบบซอฟต์แวร์',
  notes: 'ตัวอย่างสำหรับทดลอง UI: ทบทวนแนวคิดจากบทเรียนและฝึกวิเคราะห์กรณีศึกษา ข้อมูลนี้ไม่ใช่แนวข้อสอบที่ผู้ใช้เผยแพร่จริง',
  formats: ['อัตนัย'], question_count: 6, instructor: 'ยังไม่มีข้อมูลผู้สอน',
  rating: null, reviews: 0, views: 0, downloads: 0, updated_at: '2024-09-18T12:00:00Z'
}));
  const findCourse = code => COURSE_CATALOG.find(course => course.code === String(code || '').trim().toUpperCase()) || null;

  function normalizeExam(row) {
    if (!row || typeof row.id !== 'string' || !row.id || !findCourse(row.course_code)
        || typeof row.title !== 'string' || typeof row.topics !== 'string'
        || !Array.isArray(row.formats) || row.formats.some(format => typeof format !== 'string')) {
      throw new Error('รูปแบบข้อมูลแนวข้อสอบไม่ถูกต้อง ข้อมูลเดิมยังไม่ถูกเขียนทับ');
    }
    if (row.saved_by != null && (!Array.isArray(row.saved_by) || row.saved_by.some(id => typeof id !== 'string'))) {
      throw new Error('ข้อมูลรายการที่บันทึกไม่ถูกต้อง');
    }
    const semester = String(row.semester ?? '');
    return {...row, year: String(row.year ?? row.academic_year ?? ''),
      semester: ['ฤดูร้อน', 'ซัมเมอร์'].includes(semester) ? '3' : semester,
      period: row.period === 'midterm' ? 'กลางภาค' : row.period === 'final' ? 'ปลายภาค' : String(row.period ?? ''),
      saved: (row.saved_by || []).includes(CURRENT_USER)};
  }

  function rawRows() {
    let rows;
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      rows = raw === null ? seed() : JSON.parse(raw);
    } catch (_) { throw new Error('อ่านข้อมูลในเบราว์เซอร์ไม่ได้ ข้อมูลเดิมยังไม่ถูกเขียนทับ'); }
    if (!Array.isArray(rows)) throw new Error('ข้อมูลแนวข้อสอบไม่ถูกต้อง');
    const ids = new Set();
    for (const row of rows) {
      normalizeExam(row);
      if (ids.has(row.id)) throw new Error('พบรหัสแนวข้อสอบซ้ำกัน');
      ids.add(row.id);
    }
    return rows;
  }

  function commit(rows, kind, id) {
    rows.forEach(normalizeExam);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(rows)); }
    catch (_) { throw new Error('บันทึกไม่ได้ กรุณาตรวจพื้นที่เก็บข้อมูลของเบราว์เซอร์ ข้อมูลเดิมยังอยู่'); }
    if (typeof window.dispatchEvent === 'function' && typeof window.CustomEvent === 'function') {
      window.dispatchEvent(new window.CustomEvent('course-data:change', {detail: {kind, id}}));
    }
  }

  function loadExams() { return rawRows().map(normalizeExam); }
  function getExam(id) {
    const row = loadExams().find(row => row.id === String(id));
    if (!row) throw new Error('ไม่พบแนวข้อสอบหรือรายการถูกลบแล้ว');
    return row;
  }
  function listMine() {
    return loadExams().filter(row => row.owner_id === CURRENT_USER)
      .map(row => ({...row, semester: row.semester === '3' ? 'ฤดูร้อน' : row.semester}));
  }
  function createExam(row) {
    const rows = rawRows();
    if (rows.some(item => item.id === row.id)) throw new Error('รายการนี้ถูกบันทึกแล้ว');
    const record = {...row, owner_id: CURRENT_USER, saved_by: []};
    normalizeExam(record);
    rows.push(record); commit(rows, 'publish', record.id);
    return normalizeExam(record);
  }
  function updateExam(id, changes) {
    const rows = rawRows();
    const index = rows.findIndex(row => row.id === id && row.owner_id === CURRENT_USER);
    if (index < 0) throw new Error('ไม่พบรายการของคุณหรือรายการถูกลบแล้ว');
    const allowed = ['course_code', 'title', 'year', 'semester', 'period', 'formats', 'essay_count',
      'objective_count', 'question_count', 'topics', 'notes'];
    const patch = Object.fromEntries(Object.entries(changes).filter(([key]) => allowed.includes(key)));
    rows[index] = {...rows[index], ...patch, updated_at: new Date().toISOString()};
    commit(rows, 'update', id);
  }
  function removeExam(id) {
    const rows = rawRows();
    if (!rows.some(row => row.id === id && row.owner_id === CURRENT_USER)) throw new Error('ไม่พบรายการของคุณหรือรายการถูกลบแล้ว');
    commit(rows.filter(row => row.id !== id), 'delete', id);
  }
  function toggleSaved(id) {
    const rows = rawRows();
    const row = rows.find(row => row.id === id);
    if (!row) throw new Error('ไม่พบแนวข้อสอบหรือรายการถูกลบแล้ว');
    const users = new Set(row.saved_by || []);
    const saved = !users.has(CURRENT_USER);
    if (saved) users.add(CURRENT_USER); else users.delete(CURRENT_USER);
    row.saved_by = [...users];
    commit(rows, 'bookmark', id);
    return saved;
  }
  function listSaved() { return loadExams().filter(row => row.saved); }
  function resetDemo() { commit(seed(), 'reset'); }
  function subscribe(callback) {
    const storage = event => { if (event.key === STORAGE_KEY || event.key === null) callback(); };
    window.addEventListener('storage', storage);
    window.addEventListener('focus', callback);
    window.addEventListener('course-data:change', callback);
    return () => {
      window.removeEventListener('storage', storage);
      window.removeEventListener('focus', callback);
      window.removeEventListener('course-data:change', callback);
    };
  }
  window.CourseData = Object.freeze({catalog: COURSE_CATALOG, currentUser: CURRENT_USER, storageKey: STORAGE_KEY,
    loadExams, getExam, listMine, createExam, updateExam, removeExam, toggleSaved, listSaved, resetDemo, subscribe, findCourse, escapeHtml, semesterLabel, publisherName, questionCounts});
})();

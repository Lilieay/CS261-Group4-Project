(() => {
  'use strict';
  // Shared read-only preview adapter. Replace here when the team connects its API.
const COURSE_CATALOG = [{"code": "CS100", "name": "BASIC WEB DEVELOPMENT"}, {"code": "CS101", "name": "DISCRETE STRUCTURES"}, {"code": "CS102", "name": "PROBLEM SOLVING BASICS AND COMPUTER PROGRAMMING"}, {"code": "CS103", "name": "INTRODUCTION TO COMPUTER PROGRAMMING"}, {"code": "CS104", "name": "INTRODUCTION TO COMPUTER PROGRAMMING USING PYTHON"}, {"code": "CS213", "name": "DATA STRUCTURES"}, {"code": "CS221", "name": "INTRODUCTION TO COMPUTER SYSTEM AND ORGANIZATION"}, {"code": "CS223", "name": "VIRTUALIZATION TECHNOLOGY"}, {"code": "CS224", "name": "LINUX ADMINISTRATION AND PERFORMANCE MONITORING"}, {"code": "CS240", "name": "PRINCIPLES OF DATA SCIENCE"}, {"code": "CS241", "name": "PROGRAMMING LANGUAGES AND PARADIGMS"}, {"code": "CS261", "name": "INTRODUCTION TO SOFTWARE ENGINEERING"}, {"code": "CS263", "name": "SOFTWARE REQUIREMENT SPECIFICATION"}, {"code": "CS265", "name": "BASIC MOBILE DEVELOPMENT"}, {"code": "CS301", "name": "PREPARATION FOR SENIOR PROJECTS AND CO-OPERATIVE EDUCATION"}, {"code": "CS303", "name": "SPECIAL PROJECTS 1"}, {"code": "CS331", "name": "NET-CENTRIC COMPUTING"}, {"code": "CS341", "name": "BIG DATA ENGINEERING"}, {"code": "CS345", "name": "PRACTICAL MACHINE LEARNING"}, {"code": "CS346", "name": "BIG DATA APPLICATIONS AND ANALYTICS"}, {"code": "CS361", "name": "CLOUD-BASED SOFTWARE ARCHITECTING"}, {"code": "CS364", "name": "MOBILE APPLICATION DEVELOPMENT"}, {"code": "CS373", "name": "ADVANCED SEARCH STRATEGIES"}, {"code": "CS374", "name": "NATURAL LANGUAGE PROCESSING"}, {"code": "CS384", "name": "HUMAN - COMPUTER INTERACTION"}, {"code": "CS403", "name": "SPECIAL PROJECTS 2"}, {"code": "CS404", "name": "CO-OPERATIVE EDUCATION 2"}, {"code": "CS440", "name": "SELECTED TOPICS IN DATA SCIENCE"}];
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
  rating: '4.9', reviews: 18, views: 340, downloads: 128, updated_at: '2024-09-18T12:00:00Z'
}));
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));
  const findCourse = code => COURSE_CATALOG.find(course => course.code === String(code || '').trim().toUpperCase()) || null;
  const semesterLabel = value => String(value) === '3' || value === 'ฤดูร้อน' || value === 'ซัมเมอร์' ? 'ซัมเมอร์' : `ที่ ${value}`;
  function normalizeExam(row) {
    if (!row || row.id == null || typeof row.course_code !== 'string' || typeof row.title !== 'string' || typeof row.topics !== 'string' || !Array.isArray(row.formats)) throw new Error('รูปแบบข้อมูลแนวข้อสอบไม่ถูกต้อง');
    const semester = String(row.semester ?? '');
    return {...row, id:String(row.id), year:String(row.year ?? row.academic_year ?? ''), semester:['ฤดูร้อน','ซัมเมอร์'].includes(semester) ? '3' : semester, period:row.period === 'midterm' ? 'กลางภาค' : row.period === 'final' ? 'ปลายภาค' : String(row.period ?? '')};
  }
  function loadExams() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const rows = raw === null ? seed() : JSON.parse(raw);
      if (!Array.isArray(rows)) throw new Error('invalid');
      return rows.map(normalizeExam);
    } catch (_) { throw new Error('ไม่สามารถอ่านข้อมูลแนวข้อสอบในเบราว์เซอร์ได้ กรุณาตรวจข้อมูลตัวอย่างในหน้ารายวิชาที่แบ่งปัน'); }
  }
  function publisherName(row) {
    const publisher = row.publisher || {};
    return publisher.displayname_th || publisher.displayname_en || row.publisher_name || 'ไม่ระบุชื่อ';
  }
  function questionCounts(row) {
    const valid = value => Number.isSafeInteger(value) && value >= 0 ? value : null;
    if (['essay_count','subjective_count','objective_count'].some(key => Object.hasOwn(row, key))) {
      return {essay:valid(Object.hasOwn(row,'essay_count') ? row.essay_count : row.subjective_count), objective:valid(row.objective_count)};
    }
    const single = row.formats.length === 1 ? row.formats[0] : '';
    return {essay:single === 'อัตนัย' ? valid(row.question_count) : null, objective:single === 'ปรนัย' ? valid(row.question_count) : null};
  }
  window.CourseData = Object.freeze({catalog:COURSE_CATALOG, storageKey:STORAGE_KEY, loadExams, findCourse, escapeHtml, semesterLabel, publisherName, questionCounts});
})();

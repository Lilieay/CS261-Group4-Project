(() => {
  'use strict';
  const COURSE_CATALOG = window.CourseData.catalog;
  const FEATURED_CODES = ['CS101', 'CS102', 'CS221', 'CS213', 'CS261', 'CS331'];
  const DESCRIPTIONS = {
    CS100: 'พื้นฐานการพัฒนาเว็บไซต์ โครงสร้าง HTML การจัดรูปแบบด้วย CSS และ JavaScript',
    CS101: 'โครงสร้างไม่ต่อเนื่อง ตรรกศาสตร์ เซต ความสัมพันธ์ และพื้นฐานคณิตศาสตร์สำหรับคอมพิวเตอร์',
    CS102: 'พื้นฐานการแก้ปัญหา การออกแบบขั้นตอนวิธี และการเขียนโปรแกรมคอมพิวเตอร์',
    CS103: 'แนวคิดการเขียนโปรแกรม ตัวแปร เงื่อนไข การทำซ้ำ และการออกแบบฟังก์ชัน',
    CS104: 'พื้นฐานการเขียนโปรแกรมด้วย Python โครงสร้างข้อมูล และการแก้ปัญหา',
    CS213: 'โครงสร้างข้อมูล ลิสต์ สแตก คิว ต้นไม้ กราฟ และขั้นตอนวิธีสำหรับจัดการข้อมูล',
    CS221: 'ระบบคอมพิวเตอร์และองค์ประกอบ สถาปัตยกรรม ชุดคำสั่ง และการประมวลผล',
    CS240: 'หลักการวิทยาการข้อมูล การเตรียมข้อมูล การวิเคราะห์ และการนำเสนอผล',
    CS261: 'กระบวนการพัฒนาซอฟต์แวร์ การวิเคราะห์ความต้องการ การออกแบบ และการทำงานเป็นทีม',
    CS263: 'การเก็บรวบรวม วิเคราะห์ และจัดทำข้อกำหนดความต้องการซอฟต์แวร์',
    CS331: 'การประมวลผลผ่านเครือข่าย แนวคิดระบบเครือข่ายและการพัฒนาแอปพลิเคชัน'
  };
  const $ = selector => document.querySelector(selector);
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));
  let showAll = false;
  let sharedRows = [];
  let storageError = '';

  function findCourses(courses, keyword) {
    const term = keyword.trim().toLocaleLowerCase();
    if (term.length > 255) return [];
    return courses.filter(course => !term || course.code.toLocaleLowerCase().startsWith(term) || course.name.toLocaleLowerCase().includes(term));
  }

  function readSharedExams() { return window.CourseData.loadExams(); }

  function refreshSharedRows() {
    try { sharedRows = readSharedExams(); storageError = ''; }
    catch (error) { sharedRows = []; storageError = error.message || 'ไม่สามารถอ่านข้อมูลตัวอย่างในเบราว์เซอร์ได้'; }
  }

  function courseExams(code) { return sharedRows.filter(row => row.course_code === code); }
  function courseDescription(course) { return DESCRIPTIONS[course.code] || `สรุปบทเรียนและแนวข้อสอบรายวิชา ${course.name}`; }
  function courseStats(code) {
    const rows = courseExams(code);
    const semesters = [...new Set(rows.map(row => String(row.semester ?? '')).filter(Boolean))];
    return { exams: rows.length, semester: semesters.length === 1 ? `Semester ${semesters[0]}` : 'หลักสูตร 2566' };
  }

  function displayCourseName(name) {
    return name.toLocaleLowerCase().replace(/\b[a-z]/g, letter => letter.toLocaleUpperCase())
      .replace(/\b(sql|cs|uml|html|css|er)\b/gi, word => word.toLocaleUpperCase());
  }

  function courseCard(course) {
    const stats = courseStats(course.code);
    return `<article class="course-card"><div class="card-top"><span class="course-code-badge">${escapeHtml(course.code)}</span><span class="semester-text">${escapeHtml(stats.semester)}</span></div><h2 class="course-name">${escapeHtml(displayCourseName(course.name))}</h2><p class="course-desc">${escapeHtml(courseDescription(course))}</p><div class="card-footer"><span class="course-stats">0 สรุป · ${storageError ? '—' : stats.exams} แนวข้อสอบ</span><a class="btn-open-course" data-open-course="${escapeHtml(course.code)}" href="choose-courses.html?course=${encodeURIComponent(course.code)}" aria-label="เปิดคลัง ${escapeHtml(course.code)}">เปิดคลัง <span aria-hidden="true">→</span></a></div></article>`;
  }

  function renderCourses(announce = false) {
    const keyword = $('#course-search').value;
    const term = keyword.trim();
    const matches = findCourses(COURSE_CATALOG, keyword);
    const featured = FEATURED_CODES.map(code => COURSE_CATALOG.find(course => course.code === code)).filter(Boolean);
    const visible = !showAll && !term ? featured : matches;
    $('#course-grid').innerHTML = visible.length ? visible.map(courseCard).join('') : '<div class="course-empty"><h2>ไม่พบวิชาในระบบ</h2><p>ลองค้นหาด้วยรหัสวิชาหรือชื่อวิชาอื่น</p><button type="button" id="clear-search">แสดงรายวิชาทั้งหมด</button></div>';
    $('#view-all').hidden = Boolean(term) || showAll;
    $('#view-all').innerHTML = `ดูรายวิชาทั้งหมดในหลักสูตร (${COURSE_CATALOG.length} วิชา) <span aria-hidden="true">→</span>`;
    const status = $('#course-status');
    status.classList.toggle('error', Boolean(storageError));
    status.textContent = storageError || (announce ? `พบ ${visible.length} รายวิชา` : '');
  }

  function start() {
    refreshSharedRows(); renderCourses();
    $('#course-search-form').addEventListener('submit', event => { event.preventDefault(); showAll = true; renderCourses(true); });
    $('#course-search').addEventListener('input', () => { showAll = true; renderCourses(true); });
    $('#view-all').addEventListener('click', () => { showAll = true; renderCourses(true); });
    $('#course-grid').addEventListener('click', event => {
      if (event.target.closest('#clear-search')) { $('#course-search').value = ''; showAll = true; renderCourses(true); $('#course-search').focus(); }
    });
    window.addEventListener('storage', event => { if (event.key === window.CourseData.storageKey || event.key === null) { refreshSharedRows(); renderCourses(); } });
    window.addEventListener('focus', () => { refreshSharedRows(); renderCourses(); });
  }
  start();
})();

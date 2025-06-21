const { request } = require('./request');

const BASE_URL = 'http://127.0.0.1:5000';  // 使用127.0.0.1替代localhost

const api = {
  getBaseUrl: () => BASE_URL,
  // 登录和修改密码
  login: (data) => request('/login', 'POST', data),
  changePassword: (data) => request('/changePassword', 'POST', data),
  // 学生和教师信息
  getStudentInfo: (data) => request('/student/info', 'POST', data),
  getTeacherInfo: (data) => request('/teacher/info', 'POST', data),
  // 师生课程信息
  getStudentSchedule: (data) => request('/student/schedule', 'POST', data),
  getTodayCourses: (data) => request('/student/schedule/today', 'POST', data),
  getTeacherSchedule: (data) => request('/teacher/schedule', 'POST', data),
  getTeacherTodayCourses: (data) => request('/teacher/schedule/today', 'POST', data),
  //签到扫码
  publishCheckin: (data) => request('/teacher/checkin/publish', 'POST', data),
  submitCheckin: (data) => request('/student/checkin/submit', 'POST', data),
  //考勤与统计
  getAttendanceCount: (data) => request('/attendance/count', 'POST', data),
  getAttendanceRecords: (data) => request('/attendance/records', 'POST', data),
  getCheckinDates: (data) => request('/teacher/checkin/dates', 'POST', data),
  getCheckinRecords: (data) => request('/teacher/checkin/records', 'POST', data),
  getCheckinCount: (data) => request('/teacher/checkin/count', 'POST', data),
  getAbsentStudents: (data) => request('/teacher/checkin/absent_students', 'POST', data),
  registerLeave: (data) => request('/teacher/checkin/register_leave', 'POST', data),
  getCheckinStatistics: (data) => request('/teacher/checkin/statistics', 'POST', data),
  // 修改信息
  getAdminInfo: (data) => request('/admin/get_info', 'POST', data),
  updateStudent: (data) => request('/admin/update_student', 'POST', data),
  updateTeacher: (data) => request('/admin/update_teacher', 'POST', data),
  updateCourse: (data) => request('/admin/update_course', 'POST', data),
  // 删除信息
  deleteStudent: (data) => request('/admin/delete_student', 'POST', data),
  deleteTeacher: (data) => request('/admin/delete_teacher', 'POST', data),
  deleteCourse: (data) => request('/admin/delete_course', 'POST', data),
  deleteAttendance: (data) => request('/admin/delete_attendance', 'POST', data),
  //批量删除数据
  deleteStudentsByGrade: (data) => request('/admin/delete_students_by_grade', 'POST', data),
  deleteAllTeachers: () => request('/admin/delete_all_teachers', 'POST', {}),
  deleteAllCourses: () => request('/admin/delete_all_courses', 'POST', {}),
  deleteAllStudentCourses: () => request('/admin/delete_all_student_courses', 'POST', {}),
  deleteAllAttendanceRecords: () => request('/admin/delete_all_attendance_records', 'POST', {}),

};

module.exports = api;
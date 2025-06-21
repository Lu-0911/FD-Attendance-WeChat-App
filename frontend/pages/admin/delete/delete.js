const api = require('../../../utils/api.js');

Page({
  data: {
    grade: '',
    teacherConfirmText: '',
    courseConfirmText: '',
    studentCourseConfirmText: '',
    attendanceConfirmText: ''
  },

  onGradeInput: function (e) {
    this.setData({
      grade: e.detail.value
    });
  },

  onTeacherConfirmInput: function (e) {
    this.setData({
      teacherConfirmText: e.detail.value
    });
  },

  onCourseConfirmInput: function (e) {
    this.setData({
      courseConfirmText: e.detail.value
    });
  },

  onStudentCourseConfirmInput: function (e) {
    this.setData({
      studentCourseConfirmText: e.detail.value
    });
  },

  onAttendanceConfirmInput: function (e) {
    this.setData({
      attendanceConfirmText: e.detail.value
    });
  },

  deleteStudentsByGrade: async function () {
    const grade = this.data.grade;
    if (!grade) {
      wx.showToast({
        title: '请输入年级',
        icon: 'none'
      });
      return;
    }
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除${grade}年级的所有学生吗？此操作不可恢复！`,
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '删除中...' });
          const result = await api.deleteStudentsByGrade({ grade: grade });
          wx.hideLoading();
          
          if (result.status) {
            wx.showToast({
              title: '删除成功',
              icon: 'success'
            });
            this.setData({ grade: '' });
          } else {
            wx.showToast({
              title: result.message || '删除失败',
              icon: 'none'
            });
          }
        }
      }
    });
  },

  deleteAllTeachers: async function () {
    if (this.data.teacherConfirmText !== '确认删除') {
      wx.showToast({
        title: '请输入"确认删除"',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '删除中...' });
    const result = await api.deleteAllTeachers();
    wx.hideLoading();
    
    if (result.status) {
      wx.showToast({
        title: '删除成功',
        icon: 'success'
      });
      this.setData({ teacherConfirmText: '' });
    } else {
      wx.showToast({
        title: result.message || '删除失败',
        icon: 'none'
      });
    }
  },

  deleteAllCourses: async function () {
    if (this.data.courseConfirmText !== '确认删除') {
      wx.showToast({
        title: '请输入"确认删除"',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '删除中...' });
    const result = await api.deleteAllCourses();
    wx.hideLoading();
    
    if (result.status) {
      wx.showToast({
        title: '删除成功',
        icon: 'success'
      });
      this.setData({ courseConfirmText: '' });
    } else {
      wx.showToast({
        title: result.message || '删除失败',
        icon: 'none'
      });
    }
  },

  deleteAllStudentCourses: async function () {
    if (this.data.studentCourseConfirmText !== '确认删除') {
      wx.showToast({
        title: '请输入"确认删除"',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '删除中...' });
    const result = await api.deleteAllStudentCourses();
    wx.hideLoading();
    
    if (result.status) {
      wx.showToast({
        title: '选课记录删除成功',
        icon: 'success'
      });
      this.setData({ studentCourseConfirmText: '' });
    } else {
      wx.showToast({
        title: result.message || '删除失败',
        icon: 'none'
      });
    }
  },

  deleteAllAttendanceRecords: async function () {
    if (this.data.attendanceConfirmText !== '确认删除') {
      wx.showToast({
        title: '请输入"确认删除"',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '删除中...' });
    const result = await api.deleteAllAttendanceRecords();
    wx.hideLoading();
    
    if (result.status) {
      wx.showToast({
        title: '考勤记录删除成功',
        icon: 'success'
      });
      this.setData({ attendanceConfirmText: '' });
    } else {
      wx.showToast({
        title: result.message || '删除失败',
        icon: 'none'
      });
    }
  }
});

const api = require('../../../utils/api.js');

Page({
  data: {
    attendanceList: [],
    showDetail: false,
    selectedCourseName: '',
    detailList: []
  },

  onLoad() {
    this.getAttendanceCount();
  },

  getAttendanceCount() {
    const student_id = getApp().globalData.account;
    api.getAttendanceCount({ student_id }).then(res => {
      if (res.status) {
        this.setData({ attendanceList: res.data });
      } else {
        wx.showToast({
          title: res.message,
          icon: 'none'
        });
      }
    }).catch(err => {
      console.error('获取考勤汇总失败', err);
      wx.showToast({
        title: '获取考勤汇总失败',
        icon: 'none'
      });
    });
  },

  onCourseTap(e) {
    const course_id = e.currentTarget.dataset.course_id;
    const student_id = getApp().globalData.account;
    const selectedCourse = this.data.attendanceList.find(course => course.course_id === course_id);
    
    if (selectedCourse) {
      this.setData({ selectedCourseName: selectedCourse.course_name });
    }

    api.getAttendanceRecords({ student_id: student_id, course_id: course_id }).then(res => {
      if (res.status) {
        this.setData({
          detailList: res.data,
          showDetail: true
        });
      } else {
        wx.showToast({
          title: res.message,
          icon: 'none'
        });
      }
    }).catch(err => {
      console.error('获取签到记录失败', err);
      wx.showToast({
        title: '获取签到记录失败',
        icon: 'none'
      });
    });
  },

  onCloseModal() {
    this.setData({
      showDetail: false,
      selectedCourseName: '',
      detailList: []
    });
  }
});
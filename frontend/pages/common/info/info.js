const api = require('../../../utils/api.js');

Page({
  data: {
    userInfo: null,
    isStudent: false,
    isTeacher: false
  },

  onLoad() {
    const app = getApp();
    const user_type = app.globalData.user_type;
    const user_id = app.globalData.account;

    if (!user_type || !user_id) {
      wx.showToast({
        title: '无法获取用户信息，请重新登录',
        icon: 'none'
      });
      return;
    }

    if (user_type === 'student') {
      this.setData({ isStudent: true, isTeacher: false });
      api.getStudentInfo({ student_id: user_id }).then(res => {
        if (res.status) {
          // 处理出生日期格式
          if (res.data.birthday) {
            const date = new Date(res.data.birthday);
            res.data.birthday = date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
          }
          this.setData({ userInfo: res.data });
        } else {
          wx.showToast({
            title: res.message,
            icon: 'none'
          });
        }
      }).catch(err => {
        console.error('获取学生信息失败', err);
        wx.showToast({
            title: '获取学生信息失败',
            icon: 'none'
        });
      });
    } else if (user_type === 'teacher') {
      this.setData({ isStudent: false, isTeacher: true });
      api.getTeacherInfo({ teacher_id: user_id }).then(res => {
        if (res.status) {
          this.setData({ userInfo: res.data });
        } else {
          wx.showToast({
            title: res.message,
            icon: 'none'
          });
        }
      }).catch(err => {
        console.error('获取教师信息失败', err);
        wx.showToast({
          title: '获取教师信息失败',
          icon: 'none'
        });
      });
    }
  }
});
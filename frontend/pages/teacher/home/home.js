const api = require('../../../utils/api.js');

Page({
    data: {
      teacher: {},
      todayCourses: []
    },
  
    onLoad() {
      this.loadTeacherInfo();
      this.loadTodayCourses();
    },
  
    loadTeacherInfo() {
      const teacher_id = getApp().globalData.account;
      api.getTeacherInfo({ teacher_id }).then(res => {
        if (res.status) {
          this.setData({ teacher: res.data });
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
    },
  
    loadTodayCourses() {
      const teacher_id = getApp().globalData.account;
      api.getTeacherTodayCourses({ teacher_id }).then(res => {
        if (res.status) {
          this.setData({ todayCourses: res.data });
        } else {
          wx.showToast({
            title: res.message,
            icon: 'none'
          });
        }
      }).catch(err => {
        console.error('获取今日课程失败', err);
        wx.showToast({
          title: '获取今日课程失败',
          icon: 'none'
        });
      });
    },
  
  goToSchedule: function () {
    wx.navigateTo({
      url: '/pages/teacher/schedule/schedule'
    })
  },

  goToPublishCheckin: function () {
    wx.navigateTo({
      url: '/pages/teacher/publishCheckin/publishCheckin'
    })
  },

  goToStatistic: function () {
    wx.navigateTo({
      url: '/pages/teacher/statistic/statistic'
    })
  },

  goToInfo: function () {
    wx.navigateTo({
      url: '/pages/common/info/info'
    })
  },

  goToSettings: function () {
    wx.navigateTo({
      url: '/pages/common/settings/settings'
    })
  }
  });
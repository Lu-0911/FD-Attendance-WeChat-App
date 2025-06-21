const api = require('../../../utils/api.js');

Page({
  data: {
    courses: [],
    courseIndex: 0,
    startTime: '08:00', // 默认开始时间
    duration: '10', // 默认时长为10分钟
    locationOptions: [{name: '否', value: false}, 
      {name: '是', value: true}],
    locationIndex: 0,  // 默认选择不需要定位
    currentLocation: null, // 当前定位信息
    locationRange: 100,
    qrCodeUrl: ''
  },

  onLoad() {
    this.loadTeacherCourses();
  },

  loadTeacherCourses() {
    const teacher_id = getApp().globalData.account;
    api.getTeacherTodayCourses({ teacher_id }).then(res => {
      if (res.status) {
        this.setData({ courses: res.data });
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

  bindCourseChange(e) {
    this.setData({
      courseIndex: e.detail.value
    });
  },

  bindStartTimeChange(e) {
    this.setData({
      startTime: e.detail.value
    });
  },

  bindDurationInput(e) {
    const value = e.detail.value;
    this.setData({
      duration: value
    });
  },

  bindLocationChange(e) {
    const index = parseInt(e.detail.value);
    const selectedOption = this.data.locationOptions[index];
    this.setData({
      locationIndex: index,
      require_location: selectedOption.value
    });
    
    // 如果选择需要定位，获取位置
    if (selectedOption.value) {
      wx.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.setData({
            currentLocation: { latitude: res.latitude, longitude: res.longitude }
          });
        }
      });
    }
  },


  publishCheckin() {
    const selectedCourse = this.data.courses[this.data.courseIndex];
    if (!selectedCourse) {
      wx.showToast({
        title: '请选择课程',
        icon: 'none'
      });
      return;
    }

    if (this.data.duration > 60 || this.data.duration <= 0) {
      wx.showToast({
        title: '请输入有效的时长（1-60分钟）',
        icon: 'none'
      });
      return;
    }

    const requestData = {
      course_id: selectedCourse.course_id,
      duration: parseInt(this.data.duration),
      start_time: this.data.startTime,
      require_location: this.data.require_location
    };

    // 如果需要定位且有位置信息，添加到请求中
    if (this.data.require_location && this.data.currentLocation) {
      requestData.latitude = this.data.currentLocation.latitude;
      requestData.longitude = this.data.currentLocation.longitude;
      requestData.location_range = 100;
    }

    api.publishCheckin(requestData).then(res => {
      if (res.status) {
        this.setData({
          qrCodeUrl: res.data
        });
        wx.showToast({
          title: '签到发布成功',
          icon: 'success'
        });
      } else {
        wx.showToast({
          title: res.message,
          icon: 'none'
        });
      }
    }).catch(err => {
      wx.hideLoading();
      console.error('签到发布失败', err);
      wx.showToast({
        title: '签到发布失败',
        icon: 'none'
      });
    });
  },

  // 预览二维码
  previewQRCode() {
    if (this.data.qrCodeUrl) {
      wx.previewImage({
        urls: [this.data.qrCodeUrl],
        current: this.data.qrCodeUrl
      });
    } else {
      wx.showToast({
        title: '请先发布签到',
        icon: 'none'
      });
    }
  }
});

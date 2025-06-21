const api = require('../../../utils/api.js');

Page({
    data: {
      student: {},
      todayCourses: []
    },
  
    onLoad() {
      this.getStudentInfo();
      this.getTodayCourses();
    },
  
    getStudentInfo() {
      const user_id = getApp().globalData.account;
      api.getStudentInfo({ student_id: user_id }).then(res => {
        if (res.status) {
          this.setData({ student: res.data });
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
    },
  
    getTodayCourses() {
      const user_id = getApp().globalData.account;
      api.getTodayCourses({ student_id: user_id }).then(res => {
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
  
    onScan: function () {
      wx.scanCode({
        success: (res) => {
          console.log('Scan success', res)
          const qrContent = res.result
          const params = this.parseQueryString(qrContent)
          
          const studentId = getApp().globalData.account
          const courseId = params['course_id']
          const checkDate = params['check_date']
          const startTime = params['start_time']
          const endTime = params['end_time']
          const requireLocation = params['require_location'] === '1'
          const qrLatitude = params['latitude']
          const qrLongitude = params['longitude']
          const locationRange = params['location_range']

          if (!courseId || !checkDate || !startTime || !endTime) {
            wx.showToast({
              title: '签到码无效',
              icon: 'none'
            })
            return
          }

          const checkinData = {
            student_id: studentId,
            course_id: courseId,
            check_date: checkDate,
            start_time: startTime,
            end_time: endTime,
            require_location: requireLocation
          }
          // 如果需要位置信息，获取当前位置
         if (requireLocation) {
            wx.getLocation({
              type: 'gcj02',
              success: (locationRes) => {
                // 添加位置相关信息
                checkinData.student_latitude = locationRes.latitude
                checkinData.student_longitude = locationRes.longitude
                checkinData.qr_latitude = qrLatitude
                checkinData.qr_longitude = qrLongitude
                checkinData.location_range = locationRange
                
                this.submitCheckin(checkinData)
              },
              fail: (err) => {
                console.error('获取位置失败', err)
                wx.showToast({
                  title: '需要获取位置信息',
                  icon: 'none'
                })
              }
            })
          } else {
            this.submitCheckin(checkinData)
          }  
        },
        fail: (err) => {
          console.error('扫码失败', err)
          wx.showToast({
            title: '扫码失败',
            icon: 'none'
          })
        }
      })
    },

    // 添加解析查询字符串的工具函数
    parseQueryString: function(queryString) {
      const params = {}
      const pairs = queryString.split('&')
      
      for (let i = 0; i < pairs.length; i++) {
        const pair = pairs[i].split('=')
        if (pair.length === 2) {
          const key = decodeURIComponent(pair[0])
          const value = decodeURIComponent(pair[1])
          params[key] = value
        }
      }
      
      return params
    },

    // 提交签到信息的函数
    submitCheckin: function(checkinData) {
      api.submitCheckin(checkinData).then(res => {
        if (res.status) {
          wx.showToast({
            title: res.message,
            icon: res.check_state === 'checked' ? 'success' : 'none'
          })
        } else {
          wx.showToast({
            title: res.message || '签到失败',
            icon: 'none'
          })
        }
      }).catch(err => {
        console.error('签到失败', err)
        wx.showToast({
          title: '签到失败',
          icon: 'none'
        })
      })
    },


    goToSchedule: function () {
      wx.navigateTo({
        url: '/pages/student/schedule/schedule'
      })
    },
    goToAttendance: function () {
      wx.navigateTo({
        url: '/pages/student/attendance/attendance'
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
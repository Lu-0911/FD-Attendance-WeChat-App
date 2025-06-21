Page({
  data: {
    teachers: [],
    courses: [],
    dates: [],
    selectedTeacherId: 'ALL', // 默认为ALL
    selectedCourseId: 'ALL',  // 默认为ALL
    selectedDate: 'ALL',      // 默认为ALL
    teacherPickerIndex: 0,
    coursePickerIndex: 0,
    datePickerIndex: 0,
    startDate: '',
    endDate: '',
  },

  onLoad: function () {
    this.getAllTeachers();
    this.getAllCourses();
    this.getAllCheckinDates(); // 获取所有考勤日期
    // 初始化日期选择器范围
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const day = now.getDate();
    this.setData({
      startDate: `2020-01-01`, // 可以设置一个较早的起始日期
      endDate: `${year}-${month < 10 ? '0' + month : month}-${day < 10 ? '0' + day : day}`
    });
  },

  getAllTeachers: function () {
    // 获取所有教师信息的API
    wx.request({
      url: getApp().globalData.baseUrl + '/admin/teachers', // 假设存在获取所有教师的API
      method: 'GET',
      success: (res) => {
        if (res.data.status) {
          const teachers = [{ teacher_id: 'ALL', name: '所有老师' }, ...res.data.data];
          this.setData({
            teachers: teachers,
          });
        } else {
          wx.showToast({
            title: '获取教师失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  getAllCourses: function () {
    // 获取所有课程信息的API
    wx.request({
      url: getApp().globalData.baseUrl + '/admin/courses', // 假设存在获取所有课程的API
      method: 'GET',
      success: (res) => {
        if (res.data.status) {
          const courses = [{ course_id: 'ALL', course_name: '所有课程' }, ...res.data.data];
          this.setData({
            courses: courses,
          });
        } else {
          wx.showToast({
            title: '获取课程失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },

  getAllCheckinDates: function () {
    const dates = ['ALL'];
    wx.request({
        url: getApp().globalData.baseUrl + '/admin/attendance/all_dates', // 假设存在
        method: 'GET',
        success: (res) => {
            if (res.data.status) {
                const fetchedDates = res.data.data.map(d => d.substring(0, 10)); // 假设日期格式为 YYYY-MM-DD HH:MM:SS
                this.setData({
                    dates: ['ALL', ...new Set(fetchedDates)], // 去重
                });
            } else {
                wx.showToast({
                    title: '获取日期失败',
                    icon: 'none'
                });
            }
        },
        fail: () => {
            wx.showToast({
                title: '网络错误',
                icon: 'none'
            });
        }
    });

    this.setData({
      dates: ['ALL', '2023-01-01', '2023-01-02'], // 示例数据，后续需从后端获取
    });
  },

  bindTeacherPickerChange: function (e) {
    const index = e.detail.value;
    const selectedTeacherId = this.data.teachers[index].teacher_id;
    this.setData({
      teacherPickerIndex: index,
      selectedTeacherId: selectedTeacherId,
    });
  },

  bindCoursePickerChange: function (e) {
    const index = e.detail.value;
    const selectedCourseId = this.data.courses[index].course_id;
    this.setData({
      coursePickerIndex: index,
      selectedCourseId: selectedCourseId,
    });
  },

  bindDatePickerChange: function (e) {
    const index = e.detail.value;
    const selectedDate = this.data.dates[index];
    this.setData({
      datePickerIndex: index,
      selectedDate: selectedDate,
    });
  },

  exportData: function () {
    const { selectedTeacherId, selectedCourseId, selectedDate } = this.data;
    const baseUrl = getApp().globalData.baseUrl;
    let exportUrl = `${baseUrl}/admin/attendance/export?`;

    // 构建查询参数
    if (selectedTeacherId !== 'ALL') {
      exportUrl += `teacher_id=${selectedTeacherId}&`;
    }
    if (selectedCourseId !== 'ALL') {
      exportUrl += `course_id=${selectedCourseId}&`;
    }
    if (selectedDate !== 'ALL') {
      exportUrl += `checkin_date=${selectedDate}&`;
    }
    
    // 移除末尾的'&'
    exportUrl = exportUrl.endsWith('&') ? exportUrl.slice(0, -1) : exportUrl;

    wx.showLoading({
      title: '导出中...',
      mask: true
    });

    wx.downloadFile({
      url: exportUrl,
      success: (res) => {
        wx.hideLoading();
        if (res.statusCode === 200) {
          wx.openDocument({
            filePath: res.tempFilePath,
            showMenu: true,
            success: (openRes) => {
              console.log('文件打开成功', openRes);
              wx.showToast({
                title: '导出成功',
                icon: 'success'
              });
            },
            fail: (openErr) => {
              console.error('文件打开失败', openErr);
              wx.showModal({
                title: '导出失败',
                showCancel: false
              });
            }
          });
        } else {
          // 处理后端返回的错误信息
          wx.request({
            url: exportUrl, // 重新请求以获取错误信息，因为downloadFile不直接返回res.data
            method: 'GET',
            success: (errorRes) => {
              wx.showToast({
                title: errorRes.data.message || '导出失败，请重试',
                icon: 'none'
              });
            },
            fail: () => {
              wx.showToast({
                title: '导出失败',
                icon: 'none'
              });
            }
          });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('下载失败', err);
        wx.showToast({
          title: '下载失败，请检查网络或稍后重试',
          icon: 'none'
        });
      }
    });
  }
}) 
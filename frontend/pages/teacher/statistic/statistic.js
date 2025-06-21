const api = require('../../../utils/api.js');

Page({
  data: {
    courses: [],
    courseIndex: 0,
    queryDate: '全部日期',
    availableDates: ['全部日期'],
    dateIndex: 0,
    showDetail: false,
    CourseName: '',
    detailList: [],
    showSelectionModal: false,
    absentStudents: [],
    absentStudentIds: []
  },

  onLoad() {
    this.loadTeacherCourses();
  },

  loadTeacherCourses() {
    const teacher_id = getApp().globalData.account;
    api.getTeacherSchedule({ teacher_id }).then(res => {
      if (res.status) {
        this.setData({ courses: res.data });  
        this.loadCheckinDates();
      } else {
        wx.showToast({
          title: res.message,
          icon: 'none'
        });
      }
    }).catch(err => {
      console.error('获取教师课程失败', err);
      wx.showToast({
        title: '获取教师课程失败',
        icon: 'none'
      });
    });
  },

  
  loadCheckinDates() {
    const selectedCourse = this.data.courses[this.data.courseIndex];
    if (!selectedCourse) return;

    api.getCheckinDates({ course_id: selectedCourse.course_id }).then(res => {
      const dates = res.status && res.data.length > 0 ? ['全部日期', ...res.data] : ['全部日期'];
      let newQueryDate = this.data.queryDate;
      if (!dates.includes(newQueryDate) || newQueryDate === '全部日期') {
        newQueryDate = dates.length > 1 ? dates[1] : dates[0];
      }
      
      this.setData({ 
        availableDates: dates,
        dateIndex: dates.indexOf(newQueryDate),
        queryDate: newQueryDate
      });
    }).catch(err => {
      this.setData({ availableDates: ['全部日期'], dateIndex: 0, queryDate: '全部日期' });
    });
  },

  bindCourseChange(e) {
    this.setData({ courseIndex: e.detail.value });
    this.loadCheckinDates();
  },

  bindDateChange(e) {
    const index = parseInt(e.detail.value);
    this.setData({
      dateIndex: index,
      queryDate: this.data.availableDates[index]
    });
  },

  queryCheckinRecords() {
    const selectedCourse = this.data.courses[this.data.courseIndex];
    if (!selectedCourse) return;
    
    const course_id = selectedCourse.course_id;
    const isAll = this.data.queryDate === '全部日期';
    const apiMethod = isAll ? 'getCheckinCount' : 'getCheckinRecords';
    const params = isAll ? { course_id } : { course_id, check_date: this.data.queryDate };

    api[apiMethod](params).then(res => {
      wx.hideLoading();
      if (res.status) {
        this.setData({
          detailList: res.data,
          CourseName: selectedCourse.course_name,
          showDetail: true
        });
      } else {
        wx.showToast({ title: res.message || '查询失败', icon: 'none' });
      }
    }).catch(() => {
      wx.hideLoading();
      wx.showToast({ title: '查询失败', icon: 'none' });
    });
  },

  onCloseModal() {
    this.setData({
      showDetail: false,
      CourseName: '',
      detailList: []
    });
  },

  registerLeave() {
    const selectedCourse = this.data.courses[this.data.courseIndex];
    if (!selectedCourse || this.data.queryDate === '全部日期') {
      wx.showToast({
        title: '请选择具体的课程和日期',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({ title: '获取缺勤学生...', mask: true });

    api.getAbsentStudents({
      course_id: selectedCourse.course_id,
      check_date: this.data.queryDate
    }).then(res => {
      wx.hideLoading();
      if (res.status) {
        if (res.data.length > 0) {
          this.setData({
            absentStudents: res.data.map(student => ({ 
              ...student, 
              student_id: String(student.student_id), 
              checked: false 
            })),
            absentStudentIds: [],
            showSelectionModal: true
          });
        } else {
          wx.showToast({
            title: '没有找到缺勤学生',
            icon: 'none'
          });
        }
      } else {
        wx.showToast({
          title: res.message || '获取缺勤学生失败',
          icon: 'none'
        });
      }
    }).catch(err => {
      wx.hideLoading();
      console.error('获取缺勤学生失败', err);
      wx.showToast({
        title: '网络错误，请稍后重试',
        icon: 'none'
      });
    });
  },

  toggleStudentSelection(e) {
    const index = e.currentTarget.dataset.index;
    const studentId = String(e.currentTarget.dataset.studentid);
    let { absentStudents, absentStudentIds } = this.data;
    
    absentStudents[index].checked = !absentStudents[index].checked;

    if (absentStudents[index].checked) {
      if (!absentStudentIds.includes(studentId)) {
        absentStudentIds = [...absentStudentIds, studentId];
      }
    } else {
      absentStudentIds = absentStudentIds.filter(id => id !== studentId);
    }

    this.setData({
      absentStudents,
      absentStudentIds
    });
  },

  confirmRegisterLeave() {
    const selectedCourse = this.data.courses[this.data.courseIndex];
    const { absentStudentIds } = this.data;

    if (absentStudentIds.length === 0) {
      wx.showToast({
        title: '请至少选择一名学生',
        icon: 'none'
      });
      return;
    }

    wx.showModal({
      title: '确认登记请假',
      content: '确定要将已选学生的缺勤记录修改为请假吗？此操作不可逆。',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '处理中...', mask: true });
          
          api.registerLeave({
            course_id: selectedCourse.course_id,
            check_date: this.data.queryDate,
            student_ids: absentStudentIds
          }).then(response => {
            wx.hideLoading();
            if (response.status) {
              wx.showToast({
                title: response.message,
                icon: 'success'
              });
              this.setData({ showSelectionModal: false });
              this.queryCheckinRecords();
            } else {
              wx.showToast({
                title: response.message || '登记请假失败',
                icon: 'none'
              });
            }
          }).catch(err => {
            wx.hideLoading();
            console.error('登记请假失败', err);
            wx.showToast({
              title: '网络错误，请稍后重试',
              icon: 'none'
            });
          });
        }
      }
    });
  },

  cancelStudentSelection() {
    this.setData({ showSelectionModal: false });
  },

  queryCheckinStatistics() {
    const selectedCourse = this.data.courses[this.data.courseIndex];
    if (!selectedCourse) {
      wx.showToast({
        title: '请选择具体的课程',
        icon: 'none'
      });
      return;
    }

    wx.navigateTo({
      url: `/pages/teacher/statistic/statistics-multi/statistics-multi?course_id=${selectedCourse.course_id}&course_name=${selectedCourse.course_name}`
    });
  },

  exportCheckinRecords: function () {
    const course_id = this.data.courses[this.data.courseIndex].course_id;
    const checkin_date = this.data.queryDate;

    wx.showLoading({title: '导出中...'});

    const baseUrl = api.getBaseUrl();
    wx.downloadFile({
      url: `${baseUrl}/teacher/checkin/export?course_id=${course_id}&checkin_date=${checkin_date}`,
      success: (res) => {
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
              wx.showToast({
                title: '文件打开失败',
                icon: 'none'
              });
            }
          });
        } else {
          wx.showToast({
            title: '导出失败: ' + res.statusCode,
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('文件下载失败', err);
        wx.showToast({
          title: '文件下载失败',
          icon: 'none'
        });
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  }
});


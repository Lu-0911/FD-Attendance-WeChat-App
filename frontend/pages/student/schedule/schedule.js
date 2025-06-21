const api = require('../../../utils/api.js');

Page({
    data: {
      weekDays: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      timeSlots: ['8:00-10:00', '10:00-12:00', '14:00-16:00', '16:00-18:00', '19:00-21:00'],
      weekCourses: [],
      showDetail: false,
      currentCourse: {}
    },
  
    onLoad() {
      this.loadCourses();
    },
  
    // prevWeek() {
    //   this.setData({ week: this.data.week - 1 }, this.loadCourses);
    // },
  
    // nextWeek() {
    //   this.setData({ week: this.data.week + 1 }, this.loadCourses);
    // },
  
    loadCourses() {
      const student_id = getApp().globalData.account;
      api.getStudentSchedule({ student_id: student_id }).then(res => {
        if (res.status) {
          const courses = res.data;
          const weekCourses = Array(5).fill(0).map(() => Array(7).fill(null));

          courses.forEach(course => {
            const courseTime = course.course_time;
            const [day, timeRange] = courseTime.split(' ');
            const dayIndex = this.data.weekDays.indexOf(day);
            const timeIndex = this.data.timeSlots.indexOf(timeRange);
              weekCourses[timeIndex][dayIndex] = {
                course_name: course.course_name,
                teacher_name: course.teacher_name,
                class_time: course.course_time,
                class_location: course.course_location,
                credit: course.credit,
                department: course.department
              };
            }
          );
          this.setData({ weekCourses: weekCourses });
        } else {
          wx.showToast({
            title: '获取课表失败',
            icon: 'none'
          });
        }
      }).catch(err => {
        console.error("获取课表失败", err);
        wx.showToast({
          title: '获取课表失败',
          icon: 'none'
        });
      });
    },

    showCourseDetail(e) {
      const course = e.currentTarget.dataset.course;
      if (course) {
        this.setData({
          showDetail: true,
          currentCourse: course
        });
      }
    },
  
    closeModal() {
      this.setData({ showDetail: false });
    }
  });
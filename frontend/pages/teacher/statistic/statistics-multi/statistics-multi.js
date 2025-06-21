const app = getApp();
const api = require('../../../../utils/api.js');

Page({
  data: {
    pickdim: 0,
    dimlist: ['年级', '性别', '院系'],
    majorList: [],
    rate_attend: [],
    rate_leave: [],
    rate_not: [],
    showSta: 0,
    course_id: '',
    course_name: ''
  },

  onLoad(options) {
    if (!options.course_id || !options.course_name) {
      wx.showToast({
        title: '参数错误',
        icon: 'none'
      });
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
      return;
    }
    
    this.setData({
      course_id: options.course_id,
      course_name: options.course_name
    });
  },

  choosedim(e) {
    this.setData({ pickdim: e.detail.value });
  },

  searchInfo() {
    let that = this;
    let pickdim = that.data.pickdim;
    let dim = that.data.dimlist[pickdim];
    let mode = '';
    if (dim === '年级') mode = 'grade';
    if (dim === '性别') mode = 'gender';
    if (dim === '院系') mode = 'dep';

    console.log('开始查询统计信息:', {
      mode: mode,
      course_id: that.data.course_id
    });

    wx.showLoading({ title: '加载中' });
    api.getCheckinStatistics({
      mode: mode,
      course_id: that.data.course_id
    }).then(res => {
      console.log('收到统计响应:', res);
      wx.hideLoading();
      
      if (!res) {
        throw new Error('响应为空');
      }

      if (res.status && res.data && res.data.length > 0) {
        let json = res.data;
        let majorList = [];
        let rate_attend = [];
        let rate_leave = [];
        let rate_not = [];

        for (let i = 0; i < json.length; i++) {
          let item = json[i];
          let total = item.total || 0;
          
          // 处理分组名称
          let groupName = item.group;
          if (mode === 'grade' && groupName) {
            groupName = groupName + '级';
          }
          majorList.push(groupName || '未分配');

          // 计算百分比
          let checked = item.checked || 0;
          let leave = item.leave || 0;
          let absent = item.absent || 0;

          if (total > 0) {
            rate_attend.push(Math.round(checked * 100 / total));
            rate_leave.push(Math.round(leave * 100 / total));
            rate_not.push(Math.round(absent * 100 / total));
          } else {
            rate_attend.push(0);
            rate_leave.push(0);
            rate_not.push(0);
          }
        }

        console.log('处理后的数据:', {
          majorList,
          rate_attend,
          rate_leave,
          rate_not
        });

        that.setData({
          majorList,
          rate_attend,
          rate_leave,
          rate_not,
          showSta: 1
        });
      } else {
        wx.showToast({ 
          title: res.message || '无数据', 
          icon: 'none',
          duration: 2000
        });
        that.setData({ showSta: 0 });
      }
    }).catch(err => {
      console.error('统计查询失败:', err);
      wx.hideLoading();
      wx.showToast({ 
        title: '查询失败，请重试', 
        icon: 'none',
        duration: 2000
      });
      that.setData({ showSta: 0 });
    });
  }
});

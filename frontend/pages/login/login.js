// pages/login/login.js
const api = require('../../utils/api');

Page({

  /**
   * 页面的初始数据
   */
  data: {
    account: '',
    password: ''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },

  // 监听账号输入
  onAccountInput(e) {
    this.setData({
      account: e.detail.value
    });
  },

  // 监听密码输入
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },

  // 登录逻辑
  onLogin() {
    const { account, password } = this.data;

    if (!account || !password) {
      wx.showToast({
        title: '账号和密码不能为空',
        icon: 'none'
      });
      return;
    }

    api.login({ user_id: account, password: password })
      .then(res => {
        if (res.status) {
          wx.showToast({
            title: '登录成功',
            icon: 'success'
          });
          // 登录成功后，保存用户信息并跳转到对应页面
          const { user_type, user_id } = res;
          getApp().globalData.userInfo = res;
          getApp().globalData.user_type = user_type;
          getApp().globalData.account = user_id;

          if (user_type === 'student') {
            wx.redirectTo({
              url: '/pages/student/home/home',
            });
          } else if (user_type === 'teacher') {
            wx.redirectTo({
              url: '/pages/teacher/home/home',
            });
          } else if (user_type === 'admin') {
            wx.redirectTo({
              url: '/pages/admin/home/home',
            });
          }
        } else {
          wx.showToast({
            title: res.message || '登录失败',
            icon: 'none'
          });
        }
      })
      .catch(err => {
        console.error('登录请求失败', err);
        wx.showToast({
          title: '网络错误，请稍后再试',
          icon: 'none'
        });
      });
  }
})
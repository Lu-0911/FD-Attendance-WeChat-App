// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 登录
    wx.login({
      success: res => {
        
      }
    })
  },

  globalData: {
    userInfo: null,
    account: null,
    user_type: null,
    baseUrl:'http://127.0.0.1:5000'
    // baseUrl: 'http://localhost:5000' // 后端服务地址
  }
})
const api = require('../../../utils/api.js');

Page({
    data: {
      oldPassword: '',
      newPassword: ''
    },
  
    onOldPasswordInput(e) {
      this.setData({ oldPassword: e.detail.value });
    },
  
    onNewPasswordInput(e) {
      this.setData({ newPassword: e.detail.value });
    },
  
    onChangePassword() {
      const { oldPassword, newPassword } = this.data;
      const user_id = getApp().globalData.account;
  
      if (!oldPassword || !newPassword) {
        wx.showToast({ title: '请输入完整信息', icon: 'none' });
        return;
      }

      api.changePassword({ user_id, oldPassword, newPassword }).then(res => {
        if (res.status) {
          wx.showToast({ title: res.message });
        } else {
          wx.showToast({ title: res.message, icon: 'none' });
        }
      }).catch(err => {
        console.error('修改密码失败', err);
        wx.showToast({ title: '修改密码失败', icon: 'none' });
      });
    },
  
    onLogout() {
      wx.clearStorageSync();
      getApp().globalData.account = null;
      getApp().globalData.role = null;
      wx.reLaunch({
        url: '../../login/login'
      });
    }
  });
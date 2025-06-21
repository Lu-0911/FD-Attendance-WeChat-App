const api = require('../../../utils/api.js');

Page({
    data: {
      admin: {}
    },
  
    onLoad() {
      this.getAdminInfo();
    },
  
    getAdminInfo() {
      const adminAccount = getApp().globalData.account;
      this.setData({
        admin: {
          account: adminAccount,
          name: '管理员'
        }
      });
    },
  
    goToImport: function () {
      wx.navigateTo({
        url: '../import/import'
      })
    },
  
    goToExport: function () {
      wx.navigateTo({
        url: '../export/export'
      })
    },
    goToEdit: function () {
      wx.navigateTo({
        url: '../edit/edit'
      })
    },
    goToDelete: function () {
      wx.navigateTo({
        url: '../delete/delete'
      })
    },
    goToSettings() {
      wx.navigateTo({ url: '../../common/settings/settings' });
    }
  });
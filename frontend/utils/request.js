const request = (url, method, data) => {
  const app = getApp(); // 获取全局应用实例
  const baseUrl = app.globalData.baseUrl || 'http://localhost:5000';
  
  return new Promise((resolve, reject) => {
    wx.request({
      url: baseUrl + url,
      method: method,
      data: data,
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else {
          reject(res.statusCode);
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};

module.exports = {
  request
};
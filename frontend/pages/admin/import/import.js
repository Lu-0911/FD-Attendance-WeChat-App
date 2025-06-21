const api = require('../../../utils/api.js');

Page({
  data: {
    importType: 'students', // students, teachers, courses, student_courses
    importTypes: [
      { value: 'students', label: '学生信息' },
      { value: 'teachers', label: '教师信息' },
      { value: 'courses', label: '课程信息' },
      { value: 'student_courses', label: '学生课程表' },
      { value: 'users', label: '用户信息' }
    ],
    importTypeIndex: 0, // 新增：用于picker的索引
    filePath: '',
    uploading: false,
    uploadResult: null
  },

  onLoad() {
    // 初始化时根据importType设置正确的importTypeIndex
    const initialType = this.data.importType;
    const initialIndex = this.data.importTypes.findIndex(item => item.value === initialType);
    if (initialIndex !== -1) {
      this.setData({ importTypeIndex: initialIndex });
    }
  },

  bindTypeChange(e) {
    const index = parseInt(e.detail.value);
    this.setData({
      importTypeIndex: index, // 更新索引
      importType: this.data.importTypes[index].value, // 更新实际值
      filePath: '',
      uploadResult: null
    });
  },

  chooseFile() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['xlsx'],
      success: (res) => {
        const tempFilePath = res.tempFiles[0].path;
        this.setData({
          filePath: tempFilePath,
          uploadResult: null
        });
      },
      fail: (err) => {
        console.error('选择文件失败', err);
        wx.showToast({
          title: '选择文件失败',
          icon: 'none'
        });
      }
    });
  },

  uploadFile() {
    if (!this.data.filePath) {
      wx.showToast({
        title: '请先选择文件',
        icon: 'none'
      });
      return;
    }

    this.setData({ uploading: true });

    const baseUrl = api.getBaseUrl();
    wx.uploadFile({
      url: `${baseUrl}/admin/import/${this.data.importType}`,
      filePath: this.data.filePath,
      name: 'file',
      success: (res) => {
        try {
          const result = JSON.parse(res.data);
          this.setData({
            uploadResult: result
          });
          
          if (result.status) {
            wx.showToast({
              title: '导入成功',
              icon: 'success'
            });
          } else {
            wx.showToast({
              title: result.message || '导入失败',
              icon: 'none'
            });
          }
        } catch (err) {
          console.error('解析响应失败', err);
          wx.showToast({
            title: '导入失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.error('上传文件失败', err);
        wx.showToast({
          title: '上传文件失败',
          icon: 'none'
        });
      },
      complete: () => {
        this.setData({ uploading: false });
      }
    });
  },

  downloadTemplate() {
    const templateMap = {
      students: '学生信息导入模板.xlsx',
      teachers: '教师信息导入模板.xlsx',
      courses: '课程信息导入模板.xlsx',
      student_courses: '学生课程表导入模板.xlsx',
      users: '用户信息导入模板.xlsx'
    };

    const templateName = templateMap[this.data.importType];
    if (!templateName) return;

    const baseUrl = api.getBaseUrl();
    wx.downloadFile({
      url: `${baseUrl}/static/templates/${templateName}`,
      success: (res) => {
        if (res.statusCode === 200) {
          wx.openDocument({
            filePath: res.tempFilePath,
            showMenu: true,
            success: () => {
              wx.showToast({
                title: '模板下载成功',
                icon: 'success'
              });
            },
            fail: () => {
              wx.showToast({
                title: '打开模板失败',
                icon: 'none'
              });
            }
          });
        } else {
          wx.showToast({
            title: '下载模板失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '下载模板失败',
          icon: 'none'
        });
      }
    });
  }
}); 
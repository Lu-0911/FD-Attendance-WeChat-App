const api = require('../../../utils/api.js');

Page({
  data: {
    searchID: '',
    info: null,
    searched: false,
    currentType: '',
    originalInfo: null
  },

  // 字段标签映射
  labels: {
    student: { name: '学生姓名', gender: '性别', department: '学院', major: '专业', grade: '年级', birthday: '生日' },
    teacher: { name: '教师姓名', gender: '性别', department: '部门', title: '职称', birthday: '生日' },
    course: { course_name: '课程名称', credit: '学分', teacher_id: '教师ID', department: '开课学院', course_time: '上课时间', course_location: '上课地点' }
  },

  // 字段显示顺序
  fieldOrders: {
    student: ['name', 'gender', 'department', 'major', 'grade', 'birthday'],
    teacher: ['name', 'gender', 'department', 'title', 'birthday'],
    course: ['course_name', 'credit', 'teacher_id', 'department', 'course_time', 'course_location']
  },

  onIDInput(e) {
    this.setData({ searchID: e.detail.value });
  },

  async searchInfo() {
    const id = this.data.searchID;
    if (!id) {
      wx.showToast({ title: '请输入ID', icon: 'none' });
      return;
    }

    this.setData({ info: null, searched: false, currentType: '', originalInfo: null });
    wx.showLoading({ title: '搜索中...' });

    // 依次搜索三种类型
    const types = ['student', 'teacher', 'course'];
    let foundInfo = null, foundType = '';

    for (const type of types) {
      const res = await api.getAdminInfo({ id, type });
      if (res.status && res.data) {
        foundInfo = res.data;
        foundType = type;
        break;
      }
    }

    wx.hideLoading();

    if (foundInfo) {
      const displayInfo = this.formatDisplayInfo(foundInfo, foundType);
      this.setData({
        info: displayInfo,
        originalInfo: foundInfo,
        searched: true,
        currentType: foundType
      });
    } else {
      this.setData({ info: null, searched: true });
      wx.showToast({ title: '未找到相关信息', icon: 'none' });
    }
  },

  // 格式化显示信息
  formatDisplayInfo(data, type) {
    const displayInfo = [];
    const order = this.fieldOrders[type] || [];
    
    // 按顺序添加字段
    order.forEach(key => {
      if (data.hasOwnProperty(key)) {
        displayInfo.push({
          label: this.labels[type]?.[key] || key,
          value: data[key],
          key
        });
      }
    });

    // 添加其他字段（排除ID字段）
    Object.keys(data).forEach(key => {
      if (!key.includes('_id') && !order.includes(key)) {
        displayInfo.push({
          label: this.labels[type]?.[key] || key,
          value: data[key],
          key
        });
      }
    });

    return displayInfo;
  },

  onInfoInputChange(e) {
    const { key } = e.currentTarget.dataset;
    const { value } = e.detail;
    const updatedInfo = this.data.info.map(item => 
      item.key === key ? { ...item, value } : item
    );
    this.setData({ info: updatedInfo });
  },

  async submitModification() {
    const { info, originalInfo, currentType } = this.data;
    if (!info || !currentType) {
      wx.showToast({ title: '无信息可提交', icon: 'none' });
      return;
    }

    // 构建修改数据
    const modifiedData = {};
    info.forEach(item => { modifiedData[item.key] = item.value; });
    
    // 添加ID字段
    const idField = `${currentType}_id`;
    modifiedData[idField] = originalInfo[idField];

    await this.performOperation('update', modifiedData, currentType, '修改');
  },

  async deleteCurrentInfo() {
    const { originalInfo, currentType } = this.data;
    if (!originalInfo || !currentType) {
      wx.showToast({ title: '无信息可删除', icon: 'none' });
      return;
    }

    const typeNames = { student: '学生', teacher: '教师', course: '课程' };
    wx.showModal({
      title: '确认删除',
      content: `确定要删除这条${typeNames[currentType]}信息吗？此操作不可撤销。`,
      success: async (res) => {
        if (res.confirm) {
          const idField = `${currentType}_id`;
          const deleteData = { [idField]: originalInfo[idField] };
          await this.performOperation('delete', deleteData, currentType, '删除');
        }
      }
    });
  },

  // 统一的操作处理函数
  async performOperation(operation, data, type, operationName) {
    wx.showLoading({ title: `${operationName}中...` });

    try {
      let res;
      const apiMap = {
        update: { student: 'updateStudent', teacher: 'updateTeacher', course: 'updateCourse' },
        delete: { student: 'deleteStudent', teacher: 'deleteTeacher', course: 'deleteCourse' }
      };

      const apiMethod = apiMap[operation][type];
      if (apiMethod) {
        res = await api[apiMethod](data);
      } else {
        throw new Error('未知操作类型');
      }

      wx.hideLoading();

      if (res.status) {
        wx.showToast({ title: `${operationName}成功`, icon: 'success' });
        this.clearData();
      } else {
        wx.showToast({ title: res.message || `${operationName}失败`, icon: 'none' });
      }
    } catch (error) {
      wx.hideLoading();
      wx.showToast({ title: `${operationName}失败，请稍后再试`, icon: 'none' });
      console.error(`${operationName}操作发生错误:`, error);
    }
  },

  // 清空数据
  clearData() {
    this.setData({
      searchID: '',
      info: null,
      searched: false,
      currentType: '',
      originalInfo: null
    });
  }
});

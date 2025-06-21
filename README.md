# FD-Attendance-WeChat-App FD微信考勤小程序
## 1.文件目录结构

```
.
├── README.md
├── database.sql # 数据库构建文件，包含一些测试数据
├── requirements.txt # 依赖包列表
├── backend # 后端代码
│   ├── app.py # 后端程序入口
│   ├── init.py # 后端初始化配置
│   ├── models.py # 数据库模型定义与映射
│   ├── routes.py # 所有的后端接口定义
│   ├── static
|   │   ├── qr_codes # 存放二维码图片
|   │   └── templates # 存放导入表格模板
└── frontend # 前端代码
    ├── app.js # 程序入口
    ├── app.json # 程序配置文件
    ├── app.wxss # 全局样式文件
    ├── project.config.json
    ├── project.private.config.json
    ├── utils
    │   ├── api.js # 封装的后端接口请求函数
    │   └── request.js # 封装的请求函数
    └── pages
        ├── login # 登录页面
        ├── student
        │   ├── home # 学生主页
        |   ├── schedule # 学生课表
        │   └── attendance # 学生查看考勤记录
        ├── teacher
        |   ├── home # 教师主页
        |   ├── publishCheckin # 发布签到页面
        │   └── statistics # 教师考勤统计页面
        ├── admin # 管理员页面
        |   ├── home # 管理员主页
        |   ├── delete # 根据学生、教师、课程、考勤记录id删除有关信息
        |   ├── edit # 根据学生、教师、课程id修改有关信息
        |   ├── export # 导出考勤信息页面
        │   └── import # 导入信息页面 
        └── common
            ├── settings # 设置页面
            └── info # 个人信息页面
```

基本运行逻辑为前端页面进行操作，由api.js中的函数发送请求到后端，通过routes.py中的接口定义进行处理，返回数据给前端，前端页面进行渲染。

## 2.创建python虚拟环境并激活，后端基于Flask框架

```bash
cd work_dir
python -m venv .flask_env
.flask_env\Scripts\activate
```

## 3.安装依赖包

```bash
pip install -r requirements.txt
```

## 4.构建数据库
构建数据库见sql文件 `database.sql`，文件中已包含数据库及表的创建，包含测试数据插入。
创建数据库attendtance_system,在MySQL workbench直接运行 `database.sql` 文件即可。

## 5.配置数据库连接URI
见 `backend/init.py`，需修改数据库密码。

```bash
# MySQL数据库连接URI，格式：mysql+连接器://用户名:密码@主机:端口/数据库名,这里需要替换密码和数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:密码@localhost:3306/attendance_system'
```

## 6.运行小程序
运行 `app.py`文件，启动后端程序。

安装微信开发者工具，前端在微信开发者工具应用内导入`frontend`目录，进行编译测试。

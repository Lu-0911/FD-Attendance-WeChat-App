import json
from datetime import datetime, date
import decimal

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# JSON编码器，用于特殊数据类型序列化为JSON格式
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # 支持datetime、date、decimal类型的标准序列化
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


app = Flask(__name__)
# MySQL数据库连接URI，格式：mysql+连接器://用户名:密码@主机:端口/数据库名
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost:3306/attendance_system'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/attendance_system'

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True # 每次请求结束后自动提交数据库事务，开发完毕后关闭

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # 跟踪对象的修改并且发送信号，开发完毕后关闭

app.json_encoder = JSONEncoder

# 初始化SQLAlchemy数据库对象
db = SQLAlchemy(app)

from flask import request, jsonify, send_file
from datetime import datetime, timedelta
import qrcode
from flask import current_app
import os
import pandas as pd
import io

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import atexit

from sqlalchemy import func
from sqlalchemy import case
import bcrypt
import re

from init import app, db
from models import *


# 初始化调度器
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


# ======================================== 登录和退出相关接口 ========================================

# 根路径API接口，检查服务状态
@app.route('/')
def index():
    return jsonify({
        "status": "服务运行正常",
        "api_version": "1.0"
    })

# 登录接口
@app.route('/login', methods=['POST'])
def login():
    if not request.json:
        return jsonify('not json')
    
    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({'status': False, 'message': '账号或密码不能为空'})
        
    # 查询用户身份
    user = User.query.filter_by(user_id=user_id).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({
            'status': True,
            'message': '登录成功',
            'user_id': user.user_id,
            'user_type': user.user_type
        })
    else:
        return jsonify({'status': False, 'message': '账号或密码错误'})


# 修改密码接口
@app.route('/changePassword', methods=['POST'])
def change_password():
    if not request.json:
        return jsonify('not json')

    data = request.get_json()
    user_id = data.get('user_id')
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    # 查询用户身份
    user = User.query.filter_by(user_id=user_id).first()
    if not bcrypt.checkpw(old_password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'status': False,'message': '旧密码错误'})

    # 保存加密的新密码
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    db.session.commit()

    return jsonify({'status': True,'message': '密码修改成功'})


# ==========================================  学生信息相关接口 ========================================

# 查询学生基本信息的接口
@app.route('/student/info', methods=['POST'])
def student_info():
    data = request.get_json()
    student_id = data.get('student_id')

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({'status': False, 'message': '学生不存在'})

    return jsonify({
        'status': True,
        'data': {
            'student_id': student.student_id,
            'name': student.name,
            'gender': student.gender,
            'department': student.department,
            'major': student.major,
            'grade': student.grade,
            'birthday': student.birthday
        }
    })


# 查询课表的接口
@app.route('/student/schedule', methods=['POST'])
def schedule():
    data = request.get_json()
    student_id = data.get('student_id')

    # 联合查询学生选课信息、课程信息和教师信息
    courses = (db.session.query(Course, Teacher.name.label('teacher_name'))
               .join(StudentCourse, StudentCourse.course_id == Course.course_id)
               .join(Teacher, Course.teacher_id == Teacher.teacher_id)
               .filter(StudentCourse.student_id == student_id)
               .all())

    course_list = []
    for course, teacher_name in courses:
        course_list.append({
            'course_id': course.course_id,
            'course_name': course.course_name,
            'credit': course.credit,
            'teacher_name': teacher_name,
            'department': course.department,
            'course_time': course.course_time,
            'course_location': course.course_location
        })

    return jsonify({'status': True, 'data': course_list})


# 查询今日课程的接口
@app.route('/student/schedule/today', methods=['POST'])
def today_schedule():
    data = request.get_json()
    student_id = data.get('student_id')

    today = datetime.today()
    weekday = today.weekday()
    weekday_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday]

    # 查询学生的课程表
    courses = (db.session.query(Course)
               .join(StudentCourse, StudentCourse.course_id == Course.course_id)
               .filter(StudentCourse.student_id == student_id)
               .filter(Course.course_time.like(f"%{weekday_name}%"))  # 过滤出今天的课程
               .all())

    if not courses:
        return jsonify({'status': False})

    course_list = []
    for course in courses:
        course_list.append({
            'course_name': course.course_name,
            'teacher_id': course.teacher_id,
            'course_time': course.course_time,
            'course_location': course.course_location
        })

    return jsonify({'status': True, 'data': course_list})


# ==========================================  教师信息相关接口 ========================================

# 查询教师基本信息的接口
@app.route('/teacher/info', methods=['POST'])
def teacher_info():
    data = request.get_json()
    teacher_id = data.get('teacher_id')

    teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
    if not teacher:
        return jsonify({'status': False, 'message': '教师不存在'})

    return jsonify({
        'status': True,
        'data': {
            'teacher_id': teacher.teacher_id,
            'name': teacher.name,
            'gender': teacher.gender,
            'department': teacher.department,
            'title': teacher.title,
            'birthday': teacher.birthday
        }
    })


# 教师课程列表接口
@app.route('/teacher/schedule', methods=['POST'])
def get_teacher_courses():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    
    courses = Course.query.filter_by(teacher_id=teacher_id).all()
    
    if not courses:
        return jsonify({'status': False, 'message': '没有课程数据'})

    course_list = []
    for course in courses:
        course_list.append({
            'course_id': course.course_id,
            'course_name': course.course_name,
            'credit': course.credit,
            'teacher_id': course.teacher_id,
            'department': course.department,
            'course_time': course.course_time,
            'course_location': course.course_location
        })
    return jsonify({'status': True, 'data': course_list})


# 查询教师今日授课的接口
@app.route('/teacher/schedule/today', methods=['POST'])
def teacher_today_schedule():
    data = request.get_json()
    teacher_id = data.get('teacher_id')

    today = datetime.today()
    weekday = today.weekday()
    weekday_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday]

    # 查询教师的课程表
    courses = (db.session.query(Course)
            .filter(Course.teacher_id == teacher_id)
            .filter(Course.course_time.like(f"%{weekday_name}%"))
            .all())

    if not courses:
        return jsonify({'status': False})

    course_list = []
    for course in courses:
        course_list.append({
            'course_id': course.course_id,
            'course_name': course.course_name,
            'teacher_id': course.teacher_id,
            'course_time': course.course_time,
            'course_location': course.course_location
        })

    return jsonify({'status': True, 'data': course_list})


# ==========================================  发布签到相关接口 ========================================

# 教师发布签到接口
@app.route('/teacher/checkin/publish', methods=['POST'])
def publish_checkin():
    data = request.get_json()
    course_id, duration, start_time_str = data.get('course_id'), data.get('duration'), data.get('start_time')
    require_location = data.get('require_location', False)
    latitude, longitude, location_range = data.get('latitude'), data.get('longitude'), data.get('location_range')
    
    # 参数验证
    if not all([course_id, duration, start_time_str]):
        return jsonify({'status': False, 'message': '缺少签到信息'})
    
    if require_location and (not latitude or not longitude):
        return jsonify({'status': False, 'message': '缺少定位信息'})

    # 时间处理
    check_date = datetime.now().date()
    start_datetime = datetime.combine(check_date, datetime.strptime(start_time_str, '%H:%M').time())
    end_datetime = start_datetime + timedelta(minutes=int(duration))
    
    try:
        # 生成二维码
        qr_content = f"course_id={course_id}&check_date={check_date}&start_time={int(start_datetime.timestamp())}&end_time={int(end_datetime.timestamp())}&require_location={int(require_location)}"
        if require_location:
            qr_content += f"&latitude={latitude}&longitude={longitude}&location_range={location_range}"
        
        qr_url = generate_qr_code(qr_content, course_id, check_date)

        # 查看是否有重复签到
        if AttendanceRequirement.query.filter_by(course_id=course_id, check_date=check_date).first():
            return jsonify({'status': False, 'message': '已经发布过签到了'})
        
        # 保存签到要求
        save_requirement(course_id, check_date, start_datetime, end_datetime, require_location)
        
        # 添加定时任务
        scheduler.add_job(
            auto_close_checkin,
            DateTrigger(run_date=end_datetime),
            args=[course_id, check_date],
            id=f"close_{course_id}_{check_date}_{int(datetime.now().timestamp())}"
        )
        
        db.session.commit()

        return jsonify({'status': True, 'data': qr_url})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': '签到发布失败'})

# 生成二维码
def generate_qr_code(content, course_id, check_date):
    qr_dir = os.path.join(current_app.root_path, 'static', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    filename = f"{course_id}_{check_date}_{int(datetime.now().timestamp())}.png"
    filepath = os.path.join(qr_dir, filename)
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filepath)
    
    return f"{request.url_root.rstrip('/')}/static/qr_codes/{filename}"

# 保存签到要求
def save_requirement(course_id, check_date, start_datetime, end_datetime, require_location):
    requirement = AttendanceRequirement(
        course_id=course_id, check_date=check_date,
        start_time=start_datetime.time(), end_time=end_datetime.time(),
        location=require_location
    )
    db.session.add(requirement)

# 获取选课学生
def get_course_students(course_id):
    student_courses = StudentCourse.query.filter_by(course_id=course_id).all()
    return [sc.student_id for sc in student_courses]

# 定时任务函数,签到结束时自动处理缺勤和统计
def auto_close_checkin(course_id, check_date):
    with app.app_context():
        try:
            students = get_course_students(course_id)
            for student_id in students:
                # 检查是否签到过
                if not check_already_signed(student_id, course_id, check_date):
                    db.session.add(AttendanceLog(
                        student_id=student_id, course_id=course_id,
                        check_time=datetime.now(), location=False, check_state='absent'
                    ))
                
                # 更新应签次数
                count = AttendanceCount.query.filter_by(student_id=student_id, course_id=course_id).first()
                if not count:
                    db.session.add(AttendanceCount(
                        student_id=student_id, course_id=course_id,
                        actual_count=0, need_count=1
                    ))
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"自动处理签到失败: {e}")

# 检查是否已经签到过
def check_already_signed(student_id, course_id, check_date):
    return AttendanceLog.query.filter(
        AttendanceLog.student_id == student_id,
        AttendanceLog.course_id == course_id,
        db.func.date(AttendanceLog.check_time) == check_date
    ).first() is not None


# ==========================================  学生签到相关接口 ========================================

# 学生签到接口
@app.route('/student/checkin/submit', methods=['POST'])
def submit_checkin():
    data = request.get_json()
    required_fields = ['student_id', 'course_id', 'check_date', 'start_time', 'end_time']
    
    if not all(data.get(field) for field in required_fields):
        return jsonify({'status': False, 'message': '签到码无效'})

    try:
        # 解析参数
        student_id, course_id = data['student_id'], data['course_id']
        check_date_obj = datetime.strptime(data['check_date'], '%Y-%m-%d').date()
        start_time_obj = datetime.fromtimestamp(int(data['start_time']))
        end_time_obj = datetime.fromtimestamp(int(data['end_time']))
        current_time = datetime.now()

        # 验证签到要求和重复签到
        if not verify_checkin_requirement(course_id, check_date_obj):
            return jsonify({'status': False, 'message': '签到要求不存在'})
        
        if check_already_signed(student_id, course_id, check_date_obj):
            return jsonify({'status': False, 'message': '已经签到过了'})

        # 验证时间和位置
        time_valid, time_msg = validate_time(current_time, start_time_obj, end_time_obj)
        if not time_valid:
            return jsonify({'status': False, 'message': time_msg})
            
        location_valid, location_msg = validate_location(data)
        if location_msg:
            return jsonify({'status': False, 'message': location_msg})

        # 保存签到记录和更新统计
        check_state = 'checked' if time_valid and location_valid else 'absent'
        save_attendance(student_id, course_id, current_time, data.get('require_location', False), location_valid, check_state)
        
        db.session.commit()
        return jsonify({'status': True, 'message': '签到成功' if check_state == 'checked' else '签到失败', 'check_state': check_state})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': '签到失败'})

# 验证签到要求
def verify_checkin_requirement(course_id, check_date):
    return AttendanceRequirement.query.filter_by(course_id=course_id, check_date=check_date).first() is not None

# 判定签到时间
def validate_time(current, start, end):
    if current < start:
        return False, '签到时间未到'
    elif current > end:
        return False, '签到时间已过'
    return True, None

# 判定签到位置
def validate_location(data):
    if not data.get('require_location'):
        return True, None
        
    if not all([data.get('qr_latitude'), data.get('qr_longitude')]):
        return True, None
        
    if not all([data.get('student_latitude'), data.get('student_longitude')]):
        return False, '需要获取您的位置信息'
        
    distance = calculate_distance(
        float(data['student_latitude']), float(data['student_longitude']),
        float(data['qr_latitude']), float(data['qr_longitude'])
    )
    
    if distance > data.get('location_range', 100):
        return False, '不在签到范围内'
    return True, None

# 保存签到记录和更新统计
def save_attendance(student_id, course_id, check_time, require_location, location_valid, check_state):
    # 保存签到记录
    log = AttendanceLog(
        student_id=student_id, course_id=course_id, check_time=check_time,
        location=location_valid and require_location, check_state=check_state
    )
    db.session.add(log)
    
    # 更新统计
    count = AttendanceCount.query.filter_by(student_id=student_id, course_id=course_id).first()
    if count:
        if check_state == 'checked':
            count.actual_count += 1
            count.need_count += 1
    else:
        db.session.add(AttendanceCount(
            student_id=student_id, course_id=course_id,
            actual_count=1 if check_state == 'checked' else 0,
            need_count=1
        ))

# 计算距离
def calculate_distance(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, asin, sqrt
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371000


# ==========================================  学生端考勤查询接口 ========================================

# 查询学生的考勤统计接口
@app.route('/attendance/count', methods=['POST'])
def attendance_count():
    data = request.get_json()
    student_id = data.get('student_id')

    # 查询学生的考勤次数统计
    attendance_counts = (db.session.query(AttendanceCount, Course.course_name) 
                         .join(Course, AttendanceCount.course_id == Course.course_id)
                         .filter(AttendanceCount.student_id == student_id)
                         .all())
    
    if not attendance_counts:
        return jsonify({'status': False, 'message': '没有考勤数据'})

    attendance_list = []
    for record, course_name in attendance_counts:
        attendance_list.append({
            'course_id': record.course_id,
            'course_name': course_name,
            'actual_count': record.actual_count,
            'need_count': record.need_count
        })

    return jsonify({'status': True, 'data': attendance_list})


# 某学生某课程的考勤记录接口
@app.route('/attendance/records', methods=['POST'])
def get_attendance_records():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')

    #  查询该学生在指定课程的所有考勤记录
    attendance_records = (db.session.query(AttendanceLog)
                         .filter(AttendanceLog.student_id==student_id, AttendanceLog.course_id==course_id)
                         .order_by(AttendanceLog.check_time.asc())
                         .all())

    if not attendance_records:
        return jsonify({'status': False, 'message': '没有考勤记录'})

    records_list = []
    for record in attendance_records:
        records_list.append({
            'check_time': record.check_time.strftime('%Y-%m-%d %H:%M:%S'),
            'check_state': record.check_state,
            'location': record.location
        })
    return jsonify({'status': True, 'data': records_list})


# ==========================================  教师端考勤统计接口 ========================================

# 获取发布过签到的日期
@app.route('/teacher/checkin/dates', methods=['POST'])
def get_checkin_dates():
    data = request.get_json()
    course_id = data.get('course_id')

    dates = (db.session.query(AttendanceRequirement.check_date)
                    .filter(AttendanceRequirement.course_id == course_id)
                    .order_by(AttendanceRequirement.check_date.desc())).all()

    dates = [date[0].strftime('%Y-%m-%d') for date in dates]
    return jsonify({'status': True, 'data': dates})


# 获取某课程某次的签到记录
@app.route('/teacher/checkin/records', methods=['POST'])
def get_checkin_records():
    data = request.get_json()
    course_id = data.get('course_id')
    check_date = data.get('check_date')

    if not course_id or not check_date:
        return jsonify({'status': False, 'message': '缺少课程或日期'})

    try:
        # 查询指定课程和日期的所有学生的考勤记录
        results = (db.session.query(AttendanceLog, Student.name)
                             .join(Student, AttendanceLog.student_id == Student.student_id)
                             .filter(AttendanceLog.course_id == course_id,
                             db.func.date(AttendanceLog.check_time) == datetime.strptime(check_date, '%Y-%m-%d').date())
                             .order_by(AttendanceLog.check_state.asc())
                             .all())

        result_list = []
        for log, student_name in results:
            result_list.append({
                'student_id': log.student_id,
                'student_name': student_name,
                'status': log.check_state,
            })
        return jsonify({'status': True, 'data': result_list})
    except Exception as e:
        return jsonify({'status': False, 'message': '查询失败'})


# 获取全班学生考勤统计
@app.route('/teacher/checkin/count', methods=['POST'])
def get_checkin_count():  
    data = request.get_json()
    course_id = data.get('course_id')
    
    if not course_id:
        return jsonify({'status': False, 'message': '缺少课程'})
    
    try:
        students = get_course_students(course_id)
        
        if not students:
            return jsonify({'status': True, 'data': []})
        
        # 查询学生信息和考勤统计
        results = (db.session.query(Student.student_id, Student.name, 
                                   AttendanceCount.actual_count, AttendanceCount.need_count)
                            .outerjoin(AttendanceCount, 
                                     (Student.student_id == AttendanceCount.student_id) & 
                                     (AttendanceCount.course_id == course_id))
                            .filter(Student.student_id.in_(students))
                            .order_by(Student.student_id)
                            .all())
        
        result_list = []
        for student_id, student_name, actual_count, need_count in results:
            
            result_list.append({
                'student_id': student_id,
                'student_name': student_name,
                'actual_count': actual_count,
                'need_count': need_count
            })
        
        return jsonify({'status': True, 'data': result_list})
    except Exception as e:
        return jsonify({'status': False, 'message': '查询失败'})


# 获取缺勤学生列表
@app.route('/teacher/checkin/absent_students', methods=['POST'])
def get_absent_students():
    data = request.get_json()
    course_id = data.get('course_id')
    check_date_str = data.get('check_date')

    if not course_id or not check_date_str:
        return jsonify({'status': False, 'message': '缺少课程ID或日期'})

    try:
        check_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()

        absent_records = db.session.query(AttendanceLog, Student.name).join(Student, AttendanceLog.student_id == Student.student_id).filter(
            AttendanceLog.course_id == course_id,
            db.func.date(AttendanceLog.check_time) == check_date,
            AttendanceLog.check_state == 'absent'
        ).all()

        absent_students_list = [{'student_id': record.AttendanceLog.student_id, 'student_name': record.name} for record in absent_records]

        return jsonify({'status': True, 'data': absent_students_list})
    
    except Exception as e:
        print(f"获取缺勤学生列表失败: {str(e)}")
        print(f"DEBUG: Error in get_absent_students: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': False, 'message': '获取缺勤学生列表失败'})


# 登记请假接口
@app.route('/teacher/checkin/register_leave', methods=['POST'])
def register_leave():
    data = request.get_json()
    course_id = data.get('course_id')
    check_date_str = data.get('check_date')
    student_ids = data.get('student_ids')

    if not course_id or not check_date_str:
        return jsonify({'status': False, 'message': '缺少课程ID或日期'})

    try:
        check_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()

        query = AttendanceLog.query.filter(
            AttendanceLog.course_id == course_id,
            db.func.date(AttendanceLog.check_time) == check_date,
            AttendanceLog.check_state == 'absent'
        )

        if student_ids is not None:
            query = query.filter(AttendanceLog.student_id.in_(student_ids))

        absent_records = query.all()

        if not absent_records:
            return jsonify({'status': True, 'message': '没有找到缺勤记录或指定学生的记录，无需修改。'})

        for record in absent_records:
            record.check_state = 'leave'
        
        db.session.commit()

        return jsonify({'status': True, 'message': f'已成功将 {len(absent_records)} 条缺勤记录修改为请假。'})

    except Exception as e:
        db.session.rollback()
        print(f"登记请假失败: {str(e)}")
        return jsonify({'status': False, 'message': f'登记请假失败: {str(e)}'})


# 获取不同维度的学生考勤统计结果，支持按院系、性别、年级进行统计
@app.route('/teacher/checkin/statistics', methods=['POST'])
def get_attendance_statistics():
    data = request.get_json()
    mode = data.get('mode')  # 'dep', 'gender', 'grade'
    course_id = data.get('course_id')
    
    if not course_id:
        return jsonify({'status': False, 'message': '缺少课程ID'})
    
    try:
        # 根据统计维度选择分组字段
        if mode == 'dep':
            group_field = Student.department
        elif mode == 'gender':
            group_field = Student.gender
        elif mode == 'grade':
            group_field = Student.grade
        else:
            return jsonify({'status': False, 'message': '无效的统计维度'})

        # 基础查询
        query = db.session.query(
            group_field.label('group'),
            func.count(AttendanceLog.log_id).label('total'),
            func.sum(case((AttendanceLog.check_state == 'checked', 1), else_=0)).label('checked'),
            func.sum(case((AttendanceLog.check_state == 'absent', 1), else_=0)).label('absent'),
            func.sum(case((AttendanceLog.check_state == 'leave', 1), else_=0)).label('leave')
        ).join(AttendanceLog, Student.student_id == AttendanceLog.student_id)
        
        # 添加课程筛选
        query = query.filter(AttendanceLog.course_id == course_id)
        
        # 根据统计维度分组
        query = query.group_by(group_field)
        
        # 执行查询并处理结果
        results = query.all()
        result = [{
            'group': str(item.group) if item.group else '未分配',
            'total': item.total or 0,
            'checked': item.checked or 0,
            'absent': item.absent or 0,
            'leave': item.leave or 0
        } for item in results]
        
        return jsonify({
            'status': True,
            'data': result
        })
    except Exception as e:
        print(f"统计查询错误: {str(e)}")
        return jsonify({'status': False, 'message': '查询失败'})

# 导出考勤记录接口
@app.route('/teacher/checkin/export', methods=['GET'])
def export_attendance():
    course_id = request.args.get('course_id')
    checkin_date = request.args.get('checkin_date')
    
    if not course_id:
        return jsonify({'status': False, 'message': '缺少课程ID'})
    
    try:
        # 获取课程信息
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'status': False, 'message': '课程不存在'})
        
        # 状态转换映射
        status_map = {
            'checked': '出勤',
            'leave': '请假',
            'absent': '缺勤'
        }
        
        if checkin_date and checkin_date != '全部日期':
            # 单日期导出：保持原有格式
            query = db.session.query(
                Student.student_id,
                Student.name.label('student_name'),
                AttendanceLog.check_state.label('status'),
                AttendanceLog.check_time.label('checkin_time')) \
            .join(StudentCourse, Student.student_id == StudentCourse.student_id) \
            .join(AttendanceLog, (Student.student_id == AttendanceLog.student_id) & (StudentCourse.course_id == AttendanceLog.course_id)) \
            .filter(StudentCourse.course_id == course_id,
                db.func.date(AttendanceLog.check_time) == datetime.strptime(checkin_date, '%Y-%m-%d').date())
            
            records = query.all()
            if not records:
                return jsonify({'status': False, 'message': '没有找到考勤记录，无法导出。'})
            
            df = pd.DataFrame(records, columns=['学号', '姓名', '状态', '签到时间'])
            df['状态'] = df['状态'].map(status_map)
            
            sheet_name = '考勤记录'
            column_widths = {'A:A': 15, 'B:B': 10, 'C:C': 10, 'D:D': 20}
            
        else:
            # 全部日期导出
            students_query = db.session.query(Student.student_id, Student.name) \
            .join(StudentCourse, Student.student_id == StudentCourse.student_id) \
            .filter(StudentCourse.course_id == course_id) \
            .order_by(Student.student_id)
            
            students = students_query.all()
            if not students:
                return jsonify({'status': False, 'message': '该课程没有学生，无法导出。'})
            
            # 获取所有考勤记录
            records_query = db.session.query(
                Student.student_id,
                Student.name.label('student_name'),
                AttendanceLog.check_state.label('status'),
                db.func.date(AttendanceLog.check_time).label('check_date')) \
                .join(StudentCourse, Student.student_id == StudentCourse.student_id) \
                .join(AttendanceLog, (Student.student_id == AttendanceLog.student_id) & (StudentCourse.course_id == AttendanceLog.course_id)) \
                .filter(StudentCourse.course_id == course_id)
            
            records = records_query.all()
            
            # 获取统计数据
            stats_query = db.session.query(Student.student_id,AttendanceCount.actual_count,
                AttendanceCount.need_count) \
            .join(StudentCourse, Student.student_id == StudentCourse.student_id) \
            .outerjoin(AttendanceCount, (Student.student_id == AttendanceCount.student_id) & (AttendanceCount.course_id == course_id)) \
            .filter(StudentCourse.course_id == course_id)
            
            stats = {row.student_id: (row.actual_count or 0, row.need_count or 0) for row in stats_query.all()}
            
            df_base = pd.DataFrame(students, columns=['学号', '姓名'])
            
            if records:
                # 处理考勤记录
                df_records = pd.DataFrame(records, columns=['学号', '姓名', '状态', '日期'])
                df_records['状态'] = df_records['状态'].map(status_map)
                df_records['日期'] = df_records['日期'].astype(str)
                
                # 创建透视表
                pivot_df = df_records.pivot_table(
                    index=['学号', '姓名'], 
                    columns='日期', 
                    values='状态', 
                    aggfunc='first',
                    fill_value=''
                )
                
                # 重置索引并合并
                pivot_df = pivot_df.reset_index()
                df = pivot_df
            else:
                df = df_base
            
            # 添加统计列
            df['实签次数'] = df['学号'].map(lambda x: stats.get(x, (0, 0))[0])
            df['应签次数'] = df['学号'].map(lambda x: stats.get(x, (0, 0))[1])
            
            sheet_name = '考勤汇总'
            # 动态设置列宽
            column_widths = {'A:A': 15, 'B:B': 10}
            date_columns = [col for col in df.columns if col not in ['学号', '姓名', '实签次数', '应签次数']]
            for i, col in enumerate(date_columns, start=2):
                column_widths[f'{chr(67+i)}:{chr(67+i)}'] = 12
            # 统计列
            stats_start = chr(67 + len(date_columns))
            column_widths[f'{stats_start}:{stats_start}'] = 10
            stats_start = chr(68 + len(date_columns))
            column_widths[f'{stats_start}:{stats_start}'] = 10
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # 设置列宽
            for col_range, width in column_widths.items():
                worksheet.set_column(col_range, width)
        
        output.seek(0)
        
        # 生成文件名
        date_suffix = checkin_date if checkin_date != '全部日期' else '全部日期汇总'
        filename = f"{course.course_name}_考勤记录_{date_suffix}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"导出Excel失败: {str(e)}")
        return jsonify({'status': False, 'message': '导出失败'})


# ==========================================  管理员端相关接口 ========================================

# 验证是否上传文件
def validate_excel_file():
    if 'file' not in request.files:
        return None, {'status': False, 'message': '没有上传文件'}
    
    file = request.files['file']
    if file.filename == '':
        return None, {'status': False, 'message': '没有选择文件'}
    
    if not file.filename.endswith('.xlsx'):
        return None, {'status': False, 'message': '请上传Excel文件(.xlsx)'}
    
    return file, None

def clean_excel_data(value):
    if pd.isna(value):
        return None if value is None else ''
    return str(value).replace('_x000d_', '').strip()

def process_date_field(date_value):
    if pd.isna(date_value):
        return None
    try:
        return pd.to_datetime(date_value).strftime('%Y-%m-%d')
    except ValueError:
        return None

def build_import_response(success_count, error_count, error_messages):
    return jsonify({
        'status': True,
        'message': f'导入完成。成功: {success_count}条, 失败: {error_count}条',
        'errors': error_messages if error_messages else None
    })

# 导入用户账号信息
@app.route('/admin/import/users', methods=['POST'])
def import_users():
    file, error = validate_excel_file()
    if error:
        return jsonify(error)
    
    try:
        df = pd.read_excel(file)
        
        required_columns = ['用户ID', '密码', '用户类型']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'status': False,
                'message': f'Excel文件缺少必要的列: {", ".join(missing_columns)}'
            })
        
        success_count, error_count, error_messages = 0, 0, []
        allowed_user_types = ['student', 'teacher', 'admin']
        
        for _, row in df.iterrows():
            try:
                user_id = clean_excel_data(row['用户ID'])
                password = str(row['密码']).strip()
                user_type = str(row['用户类型']).strip()
                
                if not user_id:
                    error_count += 1
                    error_messages.append("用户ID为空或无效，跳过该行")
                    continue
                
                if not password:
                    error_count += 1
                    error_messages.append(f"用户ID {user_id} 的密码为空或无效，跳过该行")
                    continue
                
                if user_type not in allowed_user_types:
                    error_count += 1
                    error_messages.append(f"用户ID {user_id} 的用户类型 '{user_type}' 无效，跳过该行。允许的类型: {{{', '.join(allowed_user_types)}}}")
                    continue
                
                # 加密密码
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                user = User.query.filter_by(user_id=user_id).first()
                if user:
                    # 更新现有用户信息
                    user.password = hashed_password
                    user.user_type = user_type
                else:
                    # 创建新用户
                    new_user = User(
                        user_id=user_id,
                        password=hashed_password,
                        user_type=user_type
                    )
                    db.session.add(new_user)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                error_messages.append(f"处理用户 {row.get('用户ID', 'N/A')} 时出错: {str(e)}")
        
        db.session.commit()
        return build_import_response(success_count, error_count, error_messages)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'导入失败: {str(e)}'})


# 导入学生信息
@app.route('/admin/import/students', methods=['POST'])
def import_students():
    file, error = validate_excel_file()
    if error:
        return jsonify(error)
    
    try:
        df = pd.read_excel(file)
        
        required_columns = ['学号', '姓名', '性别', '院系', '年级', '专业', '出生日期']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'status': False,
                'message': f'Excel文件缺少必要的列: {", ".join(missing_columns)}'
            })
        
        success_count, error_count, error_messages = 0, 0, []
        
        for _, row in df.iterrows():
            try:
                student_id = clean_excel_data(row['学号'])
                if not student_id:
                    error_count += 1
                    error_messages.append("学号为空或无效，跳过该行")
                    continue
                
                major = clean_excel_data(row.get('专业', ''))
                birthday = process_date_field(row.get('出生日期'))
                
                student = Student.query.filter_by(student_id=student_id).first()
                if student:
                    # 更新现有学生信息
                    student.name = row['姓名']
                    student.gender = row['性别']
                    student.department = row['院系']
                    student.grade = str(row['年级'])
                    student.major = major
                    student.birthday = birthday
                else:
                    # 创建新学生
                    student = Student(
                        student_id=student_id,
                        name=row['姓名'],
                        gender=row['性别'],
                        department=row['院系'],
                        major=major,
                        grade=str(row['年级']),
                        birthday=birthday
                    )
                    db.session.add(student)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                error_messages.append(f"学号 {row.get('学号', 'N/A')}: {str(e)}")
        
        db.session.commit()
        return build_import_response(success_count, error_count, error_messages)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'导入失败: {str(e)}'})


# 导入教师信息
@app.route('/admin/import/teachers', methods=['POST'])
def import_teachers():
    file, error = validate_excel_file()
    if error:
        return jsonify(error)
    
    try:
        df = pd.read_excel(file)
        
        required_columns = ['工号', '姓名', '性别', '院系', '职称', '出生日期']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'status': False,
                'message': f'Excel文件缺少必要的列: {", ".join(missing_columns)}'
            })
        
        success_count, error_count, error_messages = 0, 0, []
        
        for _, row in df.iterrows():
            try:
                teacher_id = clean_excel_data(row['工号'])
                if not teacher_id:
                    error_count += 1
                    error_messages.append("工号为空或无效，跳过该行")
                    continue
                
                title = clean_excel_data(row.get('职称', ''))
                birthday = process_date_field(row.get('出生日期'))
                
                teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
                if teacher:
                    # 更新现有教师信息
                    teacher.name = row['姓名']
                    teacher.gender = row['性别']
                    teacher.department = row['院系']
                    teacher.title = title
                    teacher.birthday = birthday
                else:
                    # 创建新教师
                    teacher = Teacher(
                        teacher_id=teacher_id,
                        name=row['姓名'],
                        gender=row['性别'],
                        department=row['院系'],
                        title=title,
                        birthday=birthday
                    )
                    db.session.add(teacher)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                error_messages.append(f"工号 {row.get('工号', 'N/A')}: {str(e)}")
        
        db.session.commit()
        return build_import_response(success_count, error_count, error_messages)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'导入失败: {str(e)}'})


# 导入课程信息
@app.route('/admin/import/courses', methods=['POST'])
def import_courses():
    file, error = validate_excel_file()
    if error:
        return jsonify(error)
    
    try:
        df = pd.read_excel(file)
        
        required_columns = ['课程编号', '课程名称', '教师工号', '上课时间', '上课地点', '学分', '院系']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'status': False,
                'message': f'Excel文件缺少必要的列: {", ".join(missing_columns)}'
            })
        
        success_count, error_count, error_messages = 0, 0, []
        
        for _, row in df.iterrows():
            try:
                course_id = clean_excel_data(row['课程编号'])
                teacher_id = clean_excel_data(row['教师工号'])
                
                if not course_id:
                    error_count += 1
                    error_messages.append("课程编号为空或无效，跳过该行")
                    continue
                
                if not teacher_id:
                    error_count += 1
                    error_messages.append("教师工号为空或无效，跳过该行")
                    continue
                
                credit = row.get('学分', 0) if not pd.isna(row.get('学分', 0)) else 0
                department = clean_excel_data(row.get('院系', ''))
                
                course = Course.query.filter_by(course_id=course_id).first()
                if course:
                    # 更新现有课程信息
                    course.course_name = row['课程名称']
                    course.teacher_id = teacher_id
                    course.course_time = row['上课时间']
                    course.course_location = row['上课地点']
                    course.credit = credit
                    course.department = department
                else:
                    # 创建新课程
                    course = Course(
                        course_id=course_id,
                        course_name=row['课程名称'],
                        teacher_id=teacher_id,
                        course_time=row['上课时间'],
                        course_location=row['上课地点'],
                        credit=credit,
                        department=department
                    )
                    db.session.add(course)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                error_messages.append(f"课程编号 {row.get('课程编号', 'N/A')}: {str(e)}")
        
        db.session.commit()
        return build_import_response(success_count, error_count, error_messages)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'导入失败: {str(e)}'})


# 导入学生选课表
@app.route('/admin/import/student_courses', methods=['POST'])
def import_student_courses():
    file, error = validate_excel_file()
    if error:
        return jsonify(error)
    
    try:
        df = pd.read_excel(file)
        
        required_columns = ['学号', '课程编号']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                'status': False,
                'message': f'Excel文件缺少必要的列: {", ".join(missing_columns)}'
            })
        
        success_count, error_count, error_messages = 0, 0, []
        
        for _, row in df.iterrows():
            try:
                student_id = clean_excel_data(row['学号'])
                course_id = clean_excel_data(row['课程编号'])
                
                if not student_id:
                    error_count += 1
                    error_messages.append("学号为空或无效，跳过该行")
                    continue
                
                if not course_id:
                    error_count += 1
                    error_messages.append("课程编号为空或无效，跳过该行")
                    continue
                
                # 验证学生和课程存在性
                if not Student.query.filter_by(student_id=student_id).first():
                    error_count += 1
                    error_messages.append(f"学号 {student_id} 不存在，跳过该行")
                    continue
                
                if not Course.query.filter_by(course_id=course_id).first():
                    error_count += 1
                    error_messages.append(f"课程编号 {course_id} 不存在，跳过该行")
                    continue
                
                # 检查选课关系是否已存在
                if not StudentCourse.query.filter_by(student_id=student_id, course_id=course_id).first():
                    new_student_course = StudentCourse(student_id=student_id, course_id=course_id)
                    db.session.add(new_student_course)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                error_messages.append(f"处理学生 {row.get('学号', 'N/A')}, 课程 {row.get('课程编号', 'N/A')} 时出错: {str(e)}")
        
        db.session.commit()
        return build_import_response(success_count, error_count, error_messages)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'导入失败: {str(e)}'})


# 导出考勤记录
@app.route('/admin/attendance/export', methods=['GET'])
def export_admin_attendance():
    teacher_id = request.args.get('teacher_id')
    course_id = request.args.get('course_id')
    checkin_date = request.args.get('checkin_date')
    
    try:
        # 构建基础查询
        query = (db.session.query(
            AttendanceLog.log_id,
            Student.student_id,
            Student.name.label('student_name'),
            Course.course_id,
            Course.course_name,
            Teacher.teacher_id,
            Teacher.name.label('teacher_name'),
            AttendanceLog.check_time,
            AttendanceLog.check_state,
            AttendanceLog.location.label('checkin_location')
        ).join(Student, AttendanceLog.student_id == Student.student_id)
        .join(Course, AttendanceLog.course_id == Course.course_id)
        .join(Teacher, Course.teacher_id == Teacher.teacher_id))
        
        # 根据参数添加筛选条件
        if teacher_id and teacher_id != 'ALL':
            query = query.filter(Teacher.teacher_id == teacher_id)
        
        if course_id and course_id != 'ALL':
            query = query.filter(Course.course_id == course_id)
        
        if checkin_date and checkin_date != 'ALL':
            query = query.filter(db.func.date(AttendanceLog.check_time) == datetime.strptime(checkin_date, '%Y-%m-%d').date())
        
        records = query.all()
        
        if not records:
            return jsonify({'status': False, 'message': '没有找到符合条件的考勤记录，无法导出。'})
        
        # 创建DataFrame
        df = pd.DataFrame(records, columns=[
            '记录ID', '学号', '学生姓名', '课程编号', '课程名称', '教师工号', '教师姓名', '签到时间', '签到状态', '签到地点'
        ])
        
        # 将状态转换为中文
        status_map = {
            'checked': '出勤',
            'leave': '请假',
            'absent': '缺勤'
        }
        df['签到状态'] = df['签到状态'].map(status_map)
        df['签到时间'] = df['签到时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['签到地点'] = df['签到地点'].apply(lambda x: '是' if x else '否')
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='管理员考勤记录', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['管理员考勤记录']
            
            # 设置列宽
            column_widths = [8, 15, 15, 15, 20, 15, 15, 20, 10, 10]
            for i, width in enumerate(column_widths):
                worksheet.set_column(i, i, width)
        
        output.seek(0)
        filename = "管理员考勤记录_导出.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"管理员导出Excel失败: {str(e)}")
        return jsonify({'status': False, 'message': '导出失败'})


# 获取所有教师列表
@app.route('/admin/teachers', methods=['GET'])
def get_all_teachers():
    try:
        teachers = Teacher.query.with_entities(Teacher.teacher_id, Teacher.name).all()
        teacher_list = [{'teacher_id': t.teacher_id, 'name': t.name} for t in teachers]
        return jsonify({'status': True, 'data': teacher_list})
    except Exception as e:
        return jsonify({'status': False, 'message': f'获取教师列表失败: {str(e)}'})


# 获取所有课程列表
@app.route('/admin/courses', methods=['GET'])
def get_all_courses():
    try:
        courses = Course.query.with_entities(Course.course_id, Course.course_name).all()
        course_list = [{'course_id': c.course_id, 'course_name': c.course_name} for c in courses]
        return jsonify({'status': True, 'data': course_list})
    except Exception as e:
        return jsonify({'status': False, 'message': f'获取课程列表失败: {str(e)}'})


# 获取所有考勤日期
@app.route('/admin/attendance/all_dates', methods=['GET'])
def get_all_attendance_dates():
    try:
        dates = db.session.query(db.func.distinct(db.func.date(AttendanceLog.check_time))).all()
        # 格式化日期为字符串，并转换为列表
        date_list = [d[0].strftime('%Y-%m-%d') for d in dates if d[0] is not None]
        # 按照日期排序
        date_list.sort()
        return jsonify({'status': True, 'data': date_list})
    except Exception as e:
        return jsonify({'status': False, 'message': f'获取所有考勤日期失败: {str(e)}'})

# ======================================== 管理员修改和删除数据接口 ========================================

# 获取学生、教师或课程信息的接口
@app.route('/admin/get_info', methods=['POST'])
def get_admin_info():
    data = request.get_json()
    item_id = data.get('id')
    item_type = data.get('type') # 'student', 'teacher', 'course'

    if not item_id or not item_type:
        return jsonify({'status': False, 'message': 'ID和类型不能为空'})

    info = {}
    if item_type == 'student':
        student = Student.query.filter_by(student_id=item_id).first()
        if student:
            info = {
                'student_id': student.student_id,
                'name': student.name,
                'gender': student.gender,
                'department': student.department,
                'major': student.major,
                'grade': student.grade,
                'birthday': student.birthday.strftime('%Y-%m-%d') if student.birthday else None
            }
    elif item_type == 'teacher':
        teacher = Teacher.query.filter_by(teacher_id=item_id).first()
        if teacher:
            info = {
                'teacher_id': teacher.teacher_id,
                'name': teacher.name,
                'gender': teacher.gender,
                'department': teacher.department,
                'title': teacher.title,
                'birthday': teacher.birthday.strftime('%Y-%m-%d') if teacher.birthday else None
            }
    elif item_type == 'course':
        course = Course.query.filter_by(course_id=item_id).first()
        if course:
            info = {
                'course_id': course.course_id,
                'course_name': course.course_name,
                'credit': course.credit,
                'teacher_id': course.teacher_id,
                'department': course.department,
                'course_time': course.course_time,
                'course_location': course.course_location
            }
    else:
        return jsonify({'status': False, 'message': '无效的类型'})

    if info:
        return jsonify({'status': True, 'data': info})
    else:
        return jsonify({'status': False, 'message': '未找到相关信息'})


# 修改学生信息的接口
@app.route('/admin/update_student', methods=['POST'])
def update_student():
    data = request.get_json()
    student_id = data.get('student_id')
    
    if not student_id:
        return jsonify({'status': False, 'message': '学生ID不能为空'})

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({'status': False, 'message': '学生不存在'})

    try:
        if 'name' in data: 
            if data['name'] == '':
                return jsonify({'status': False, 'message': '姓名不能为空'})
            student.name = data['name']
        if 'gender' in data:
            if data['gender'] not in ['男', '女']:
                return jsonify({'status': False, 'message': '性别只能为男或女'})
            student.gender = data['gender']
        if 'department' in data:
            if data['department'] == '':
                return jsonify({'status': False, 'message': '院系不能为空'})
            student.department = data['department']
        if 'major' in data:
            if data['major'] == '':
                return jsonify({'status': False, 'message': '专业不能为空'})
            student.major = data['major']
        if 'grade' in data:
            if data['grade'] == '':
                return jsonify({'status': False, 'message': '年级不能为空'})
            if not data['grade'].isdigit() or int(data['grade']) < 1905:
                return jsonify({'status': False, 'message': '年级必须为数字，且必须在1905之后'})
            student.grade = data['grade']
        if 'birthday' in data: 
            if data['birthday'] == '':
                return jsonify({'status': False, 'message': '生日不能为空'})
            re_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
            if not re_pattern.match(data['birthday']):
                return jsonify({'status': False, 'message': '生日格式错误'})
            student.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date() if data['birthday'] else None

        db.session.commit()
        return jsonify({'status': True, 'message': '学生信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'更新失败: {str(e)}'})


# 修改教师信息的接口
@app.route('/admin/update_teacher', methods=['POST'])
def update_teacher():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    
    if not teacher_id:
        return jsonify({'status': False, 'message': '教师ID不能为空'})

    teacher = Teacher.query.filter_by(teacher_id=teacher_id).first()
    if not teacher:
        return jsonify({'status': False, 'message': '教师不存在'})

    try:
        if 'name' in data:
            if data['name'] == '':
                return jsonify({'status': False, 'message': '姓名不能为空'})
            teacher.name = data['name']
        if 'gender' in data:
            if data['gender'] not in ['男', '女']:
                return jsonify({'status': False, 'message': '性别只能为男或女'})
            teacher.gender = data['gender']
        if 'department' in data:
            if data['department'] == '':
                return jsonify({'status': False, 'message': '院系不能为空'})
            teacher.department = data['department']
        if 'title' in data:
            if data['title'] == '':
                return jsonify({'status': False, 'message': '职称不能为空'})
            teacher.title = data['title']
        if 'birthday' in data: 
            if data['birthday'] == '':
                return jsonify({'status': False, 'message': '生日不能为空'})
            re_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
            if not re_pattern.match(data['birthday']):
                return jsonify({'status': False, 'message': '生日格式错误'})
            teacher.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date() if data['birthday'] else None

        db.session.commit()
        return jsonify({'status': True, 'message': '教师信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'更新失败: {str(e)}'})


# 修改课程信息的接口
@app.route('/admin/update_course', methods=['POST'])
def update_course():
    data = request.get_json()
    course_id = data.get('course_id')
    
    if not course_id:
        return jsonify({'status': False, 'message': '课程ID不能为空'})

    course = Course.query.filter_by(course_id=course_id).first()
    if not course:
        return jsonify({'status': False, 'message': '课程不存在'})

    try:
        if 'course_name' in data:
            if data['course_name'] == '':
                return jsonify({'status': False, 'message': '课程名称不能为空'})
            course.course_name = data['course_name']
        if 'credit' in data:
            if data['credit'] == '':
                return jsonify({'status': False, 'message': '学分不能为空'})
            if not str(data['credit']).isdigit():
                return jsonify({'status': False, 'message': '学分必须为数字'})
            course.credit = int(data['credit'])
        if 'teacher_id' in data:
            if data['teacher_id'] == '':
                return jsonify({'status': False, 'message': '教师ID不能为空'})
            if not Teacher.query.filter_by(teacher_id=data['teacher_id']).first():
                return jsonify({'status': False, 'message': '教师不存在'})
            course.teacher_id = data['teacher_id']
        if 'department' in data:
            if data['department'] == '':
                return jsonify({'status': False, 'message': '开课院系不能为空'})
            course.department = data['department']
        if 'course_time' in data:
            if data['course_time'] == '':
                return jsonify({'status': False, 'message': '上课时间不能为空'})
            # 验证时间格式例如周一 10:00-12:00
            re_pattern = re.compile(r'^[一二三四五六日]\s+\d{1,2}:\d{2}-\d{1,2}:\d{2}$')
            if not re_pattern.match(data['course_time']):
                return jsonify({'status': False, 'message': '上课时间格式错误'})
            course.course_time = data['course_time']
        if 'course_location' in data:
            if data['course_location'] == '':
                return jsonify({'status': False, 'message': '上课地点不能为空'})
            course.course_location = data['course_location']

        db.session.commit()
        return jsonify({'status': True, 'message': '课程信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'更新失败: {str(e)}'})


# 删除学生相关数据
@app.route('/admin/delete_student', methods=['POST'])
def delete_student():
    data = request.get_json()
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'status': False, 'message': '学生ID不能为空'})
    
    if not Student.query.filter_by(student_id=student_id).first():
        return jsonify({'status': False, 'message': '学生不存在'})
    
    try:
        # 删除所有相关子表记录
        AttendanceLog.query.filter_by(student_id=student_id).delete()
        StudentCourse.query.filter_by(student_id=student_id).delete()
        AttendanceCount.query.filter_by(student_id=student_id).delete()
        
        # 删除学生记录
        Student.query.filter_by(student_id=student_id).delete()
        
        # 删除用户记录
        User.query.filter_by(user_id=student_id).delete()

        db.session.commit()
        return jsonify({'status': True, 'message': '学生信息删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'删除失败: {str(e)}'})


# 删除教师相关数据
@app.route('/admin/delete_teacher', methods=['POST'])
def delete_teacher():
    data = request.get_json()
    teacher_id = data.get('teacher_id')

    if not teacher_id:
        return jsonify({'status': False, 'message': '教师ID不能为空'})
    
    if not Teacher.query.filter_by(teacher_id=teacher_id).first():
        return jsonify({'status': False, 'message': '教师不存在'})
    
    try:
        # 获取该教师的所有课程ID
        course_ids = [c.course_id for c in Course.query.filter_by(teacher_id=teacher_id).all()]
        
        # 删除所有课程相关的子表记录
        for course_id in course_ids:
            AttendanceLog.query.filter_by(course_id=course_id).delete()
            StudentCourse.query.filter_by(course_id=course_id).delete()
            AttendanceCount.query.filter_by(course_id=course_id).delete()
            AttendanceRequirement.query.filter_by(course_id=course_id).delete()
        
        # 删除教师的所有课程
        Course.query.filter_by(teacher_id=teacher_id).delete()
        
        # 删除教师记录
        Teacher.query.filter_by(teacher_id=teacher_id).delete()
        
        # 删除用户记录
        User.query.filter_by(user_id=teacher_id).delete()

        db.session.commit()
        return jsonify({'status': True, 'message': '教师信息删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'删除失败: {str(e)}'})


# 删除课程信息的接口
@app.route('/admin/delete_course', methods=['POST'])
def delete_course():
    data = request.get_json()
    course_id = data.get('course_id')

    if not course_id:
        return jsonify({'status': False, 'message': '课程ID不能为空'})
    
    course = Course.query.filter_by(course_id=course_id).first()
    if not course:
        return jsonify({'status': False, 'message': '课程不存在'})
    
    try:
        with db.session.no_autoflush:
            # 按外键约束顺序删除引用course_id的子表记录
            AttendanceLog.query.filter_by(course_id=course_id).delete()
            StudentCourse.query.filter_by(course_id=course_id).delete()
            AttendanceCount.query.filter_by(course_id=course_id).delete()
            AttendanceRequirement.query.filter_by(course_id=course_id).delete()
            
            # 删除课程记录
            db.session.delete(course)

        db.session.commit()
        return jsonify({'status': True, 'message': '课程信息删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'删除失败: {str(e)}'})

# ======================================== 管理员批量删除相关接口 ========================================

# 按年级删除学生
@app.route('/admin/delete_students_by_grade', methods=['POST'])
def delete_students_by_grade():
    data = request.get_json()
    grade = data.get('grade')

    if not grade:
        return jsonify({'status': False, 'message': '年级不能为空'})
    
    students = Student.query.filter_by(grade=grade).all()
    if not students:
        return jsonify({'status': False, 'message': '该年级没有学生'})
    
    try:
        student_ids = [s.student_id for s in students]
        
        # 删除相关子表记录
        for student_id in student_ids:
            AttendanceLog.query.filter_by(student_id=student_id).delete()
            StudentCourse.query.filter_by(student_id=student_id).delete()
            AttendanceCount.query.filter_by(student_id=student_id).delete()
        
        # 删除学生和用户记录
        Student.query.filter_by(grade=grade).delete()
        User.query.filter(User.user_id.in_(student_ids)).delete()

        db.session.commit()
        return jsonify({'status': True, 'message': f'成功删除{len(student_ids)}名学生'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'删除失败: {str(e)}'})


# 删除所有教师
@app.route('/admin/delete_all_teachers', methods=['POST'])
def delete_all_teachers():
    try:
        # 获取所有教师和课程ID
        teachers = Teacher.query.all()
        teacher_ids = [t.teacher_id for t in teachers]
        course_ids = [c.course_id for c in Course.query.all()]
        
        if not teachers:
            return jsonify({'status': False, 'message': '没有教师数据'})
        
        # 删除所有课程相关子表记录
        for course_id in course_ids:
            AttendanceLog.query.filter_by(course_id=course_id).delete()
            StudentCourse.query.filter_by(course_id=course_id).delete()
            AttendanceCount.query.filter_by(course_id=course_id).delete()
            AttendanceRequirement.query.filter_by(course_id=course_id).delete()
        
        # 删除所有课程、教师和用户记录
        Course.query.delete()
        Teacher.query.delete()
        User.query.filter(User.user_id.in_(teacher_ids)).delete()

        db.session.commit()
        return jsonify({'status': True, 'message': f'成功删除{len(teacher_ids)}名教师及相关课程'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'删除失败: {str(e)}'})


# 删除所有课程
@app.route('/admin/delete_all_courses', methods=['POST'])
def delete_all_courses():
    try:
        course_ids = [c.course_id for c in Course.query.all()]
        
        if not course_ids:
            return jsonify({'status': False, 'message': '没有课程数据'})
        
        # 删除所有课程相关子表记录
        for course_id in course_ids:
            AttendanceLog.query.filter_by(course_id=course_id).delete()
            StudentCourse.query.filter_by(course_id=course_id).delete()
            AttendanceCount.query.filter_by(course_id=course_id).delete()
            AttendanceRequirement.query.filter_by(course_id=course_id).delete()
        
        # 删除所有课程
        Course.query.delete()

        db.session.commit()
        return jsonify({'status': True, 'message': f'成功删除{len(course_ids)}门课程'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'删除失败: {str(e)}'})


# 清空选课表
@app.route('/admin/delete_all_student_courses', methods=['POST'])
def delete_all_student_courses():
    try:
        count = StudentCourse.query.count()
        
        if count == 0:
            return jsonify({'status': False, 'message': '选课表已为空'})
        
        StudentCourse.query.delete()
        db.session.commit()
        return jsonify({'status': True, 'message': f'成功清空选课表，删除{count}条记录'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'清空失败: {str(e)}'})


# 清空考勤记录
@app.route('/admin/delete_all_attendance_records', methods=['POST'])
def delete_all_attendance_records():
    try:
        log_count = AttendanceLog.query.count()
        count_count = AttendanceCount.query.count()
        requirement_count = AttendanceRequirement.query.count()
        
        if log_count == 0 and count_count == 0 and requirement_count == 0:
            return jsonify({'status': False, 'message': '考勤相关表已为空'})
        
        # 清空考勤相关所有表
        AttendanceLog.query.delete()
        AttendanceCount.query.delete()
        AttendanceRequirement.query.delete()
        
        db.session.commit()
        total_count = log_count + count_count + requirement_count
        return jsonify({'status': True, 'message': f'成功清空考勤记录，删除{total_count}条记录'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': False, 'message': f'清空失败: {str(e)}'})


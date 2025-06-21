from init import db

# 定义数据库模型，用于ORM映射
# 用户表
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(60), nullable=False)
    user_type = db.Column(db.Enum('student', 'teacher', 'admin'), nullable=False)

# 学生表
class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.String(20), db.ForeignKey('user.user_id'), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('男', '女'), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    major = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(10), nullable=False)
    birthday = db.Column(db.Date)

# 教师表
class Teacher(db.Model):
    __tablename__ = 'teacher'
    teacher_id = db.Column(db.String(20), db.ForeignKey('user.user_id'), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.Enum('男', '女'), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.Date)

# 课程表
class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.String(20), primary_key=True)
    course_name = db.Column(db.String(50), nullable=False)
    credit = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.String(20), db.ForeignKey('teacher.teacher_id'), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    course_time = db.Column(db.String(50), nullable=False)
    course_location = db.Column(db.String(50), nullable=False)

# 学生选课表
class StudentCourse(db.Model):
    __tablename__ = 'student_course'
    student_id = db.Column(db.String(20), db.ForeignKey('student.student_id'), primary_key=True)
    course_id = db.Column(db.String(20), db.ForeignKey('course.course_id'), primary_key=True)

# 考勤记录表
class AttendanceLog(db.Model):
    __tablename__ = 'attendance_log'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.String(20), db.ForeignKey('course.course_id'), nullable=False)
    check_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.Boolean, nullable=False)
    check_state = db.Column(db.Enum('checked', 'absent', 'leave'), nullable=False)

# 签到要求表
class AttendanceRequirement(db.Model):
    __tablename__ = 'attendance_requirement'
    course_id = db.Column(db.String(20), db.ForeignKey('course.course_id'), primary_key=True)
    check_date = db.Column(db.Date, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.Boolean, default=None)

# 考勤统计表
class AttendanceCount(db.Model):
    __tablename__ = 'attendance_count'
    student_id = db.Column(db.String(20), db.ForeignKey('student.student_id'), primary_key=True)
    course_id = db.Column(db.String(20), db.ForeignKey('course.course_id'), primary_key=True)
    actual_count = db.Column(db.Integer, nullable=False, default=0)
    need_count = db.Column(db.Integer, nullable=False, default=0)
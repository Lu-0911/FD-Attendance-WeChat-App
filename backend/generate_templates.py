import pandas as pd
import os

def generate_teacher_template():
    # 创建教师信息模板
    data = {
        '工号': ['T2024001', 'T2024002', 'T2024003'],
        '姓名': ['张三', '李四', '王五'],
        '性别': ['男', '女', '男'],
        '院系': ['计算机学院', '数学学院', '物理学院']
    }
    
    df = pd.DataFrame(data)
    
    # 创建templates目录（如果不存在）
    os.makedirs('static/templates', exist_ok=True)
    
    # 保存为Excel文件
    output_path = 'static/templates/教师信息导入模板.xlsx'
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='教师信息', index=False)
        
        # 获取workbook和worksheet对象
        workbook = writer.book
        worksheet = writer.sheets['教师信息']
        
        # 设置列宽
        worksheet.set_column('A:A', 15)  # 工号
        worksheet.set_column('B:B', 10)  # 姓名
        worksheet.set_column('C:C', 10)  # 性别
        worksheet.set_column('D:D', 20)  # 院系
        
        # 添加说明
        worksheet.write('F2', '说明：')
        worksheet.write('F3', '1. 工号：教师工号，必填')
        worksheet.write('F4', '2. 姓名：教师姓名，必填')
        worksheet.write('F5', '3. 性别：男/女，必填')
        worksheet.write('F6', '4. 院系：所属院系，必填')
        
    print(f"教师信息模板已生成：{output_path}")

def generate_course_template():
    # 创建课程信息模板
    data = {
        '课程编号': ['C2024001', 'C2024002', 'C2024003'],
        '课程名称': ['高等数学', '大学物理', '程序设计'],
        '教师工号': ['T2024001', 'T2024002', 'T2024003'],
        '上课时间': ['周一 1-2节', '周二 3-4节', '周三 5-6节'],
        '上课地点': ['教学楼A101', '教学楼B203', '教学楼C305']
    }
    
    df = pd.DataFrame(data)
    
    # 创建templates目录（如果不存在）
    os.makedirs('static/templates', exist_ok=True)
    
    # 保存为Excel文件
    output_path = 'static/templates/课程信息导入模板.xlsx'
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='课程信息', index=False)
        
        # 获取workbook和worksheet对象
        workbook = writer.book
        worksheet = writer.sheets['课程信息']
        
        # 设置列宽
        worksheet.set_column('A:A', 15)  # 课程编号
        worksheet.set_column('B:B', 20)  # 课程名称
        worksheet.set_column('C:C', 15)  # 教师工号
        worksheet.set_column('D:D', 20)  # 上课时间
        worksheet.set_column('E:E', 20)  # 上课地点
        
        # 添加说明
        worksheet.write('G2', '说明：')
        worksheet.write('G3', '1. 课程编号：课程唯一标识，必填')
        worksheet.write('G4', '2. 课程名称：课程名称，必填')
        worksheet.write('G5', '3. 教师工号：授课教师工号，必填')
        worksheet.write('G6', '4. 上课时间：格式如"周一 1-2节"，必填')
        worksheet.write('G7', '5. 上课地点：教室位置，必填')
        
    print(f"课程信息模板已生成：{output_path}")

def generate_student_course_template():
    # 创建学生课程表模板
    data = {
        '学号': ['S2024001', 'S2024001', 'S2024002'],
        '课程编号': ['C2024001', 'C2024002', 'C2024001']
    }
    
    df = pd.DataFrame(data)
    
    # 创建templates目录（如果不存在）
    os.makedirs('static/templates', exist_ok=True)
    
    # 保存为Excel文件
    output_path = 'static/templates/学生课程表导入模板.xlsx'
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='学生课程表', index=False)
        
        # 获取workbook和worksheet对象
        workbook = writer.book
        worksheet = writer.sheets['学生课程表']
        
        # 设置列宽
        worksheet.set_column('A:A', 15)  # 学号
        worksheet.set_column('B:B', 15)  # 课程编号
        
        # 添加说明
        worksheet.write('D2', '说明：')
        worksheet.write('D3', '1. 学号：学生学号，必填')
        worksheet.write('D4', '2. 课程编号：课程编号，必填')
        worksheet.write('D5', '注意：学号和课程编号必须已存在于系统中。')
        
    print(f"学生课程表模板已生成：{output_path}")

def generate_user_template():
    # 创建用户信息模板
    data = {
        '用户ID': ['admin001', 'T2024001', 'S2024001'],
        '密码': ['adminpass', 'teacherpass', 'studentpass'],
        '用户类型': ['admin', 'teacher', 'student']
    }
    
    df = pd.DataFrame(data)
    
    # 创建templates目录（如果不存在）
    os.makedirs('static/templates', exist_ok=True)
    
    # 保存为Excel文件
    output_path = 'static/templates/用户信息导入模板.xlsx'
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='用户信息', index=False)
        
        # 获取workbook和worksheet对象
        workbook = writer.book
        worksheet = writer.sheets['用户信息']
        
        # 设置列宽
        worksheet.set_column('A:A', 15)  # 用户ID
        worksheet.set_column('B:B', 15)  # 密码
        worksheet.set_column('C:C', 15)  # 用户类型
        
        # 添加说明
        worksheet.write('E2', '说明：')
        worksheet.write('E3', '1. 用户ID：用户唯一标识，必填')
        worksheet.write('E4', '2. 密码：用户密码，必填')
        worksheet.write('E5', '3. 用户类型：必填，只能是 student, teacher 或 admin')
        
    print(f"用户信息模板已生成：{output_path}")

if __name__ == '__main__':
    generate_teacher_template()
    generate_course_template()
    generate_student_course_template()
    generate_user_template() 
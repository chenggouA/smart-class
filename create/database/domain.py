from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, ForeignKey
from datetime import datetime
from sqlalchemy import text

db = SQLAlchemy()

# 行为记录表

db = SQLAlchemy()

# 行为记录表
class HautActionRecord(db.Model):
    __tablename__ = 'haut_action_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_url = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)

# 教师发布签到的表
class HautSign(db.Model):
    __tablename__ = 'haut_sign'
    signID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    courseID = db.Column(db.Integer, ForeignKey("haut_courses.CourseID"))
    createTime = db.Column(db.DateTime, server_default=db.func.now())
    signEndTime = db.Column(db.DateTime)
    status = db.Column(db.Boolean, server_default=text("1"))  

    course = db.relationship("HautCourses", backref='sign')


    @classmethod
    def get_not_signed_students(cls, sign_id):
        # 获取课程所有学生
        sign = cls.query.get(sign_id)
        

    @classmethod
    def get_not_signed_students(cls, sign):

        all_students = [sc.student for sc in sign.course.students_enrolled]
        
        # 获取已签到学生
        signed_students = HautStudent.query\
                            .join(HautSignRecord, HautSignRecord.studentId == HautStudent.student_id)\
                            .filter(HautSignRecord.signId == sign.signID).all()

        # 获取未签到的学生
        not_signed_students = set(all_students) - set(signed_students)
        return not_signed_students


# 学生完成签到的表
class HautSignRecord(db.Model):
    __tablename__ = 'haut_sign_record'

    recordId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    signId = db.Column(db.Integer, ForeignKey("haut_sign.signID"))
    studentId = db.Column(db.Integer, ForeignKey("haut_student.student_id"))
    signTime = db.Column(db.DateTime)
    signImg = db.Column(db.String(200))

    sign_student = db.relationship('HautStudent', backref='sign_records')
    sign = db.relationship('HautSign', backref='sign_records')

# 行为类别表
class HautBehavior(db.Model):
    __tablename__ = 'haut_behavior'
    
    action_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_negative = db.Column(db.Boolean)
    action_name = db.Column(db.String(50))

# 行为的坐标表
class HautCoordinates(db.Model):
    __tablename__ = 'haut_coordinates'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_record_id = db.Column(db.Integer, ForeignKey('haut_action_record.id'))
    student_id = db.Column(db.Integer, ForeignKey('haut_student.student_id'), nullable=True)
    behavior_id = db.Column(db.Integer, ForeignKey('haut_behavior.action_id'))
    x1 = db.Column(db.Integer)
    y1 = db.Column(db.Integer)
    x2 = db.Column(db.Integer)
    y2 = db.Column(db.Integer)

# 课程表
class HautCourses(db.Model):
    __tablename__ = 'haut_courses'
    
    CourseID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CourseName = db.Column(db.String(50))
    TeacherID = db.Column(db.Integer, ForeignKey('haut_teacher.TeacherID'))
    StartTime = db.Column(db.DateTime, nullable=True)
    EndTime = db.Column(db.DateTime, nullable=True)
    Status = db.Column(db.String(20), server_default="未开始")

# 学生信息表
class HautStudent(db.Model):
    __tablename__ = 'haut_student'
    
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_ = db.Column('class', db.String(20))
    grade = db.Column(db.Integer)
    name = db.Column(db.String(30))
    photo_url = db.Column(db.String(100))



# 学生和课程的关联表(选课表)
class HautStudentCourses(db.Model):
    __tablename__ = 'haut_student_courses'
    
    StudentID = db.Column(db.Integer, ForeignKey('haut_student.student_id'), primary_key=True)
    CourseID = db.Column(db.Integer, ForeignKey('haut_courses.CourseID'), primary_key=True)
    EnrollmentDate = db.Column(db.Date)



    student = db.relationship('HautStudent', backref='courses_enrolled')
    course = db.relationship('HautCourses', backref='students_enrolled')



# 教师信息表
class HautTeacher(db.Model):
    __tablename__ = 'haut_teacher'
    
    TeacherID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(30))
    Gender = db.Column(db.String(5))
    Email = db.Column(db.String(50), nullable=True)
    PhoneNumber = db.Column(db.String(15), nullable=True)



def create_all_tables():
    db.drop_all()
    db.create_all()

    # 插入行为数据
    behaviors = [HautBehavior(is_negative = 0, action_name = '听讲'),
        HautBehavior(is_negative = 1, action_name = '扭头'),
        HautBehavior(is_negative = 0, action_name = '看书'),
        HautBehavior(is_negative = 1, action_name = '看手机'),
        HautBehavior(is_negative = 1, action_name = '起立'),
        HautBehavior(is_negative = 1, action_name = '吃喝'),
        HautBehavior(is_negative = 1, action_name = '趴桌子'),
        HautBehavior(is_negative = 1, action_name = '睡觉'),
        HautBehavior(is_negative = 1, action_name = '走神'),]
    

    # 学生数据
    # 插入行为数据
    # INSERT INTO `haut_student` VALUES (1,),(2,);
    students = [HautStudent(class_= '6班', grade = 3, name = 'xtc', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                HautStudent(class_= '3班', grade = 2 , name = 'wcc', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                HautStudent(class_= '3班', grade = 2 , name = 'zyb', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                HautStudent(class_= '3班', grade = 2 , name = 'zsl', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                HautStudent(class_= '3班', grade = 2 , name = 'tcy', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                ]
    
    

    # 老师信息数据
    teachers = [
        HautTeacher(Name="赵天明",  Gender="男", Email="john.doe@example.com", PhoneNumber="1333412323"),
        HautTeacher(Name="天明",  Gender="女", Email="john.doe@example.com", PhoneNumber="1333412323")

    ]

    # 课表数据
    # INSERT INTO `haut_student_courses` VALUES (1,1,'2024-01-17'),(2,1,'2024-01-17');
    course = [
        HautCourses(CourseName = "自然语言处理", TeacherID = 1, StartTime = datetime.now(), Status = "正在进行中"),
        HautCourses(CourseName = "计算机视觉", TeacherID = 2, StartTime = datetime.now(), Status = "正在进行中")
    ]
    db.session.add_all(teachers + students + behaviors + course)

    db.session.commit()
    
    
    

    # 学生选课
    studentCourses = [
        HautStudentCourses(StudentID = 1, CourseID = 1, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 2, CourseID = 1, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 3, CourseID = 1, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 4, CourseID = 1, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 5, CourseID = 1, EnrollmentDate = datetime.now()),

        HautStudentCourses(StudentID = 1, CourseID = 2, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 3, CourseID = 2, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 4, CourseID = 2, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 5, CourseID = 2, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 2, CourseID = 2, EnrollmentDate = datetime.now())]
    

    
    db.session.add_all(studentCourses)
    db.session.commit()
    

    

    

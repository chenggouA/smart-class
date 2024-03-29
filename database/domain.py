from sqlalchemy import Column, Integer, String, DateTime, text, func, Boolean, Date, ForeignKey, create_engine, Enum
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


host = '175.24.164.112'
username = 'Chenggou'

# host = 'localhost'
# username = 'root'
password = '123456'
dbname = 'haut'

engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:3306/{dbname}')

# 行为记录表
class HautActionRecord(Base):
    __tablename__ = 'haut_action_record'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_url = Column(String(200))
    timestamp = Column(DateTime)

# 教师发布签到的表
class HautSign(Base):
    # 表的名字
    __tablename__ = 'haut_sign'
    # 表的结构
    signID = Column(Integer, primary_key=True, autoincrement=True)
    courseID = Column(Integer, ForeignKey("haut_courses.CourseID"))

    # default 是应用级别, server_default 是数据库级别
    createTime =  Column(DateTime, server_default=func.now())
    signEndTime = Column(DateTime)

    '''
        0 - 已过期
        1 - 未过期
    '''
    status = Column(Boolean, server_default=text("1"))  

# 学生完成签到的表
class HautSignRecord(Base):
    __tablename__ = 'haut_sign_record'

    recordId = Column(Integer, primary_key=True, autoincrement=True)
    signId = Column(Integer, ForeignKey("haut_sign.signID"))
    studentId = Column(Integer, ForeignKey("haut_student.student_id"))
    signTime = Column(DateTime)
    signImg = Column(String(200))





# 行为类别表
class HautBehavior(Base):
    __tablename__ = 'haut_behavior'
    
    action_id = Column(Integer, primary_key=True, autoincrement=True)
    is_negative = Column(Boolean)
    action_name = Column(String(50))


# 行为的坐标表
class HautCoordinates(Base):
    __tablename__ = 'haut_coordinates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    action_record_id = Column(Integer, ForeignKey('haut_action_record.id'))
    student_id = Column(Integer, ForeignKey('haut_student.student_id'), nullable=True)
    behavior_id = Column(Integer, ForeignKey('haut_behavior.action_id'))
    x1 = Column(Integer)
    y1 = Column(Integer)
    x2 = Column(Integer)
    y2 = Column(Integer)


# 课程表
class HautCourses(Base):
    __tablename__ = 'haut_courses'
    
    CourseID = Column(Integer, primary_key=True, autoincrement=True)
    CourseName = Column(String(50))
    TeacherID = Column(Integer, ForeignKey('haut_teacher.TeacherID'))
    
    StartTime = Column(DateTime, nullable=True)
    EndTime = Column(DateTime, nullable=True)
    Status = Column(Enum("未开始", "正在进行中", "已结束"), server_default="未开始")
    # 课程状态  1. 未开始, 正在进行中, 已结束
    


# 学生信息表
class HautStudent(Base):
    __tablename__ = 'haut_student'
    
    student_id = Column(Integer, primary_key=True, autoincrement=True)
    class_ = Column('class', String(20))
    grade = Column(Integer)
    name = Column(String(30))
    photo_url = Column(String(100))



# 学生和课程的关联表(选课表)
class HautStudentCourses(Base):
    __tablename__ = 'haut_student_courses'
    
    StudentID = Column(Integer, ForeignKey('haut_student.student_id'), primary_key=True)
    CourseID = Column(Integer, ForeignKey('haut_courses.CourseID'), primary_key=True)
    EnrollmentDate = Column(Date)


# 教师信息表
class HautTeacher(Base):
    __tablename__ = 'haut_teacher'
    
    TeacherID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(30))
    Gender = Column(Enum("男", "女", "未知"), server_default="未知")
    Email = Column(String(50), nullable=True)
    PhoneNumber = Column(String(15), nullable=True)



def get_session():
    Session = sessionmaker(bind=engine)
    return Session()
def create_all_table():

    # 删除前先禁用所有的外键约束
    
    with engine.connect() as con:
        con.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        result = con.execute(text("SELECT @@FOREIGN_KEY_CHECKS;"))
        print(result.fetchone())
        Base.metadata.drop_all(engine)
        con.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
    

    # 创建所有的表
    Base.metadata.create_all(engine)
    
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
    

#     INSERT INTO haut_sign (teacherID, courseID, signEndTime) VALUES (1, 1, '2024-03-07 12:00:00');
    # 学生数据
    # 插入行为数据
    # INSERT INTO `haut_student` VALUES (1,),(2,);
    students = [HautStudent(class_= '6班', grade = 3, name = '徐天赐', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                HautStudent(class_= '3班', grade = 2 , name = '翁创创', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                HautStudent(class_= '3班', grade = 2 , name = '周研博', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                HautStudent(class_= '3班', grade = 2 , name = '张森林', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                HautStudent(class_= '3班', grade = 2 , name = '田承玉', photo_url = 'https://files.catbox.moe/9zhzt6.jfif'),
                ]
    
    

    # 老师信息数据
    teachers = [
        HautTeacher(Name="赵天明",  Gender="男", Email="john.doe@example.com", PhoneNumber="1333412323"),
        HautTeacher(Name="天明",  Gender="女", Email="john.doe@example.com", PhoneNumber="1333412323")

    ]
    session = get_session()
    session.add_all(teachers + students + behaviors)
    session.commit()
    
    # 课表数据
    # INSERT INTO `haut_student_courses` VALUES (1,1,'2024-01-17'),(2,1,'2024-01-17');
    coures = [
        HautCourses(CourseName = "自然语言处理", TeacherID = 1, StartTime = datetime.now(), Status = "正在进行中"),
        HautCourses(CourseName = "计算机视觉", TeacherID = 2, StartTime = datetime.now(), Status = "正在进行中")
    ]

    # 学生选课
    studentCourses = [HautStudentCourses(StudentID = 1, CourseID = 1, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 1, CourseID = 2, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 3, CourseID = 2, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 4, CourseID = 2, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 5, CourseID = 2, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 2, CourseID = 1, EnrollmentDate = datetime.now()),
        HautStudentCourses(StudentID = 2, CourseID = 2, EnrollmentDate = datetime.now())]
    

    
    session.add_all(coures + studentCourses)
    session.commit()
    session.close()

    


if __name__ == "__main__":
    create_all_table()


    

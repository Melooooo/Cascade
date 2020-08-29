from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table('association', db.Model.metadata,
    db.Column('user_netID', db.String, db.ForeignKey('user.netID')),
    db.Column('course_courseID', db.Integer, db.ForeignKey('course.courseID'))
)

class User(db.Model):
    __tablename__ = 'user'
    netID = db.Column(db.String, primary_key=True)
    courses = db.relationship('Course', secondary=association_table, back_populates='users')

    def __init__(self, **kwargs):
        self.netID = kwargs.get('netID', '')

    def serialize(self):
        return {
            'netID': self.netID,
            'courses': [c.serialize() for c in self.courses]
        }

class Course(db.Model):
    __tablename__ = 'course'
    courseID = db.Column(db.Integer, primary_key=True)
    courseName = db.Column(db.String, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    enrolled = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', secondary=association_table, back_populates='courses')

    def __init__(self, **kwargs):
        self.courseID = kwargs.get('courseID')
        self.courseName = kwargs.get('courseName')
        self.capacity = kwargs.get('capacity')
        self.enrolled = kwargs.get('enrolled', 0)

    def serialize(self):
        return {
            'courseID': self.courseID,
            'courseName': self.courseName,
            'capacity': self.capacity,
            'enrolled': self.enrolled
        }

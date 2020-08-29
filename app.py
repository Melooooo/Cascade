import json
from flask import Flask
from flask import request
from db import db
from db import User
from db import Course

# define db filename
db_filename = "enrollment.db"
app = Flask(__name__)

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code

def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

#-- USER ROUTES ------------------------------------------------------

@app.route("/")
@app.route("/users/")
def get_users():
    users = User.query.all()
    serialized_users = []
    for user in users:
        serialized_users.append(user.serialize())
    return success_response(serialized_users)

@app.route("/users/", methods=["POST"])
def create_user():
    request_body = json.loads(request.data)
    new_user = User(netID=request_body.get("netID"))
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize())

@app.route('/users/<string:user_netID>/')
def get_user(user_netID):
    user = User.query.filter_by(netID=user_netID).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())

@app.route('/users/<string:user_netID>/', methods=['POST'])
def update_user(user_netID):
    body = json.loads(request.data)
    user = User.query.filter_by(netID=user_netID).first()
    if user is None:
        return failure_response('User not found')
    user.netID = body.get('netID', user.netID)
    db.session.commit()
    return success_response(user.serialize())

@app.route('/users/<string:user_netID>/', methods=['DELETE'])
def delete_user(user_netID):
    user = User.query.filter_by(netID=user_netID).first()
    if user is None:
        return failure_response("User not found")
    for course in user.courses:
        course.enrolled -= 1
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())


#-- COURSE ROUTES --------------------------------------------------
@app.route("/courses/")
def get_courses():
    courses = Course.query.all()
    serialized_courses = []
    for course in courses:
        serialized_courses.append(course.serialize())
    return success_response(serialized_courses)

@app.route("/courses/", methods=["POST"])
def create_course():
    request_body = json.loads(request.data)
    new_course = Course(courseID=request_body.get("courseID"), courseName=request_body.get("courseName"), capacity=request_body.get("capacity"), enrolled=request_body.get("enrolled"))
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize())

@app.route('/courses/<int:course_courseID>/')
def get_course(course_courseID):
    course = Course.query.filter_by(courseID=course_courseID).first()
    if course is None:
        return failure_response("Course not found")
    return success_response(course.serialize())

@app.route('/courses/<int:course_courseID>/', methods=['POST'])
def update_course(course_courseID):
    body = json.loads(request.data)
    course = Course.query.filter_by(courseID=course_courseID).first()
    if course is None:
        return failure_response("Course not found")
    courseName = body.get("courseName")
    capacity = body.get("capacity")
    enrolled = body.get("enrolled")
    db.session.commit()
    return success_response(course.serialize())

@app.route('/courses/<int:course_courseID>/', methods=['DELETE'])
def delete_course(course_courseID):
    course = Course.query.filter_by(courseID=course_courseID).first()
    if course is None:
        return failure_response("Course not found")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())

@app.route('/users/<string:user_netID>/course/', methods=['POST'])
def join_course(user_netID):
    user = User.query.filter_by(netID=user_netID).first()
    if user is None:
        return failure_response("User not found")
    body = json.loads(request.data)
    courseID = body.get('courseID')
    course = Course.query.filter_by(courseID=courseID).first()
    if course is None:
        return failure_response("Course not found")
    user.courses.append(course)
    course.enrolled += 1
    db.session.commit()
    return success_response(user.serialize())

@app.route('/users/<string:user_netID>/course/', methods=['DELETE'])
def drop_course(user_netID):
    user = User.query.filter_by(netID=user_netID).first()
    if user is None:
        return failure_response("User not found")
    body = json.loads(request.data)
    courseID = body.get('courseID')
    course = Course.query.filter_by(courseID=courseID).first()
    if course is None:
        return failure_response("Course not found")
    user.courses.remove(course)
    course.enrolled -= 1
    db.session.commit()
    return success_response(user.serialize())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

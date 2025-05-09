"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Profile, Teacher, Student, Enrollment, Course
from sqlalchemy import select
#from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# #seeding route - NO RECOMENDADO
# @app.route("/seed", methods=['GET'])
# def seed():
#      # Crear usuarios y perfiles
#     user1 = User(email="alice@example.com", password="1234")
#     user2 = User(email="bob@example.com", password="5678")
#     db.session.add_all([user1, user2])
#     db.session.commit()

#     profile1 = Profile(bio="Soy Alice", user_id=user1.id)
#     profile2 = Profile(bio="Soy Bob", user_id=user2.id)
#     db.session.add_all([profile1, profile2])

#     # Profesores
#     teacher1 = Teacher(name="Profesor X")
#     teacher2 = Teacher(name="Profesora Y")
#     db.session.add_all([teacher1, teacher2])
#     db.session.commit()

#     # Cursos
#     course1 = Course(title="Matemáticas", teacher_id=teacher1.id)
#     course2 = Course(title="Ciencias", teacher_id=teacher2.id)
#     db.session.add_all([course1, course2])
#     db.session.commit()

#     # Estudiantes
#     student1 = Student(name="Carlos")
#     student2 = Student(name="Lucía")
#     db.session.add_all([student1, student2])
#     db.session.commit()

#     # Inscripciones
#     enrollment1 = Enrollment(student_id=student1.id, course_id=course1.id)
#     enrollment2 = Enrollment(student_id=student2.id, course_id=course2.id)
#     db.session.add_all([enrollment1, enrollment2])

#     db.session.commit()

# GET: listar todos los usuarios
@app.route("/users", methods=["GET"])
def get_users():
    # esto se puede poner dentro del execute() sin problemas
    stmt = select(User) 
    # devuelve una lista con todos los registros de la tabla, cada uno como un <Objeto>
    users = db.session.execute(stmt).scalars().all() 
    # el scalars() se ocupa de devolverlos como objeto, sino seran devueltos como tuplas.
    # como tupla NO pueden ejecutar el serialize
    print('users sin serialize',users) #users sin serialize [<User 1>, <User 2>]
    print('users despues de loop con serialize', [user.serialize() for user in users])
    #users despues de loop con serialize 
    # [
    # {'id': 1, 'email': 'alice@example.com', 'profile': {'id': 1, 'bio': 'Soy Alice'}}, 
    # {'id': 2, 'email': 'bob@example.com', 'profile': {'id': 2, 'bio': 'Soy Bob'}}
    #]
    #siempre que se nos devuelva una lista/coleccion, hay que serializar dentro de un loop
    return jsonify([user.serialize() for user in users]), 200

# GET: obtener un solo usuario por id
@app.route("/users/<int:user_id>", methods=["GET"]) #ruta dinamica <int:user_id>
def get_user(user_id):
    stmt = select(User).where(User.id == user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    #Es un solo OBJETO, le hago serialize directamente, no necesito loop 
    return jsonify(user.serialize()), 200

# POST: crear un nuevo usuario
@app.route("/users", methods=["POST"])
def create_user():
    #extraemos la informacion del body puede ser con request.json
    data = request.get_json()
    #verificamos que tenemos los elementos OBLIGATORIOS para crear un registro nuevo
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing data"}), 400
    #creamos un nuevo objeto
    new_user = User(
        email=data["email"],
        password=data["password"],  # en prod deberías hashearla
    )
    #lo añadismo a la BD
    db.session.add(new_user)
    #almacenamos los cambios
    db.session.commit()
    return jsonify(new_user.serialize()), 201


@app.route("/users/<int:id>", methods=["PUT"]) #ruta dinamica para decir el id del registro a modificar
def update_user(id):
    #extraemos la informacion del body
    data = request.get_json()
    #data= request.json
    #buscamos el usuario porque vamos a editar
    stmt = select(User).where(User.id == id)
    user = db.session.execute(stmt).scalar_one_or_none()
    #si no encontramos usuario devolvemos que no existe
    if user is None:
        return jsonify({"error": "User not found"}), 404
    #modificamos las propiedades del objeto usuario
    #le ponemos el email que recibimos o si no recibimos email, mantenemos el que estaba
    user.email = data.get("email", user.email) 
    user.password = data.get("password", user.password)
    #almacenamos las cambios
    db.session.commit()
    return jsonify(user.serialize()), 200

@app.route("/users/<int:id>", methods=["DELETE"]) #ruta dinamica
def delete_user(id):
    #seleccionamos usuario a eliminar
    stmt = select(User).where(User.id == id)
    user = db.session.execute(stmt).scalar_one_or_none()
    #Si no hay usuario, pues, peinate...
    if user is None:
        return jsonify({"error": "User not found"}), 404
    #eliminamos usuario
    db.session.delete(user)
    #almacenamos cambios
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200



@app.route("/profiles", methods=["GET"])
def get_profiles():
    stmt = select(Profile)
    profiles = db.session.execute(stmt).scalars().all()
    return jsonify([p.serialize() for p in profiles]), 200

@app.route("/profiles/<int:id>", methods=["GET"])
def get_profile(id):
    stmt = select(Profile).where(Profile.id == id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(profile.serialize()), 200

@app.route("/profiles", methods=["POST"])
def create_profile():
    data = request.get_json()
    if not data or "bio" not in data or "user_id" not in data:
        return jsonify({"error": "Missing data"}), 400
    new_profile = Profile(bio=data["bio"], user_id=data["user_id"])
    db.session.add(new_profile)
    db.session.commit()
    return jsonify(new_profile.serialize()), 201

@app.route("/profiles/<int:id>", methods=["PUT"])
def update_profile(id):
    data = request.get_json()
    stmt = select(Profile).where(Profile.id == id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404
    profile.bio = data.get("bio", profile.bio)
    db.session.commit()
    return jsonify(profile.serialize()), 200

@app.route("/profiles/<int:id>", methods=["DELETE"])
def delete_profile(id):
    stmt = select(Profile).where(Profile.id == id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404
    db.session.delete(profile)
    db.session.commit()
    return jsonify({"message": "Profile deleted"}), 200


@app.route("/teachers", methods=["GET"])
def get_teachers():
    teachers = db.session.execute(select(Teacher)).scalars().all()
    return jsonify([t.serialize() for t in teachers]), 200

@app.route("/teachers", methods=["POST"])
def create_teacher():
    data = request.get_json()
    new_teacher = Teacher(name=data["name"])
    db.session.add(new_teacher)
    db.session.commit()
    return jsonify(new_teacher.serialize()), 201

@app.route("/teachers/<int:id>", methods=["PUT"])
def update_teacher(id):
    data = request.get_json()
    stmt = select(Teacher).where(Teacher.id == id)
    teacher = db.session.execute(stmt).scalar_one_or_none()
    if teacher is None:
        return jsonify({"error": "Teacher not found"}), 404

    teacher.name = data.get("name", teacher.name)
    db.session.commit()
    return jsonify(teacher.serialize()), 200

@app.route("/teachers/<int:id>", methods=["DELETE"])
def delete_teacher(id):
    stmt = select(Teacher).where(Teacher.id == id)
    teacher = db.session.execute(stmt).scalar_one_or_none()
    if teacher is None:
        return jsonify({"error": "Teacher not found"}), 404

    db.session.delete(teacher)
    db.session.commit()
    return jsonify({"message": "Teacher deleted"}), 200


@app.route("/courses", methods=["GET"])
def get_courses():
    courses = db.session.execute(select(Course)).scalars().all()
    return jsonify([c.serialize() for c in courses]), 200

@app.route("/courses", methods=["POST"])
def create_course():
    data = request.get_json()
    new_course = Course(title=data["title"], teacher_id=data["teacher_id"])
    db.session.add(new_course)
    db.session.commit()
    return jsonify(new_course.serialize()), 201

@app.route("/courses/<int:id>", methods=["PUT"])
def update_course(id):
    data = request.get_json()
    stmt = select(Course).where(Course.id == id)
    course = db.session.execute(stmt).scalar_one_or_none()
    if course is None:
        return jsonify({"error": "Course not found"}), 404

    course.title = data.get("title", course.title)
    course.teacher_id = data.get("teacher_id", course.teacher_id)
    db.session.commit()
    return jsonify(course.serialize()), 200

@app.route("/courses/<int:id>", methods=["DELETE"])
def delete_course(id):
    stmt = select(Course).where(Course.id == id)
    course = db.session.execute(stmt).scalar_one_or_none()
    if course is None:
        return jsonify({"error": "Course not found"}), 404

    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted"}), 200


@app.route("/students", methods=["GET"])
def get_students():
    students = db.session.execute(select(Student)).scalars().all()
    return jsonify([s.serialize() for s in students]), 200

@app.route("/students", methods=["POST"])
def create_student():
    data = request.get_json()
    new_student = Student(name=data["name"])
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.serialize()), 201

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json()
    stmt = select(Student).where(Student.id == id)
    student = db.session.execute(stmt).scalar_one_or_none()
    if student is None:
        return jsonify({"error": "Student not found"}), 404

    student.name = data.get("name", student.name)
    db.session.commit()
    return jsonify(student.serialize()), 200

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    stmt = select(Student).where(Student.id == id)
    student = db.session.execute(stmt).scalar_one_or_none()
    if student is None:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted"}), 200


@app.route("/enrollments", methods=["GET"])
def get_enrollments():
    enrollments = db.session.execute(select(Enrollment)).scalars().all()
    return jsonify([e.serialize() for e in enrollments]), 200

@app.route("/enrollments", methods=["POST"])
def create_enrollment():
    data = request.get_json()
    new_enrollment = Enrollment(
        student_id=data["student_id"],
        course_id=data["course_id"]
    )
    db.session.add(new_enrollment)
    db.session.commit()
    return jsonify(new_enrollment.serialize()), 201


@app.route("/enrollments/<int:id>", methods=["PUT"])
def update_enrollment(id):
    data = request.get_json()
    stmt = select(Enrollment).where(Enrollment.id == id)
    enrollment = db.session.execute(stmt).scalar_one_or_none()
    if enrollment is None:
        return jsonify({"error": "Enrollment not found"}), 404

    enrollment.student_id = data.get("student_id", enrollment.student_id)
    enrollment.course_id = data.get("course_id", enrollment.course_id)
    db.session.commit()
    return jsonify(enrollment.serialize()), 200

@app.route("/enrollments/<int:id>", methods=["DELETE"])
def delete_enrollment(id):
    stmt = select(Enrollment).where(Enrollment.id == id)
    enrollment = db.session.execute(stmt).scalar_one_or_none()
    if enrollment is None:
        return jsonify({"error": "Enrollment not found"}), 404

    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({"message": "Enrollment deleted"}), 200






# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
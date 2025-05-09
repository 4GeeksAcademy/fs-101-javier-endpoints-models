from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()

# 🔵 1:1 User → Profile
class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)


    #se encarga de pasar el OBJETO respuesta a diccionario. Se ejecuta como METODO de la clase
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            #serializamos el perfil porque recibimos un objeto de la tabla Perfiles que es el perfil asociado 
            # al usuario. Los objetos (<User 1>) no son compatibles con JSONIFY, solo los diccionarios/listas/string
            "profile": self.profile.serialize() if self.profile else None
        }

class Profile(db.Model):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[str] = mapped_column(String(250))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="profile")

    def serialize(self):
        return {
            "id": self.id,
            "bio": self.bio
        }

# 🟢 1:N Teacher → Course
class Teacher(db.Model):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    courses: Mapped[list["Course"]] = relationship(back_populates="teacher")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            #hacemos loop porque es una lista y no queremos el objeto, 
            # en este caso, solo queremos el title del curso asociado
            "courses": [course.title for course in self.courses]
        }

class Course(db.Model):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))

    teacher: Mapped["Teacher"] = relationship(back_populates="courses")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "teacher": self.teacher.name,
            "students": [
                {
                    "name": enrollment.student.name,
                    "enrolled_on": enrollment.enrollment_date.isoformat()
                } for enrollment in self.enrollments
            ]
        }

# 🔴 N:M Student ↔ Course con modelo de asociación
class Student(db.Model):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "courses": [
                {
                    "title": enrollment.course.title,
                    "enrolled_on": enrollment.enrollment_date.isoformat()
                } for enrollment in self.enrollments
            ]
        }
#tabla de asosiacion, se encarga de decir que alumno esta en que curso
#es relacion muchos a muchos
class Enrollment(db.Model):
    __tablename__ = "enrollments"
    #tabla de asociacion NO tienen id
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    enrollment_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

    def serialize(self):
        return {
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrollment_date": self.enrollment_date.isoformat()
        }
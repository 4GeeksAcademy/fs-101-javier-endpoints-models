from app import app, db
from models import User, Profile, Teacher, Course, Student, Enrollment

with app.app_context():
    db.drop_all()
    db.create_all()

    # Crear usuarios y perfiles
    user1 = User(email="alice@example.com", password="1234")
    user2 = User(email="bob@example.com", password="5678")
    db.session.add_all([user1, user2])
    db.session.commit()

    profile1 = Profile(bio="Soy Alice", user_id=user1.id)
    profile2 = Profile(bio="Soy Bob", user_id=user2.id)
    db.session.add_all([profile1, profile2])

    # Profesores
    teacher1 = Teacher(name="Profesor X")
    teacher2 = Teacher(name="Profesora Y")
    db.session.add_all([teacher1, teacher2])
    db.session.commit()

    # Cursos
    course1 = Course(title="Matemáticas", teacher_id=teacher1.id)
    course2 = Course(title="Ciencias", teacher_id=teacher2.id)
    db.session.add_all([course1, course2])
    db.session.commit()

    # Estudiantes
    student1 = Student(name="Carlos")
    student2 = Student(name="Lucía")
    db.session.add_all([student1, student2])
    db.session.commit()

    # Inscripciones
    enrollment1 = Enrollment(student_id=student1.id, course_id=course1.id)
    enrollment2 = Enrollment(student_id=student2.id, course_id=course2.id)
    db.session.add_all([enrollment1, enrollment2])

    db.session.commit()
    print("✅ Datos sembrados correctamente.")
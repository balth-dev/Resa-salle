from app.database import engine as db_engine
from app.models.classroom import Classroom

class ClassroomRepository:
    def get_all(self) -> list[Classroom]:
        with db_engine.SessionLocal() as session:
            classrooms = session.query(Classroom).all()
            for room in classrooms:
                session.expunge(room)
            return classrooms
    
    def get_by_id(self, classroom_id: int) -> Classroom | None:
        with db_engine.SessionLocal() as session:
            room = session.query(Classroom).filter(Classroom.id_classroom == classroom_id).first()
            if room:
                session.expunge(room)
            return room
    
    def get_by_name(self, name: str) -> Classroom | None:
        with db_engine.SessionLocal() as session:
            room = session.query(Classroom).filter(Classroom.name == name).first()
            if room:
                session.expunge(room)
            return room
    
    def add(self, classroom_data: dict) -> Classroom:
        with db_engine.SessionLocal() as session:
            classroom = Classroom(**classroom_data)
            session.add(classroom)
            session.commit()
            session.refresh(classroom)
            session.expunge(classroom)
            return classroom
    
    def update(self, classroom_id: int, classroom_data: dict) -> Classroom | None:
        with db_engine.SessionLocal() as session:
            classroom = session.query(Classroom).filter(Classroom.id_classroom == classroom_id).first()
            if classroom:
                for key, value in classroom_data.items():
                    setattr(classroom, key, value)
                session.commit()
                session.refresh(classroom)
                session.expunge(classroom)
            return classroom
    
    def delete(self, classroom_id: int) -> bool:
        with db_engine.SessionLocal() as session:
            classroom = session.query(Classroom).filter(Classroom.id_classroom == classroom_id).first()
            if classroom:
                session.delete(classroom)
                session.commit()
                return True
            return False

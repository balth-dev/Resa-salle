from datetime import date, time
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.engine import SessionLocal
from app.repositories.reservation_repository import ReservationRepository
from app.models.reservation import Reservation
from app.models.role import Role
from app.models.user import User
from app.models.building import Building
from app.models.floor import Floor
from app.models.classroom import Classroom


@pytest.fixture(scope="function")
def db_session():
    """Crée une base SQLite en mémoire pour tester ReservationRepository."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    original_session_local = SessionLocal
    import app.database.engine
    app.database.engine.SessionLocal = TestingSessionLocal

    session = TestingSessionLocal()

    # Données de test : Role, User, Building, Classroom
    role = Role(id_role=1, name="Utilisateur")
    session.add(role)

    user = User(
        id_user=1,
        name="Dupont",
        first_name="Jean",
        email="jean.dupont@example.com",
        password="secret_hash",
        id_role=1,
    )
    session.add(user)

    building = Building(id_building=1, name="Bâtiment A")
    session.add(building)

    classroom = Classroom(
        id_classroom=10,
        name="Salle 101",
        capacity=30,
        category="informatique",
        stage="1er",
        code_access="1234",
        id_building=1,
    )
    session.add(classroom)
    session.commit()

    try:
        yield session
    finally:
        session.close()
        app.database.engine.SessionLocal = original_session_local
        Base.metadata.drop_all(bind=engine)


def test_add_reservation(db_session):
    repo = ReservationRepository()
    res_data = {
        "date_reservation": date(2026, 11, 1),
        "start_time": time(9, 0),
        "end_time": time(11, 0),
        "status": "confirmée",
        "id_classroom": 10,
        "id_user": 1,
    }
    reservation = repo.add(res_data)

    assert reservation.id_reservation is not None
    assert reservation.date_reservation == date(2026, 11, 1)
    assert reservation.start_time == time(9, 0)
    assert reservation.end_time == time(11, 0)


def test_check_conflict_overlapping(db_session):
    repo = ReservationRepository()
    # Réservation existante : 09:00 -> 11:00
    repo.add({
        "date_reservation": date(2026, 11, 1),
        "start_time": time(9, 0),
        "end_time": time(11, 0),
        "status": "confirmée",
        "id_classroom": 10,
        "id_user": 1,
    })

    test_date = date(2026, 11, 1)

    # 1. Chevauchement partiel (10:00 -> 12:00) -> Conflit
    conflict = repo.check_conflict(10, test_date, time(10, 0), time(12, 0))
    assert conflict is not None

    # 2. Totalement inclus (09:30 -> 10:30) -> Conflit
    conflict = repo.check_conflict(10, test_date, time(9, 30), time(10, 30))
    assert conflict is not None

    # 3. Englobant (08:00 -> 12:00) -> Conflit
    conflict = repo.check_conflict(10, test_date, time(8, 0), time(12, 0))
    assert conflict is not None


def test_check_conflict_no_overlap(db_session):
    repo = ReservationRepository()
    repo.add({
        "date_reservation": date(2026, 11, 1),
        "start_time": time(9, 0),
        "end_time": time(11, 0),
        "status": "confirmée",
        "id_classroom": 10,
        "id_user": 1,
    })

    test_date = date(2026, 11, 1)

    # 1. Avant (07:00 -> 09:00) - bord à bord -> Pas de conflit
    assert repo.check_conflict(10, test_date, time(7, 0), time(9, 0)) is None

    # 2. Après (11:00 -> 13:00) - bord à bord -> Pas de conflit
    assert repo.check_conflict(10, test_date, time(11, 0), time(13, 0)) is None

    # 3. Autre jour (09:00 -> 11:00) -> Pas de conflit
    assert repo.check_conflict(10, date(2026, 11, 2), time(9, 0), time(11, 0)) is None

    # 4. Autre salle (10:00 -> 12:00 sur salle 99) -> Pas de conflit
    assert repo.check_conflict(99, test_date, time(10, 0), time(12, 0)) is None


def test_get_by_classroom_and_date(db_session):
    repo = ReservationRepository()
    repo.add({
        "date_reservation": date(2026, 11, 1),
        "start_time": time(14, 0),
        "end_time": time(16, 0),
        "status": "confirmée",
        "id_classroom": 10,
        "id_user": 1,
    })
    repo.add({
        "date_reservation": date(2026, 11, 1),
        "start_time": time(9, 0),
        "end_time": time(11, 0),
        "status": "confirmée",
        "id_classroom": 10,
        "id_user": 1,
    })

    results = repo.get_by_classroom_and_date(10, date(2026, 11, 1))
    assert len(results) == 2
    # Doit être ordonné par heure croissante
    assert results[0].start_time == time(9, 0)
    assert results[1].start_time == time(14, 0)



def test_cancel_reservation(db_session):
    repo = ReservationRepository()
    res = repo.add({
        "date_reservation": date(2026, 11, 1),
        "start_time": time(9, 0),
        "end_time": time(11, 0),
        "status": "confirmée",
        "id_classroom": 10,
        "id_user": 1,
    })

    success = repo.cancel(res.id_reservation)
    assert success is True

    # Après annulation, le créneau ne doit plus être en conflit
    conflict = repo.check_conflict(10, date(2026, 11, 1), time(9, 30), time(10, 30))
    assert conflict is None


def test_get_by_user(db_session):
    repo = ReservationRepository()
    repo.add({
        "date_reservation": date(2026, 11, 1),
        "start_time": time(9, 0),
        "end_time": time(11, 0),
        "status": "confirmée",
        "id_classroom": 10,
        "id_user": 1,
    })
    repo.add({
        "date_reservation": date(2026, 11, 2),
        "start_time": time(14, 0),
        "end_time": time(15, 0),
        "status": "confirmée",
        "id_classroom": 10,
        "id_user": 1,
    })

    user_reservations = repo.get_by_user(1)
    assert len(user_reservations) == 2

from datetime import date, time
from app.database import engine as db_engine
from app.models.reservation import Reservation

class ReservationRepository:
    def get_all(self) -> list[Reservation]:
        with db_engine.SessionLocal() as session:
            reservations = session.query(Reservation).all()
            for res in reservations:
                session.expunge(res)
            return reservations
    
    def get_by_id(self, reservation_id: int) -> Reservation | None:
        with db_engine.SessionLocal() as session:
            reservation = session.query(Reservation).filter(Reservation.id_reservation == reservation_id).first()
            if reservation:
                session.expunge(reservation)
            return reservation
    
    def get_by_classroom(self, classroom_id: int) -> list[Reservation]:
        with db_engine.SessionLocal() as session:
            reservations = session.query(Reservation).filter(Reservation.id_classroom == classroom_id).all()
            for res in reservations:
                session.expunge(res)
            return reservations
    
    def get_by_user(self, user_id: int) -> list[Reservation]:
        with db_engine.SessionLocal() as session:
            reservations = session.query(Reservation).filter(
                Reservation.id_user == user_id
            ).order_by(Reservation.date_reservation.desc(), Reservation.start_time.asc()).all()
            for res in reservations:
                session.expunge(res)
            return reservations
    
    def get_by_date(self, date_reservation: date) -> list[Reservation]:
        with db_engine.SessionLocal() as session:
            reservations = session.query(Reservation).filter(
                Reservation.date_reservation == date_reservation
            ).all()
            for res in reservations:
                session.expunge(res)
            return reservations
    
    def get_by_classroom_and_date(self, classroom_id: int, date_reservation: date) -> list[Reservation]:
        with db_engine.SessionLocal() as session:
            reservations = session.query(Reservation).filter(
                Reservation.id_classroom == classroom_id,
                Reservation.date_reservation == date_reservation
            ).order_by(Reservation.start_time.asc()).all()
            for res in reservations:
                session.expunge(res)
            return reservations

    def check_conflict(
        self,
        classroom_id: int,
        date_reservation: date,
        start_time: time,
        end_time: time,
        exclude_reservation_id: int | None = None,
    ) -> Reservation | None:
        """Vérifie si un créneau chevauche une réservation existante.
        Retourne la réservation en conflit, ou None s'il n'y en a pas.
        Deux créneaux [s1, e1] et [s2, e2] se chevauchent si s1 < e2 et e1 > s2.
        """
        with db_engine.SessionLocal() as session:
            query = session.query(Reservation).filter(
                Reservation.id_classroom == classroom_id,
                Reservation.date_reservation == date_reservation,
            )
            if exclude_reservation_id:
                query = query.filter(Reservation.id_reservation != exclude_reservation_id)

            reservations = query.all()
            for res in reservations:
                if res.status and res.status.lower() == "annulée":
                    continue
                if start_time < res.end_time and end_time > res.start_time:
                    session.expunge(res)
                    return res
            return None
    
    def add(self, reservation_data: dict) -> Reservation:
        with db_engine.SessionLocal() as session:
            reservation = Reservation(**reservation_data)
            session.add(reservation)
            session.commit()
            session.refresh(reservation)
            session.expunge(reservation)
            return reservation
    
    def update(self, reservation_id: int, reservation_data: dict) -> Reservation | None:
        with db_engine.SessionLocal() as session:
            reservation = session.query(Reservation).filter(Reservation.id_reservation == reservation_id).first()
            if reservation:
                for key, value in reservation_data.items():
                    setattr(reservation, key, value)
                session.commit()
                session.refresh(reservation)
                session.expunge(reservation)
            return reservation

    def cancel(self, reservation_id: int) -> bool:
        """Annuler une réservation en passant son statut à 'annulée'."""
        with db_engine.SessionLocal() as session:
            reservation = session.query(Reservation).filter(Reservation.id_reservation == reservation_id).first()
            if reservation:
                reservation.status = "annulée"
                session.commit()
                return True
            return False
    
    def delete(self, reservation_id: int) -> bool:
        with db_engine.SessionLocal() as session:
            reservation = session.query(Reservation).filter(Reservation.id_reservation == reservation_id).first()
            if reservation:
                session.delete(reservation)
                session.commit()
                return True
            return False

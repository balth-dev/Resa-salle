from datetime import date
from PySide6.QtWidgets import QMessageBox

from app.views.dashboard import DashboardView
from app.views.reservation_dialog import ReservationDialog
from app.repositories.classroom_repository import ClassroomRepository
from app.repositories.reservation_repository import ReservationRepository
from app.models.user import User


class DashboardController:
    def __init__(
        self,
        view: DashboardView,
        classroom_repo: ClassroomRepository,
        reservation_repo: ReservationRepository,
        current_user: User | None = None,
    ):
        self.view = view
        self.classroom_repo = classroom_repo
        self.reservation_repo = reservation_repo
        self.current_user = current_user
        self._initialize()
        self.connect_signals()

    def _initialize(self):
        """Initialiser le dashboard avec les salles disponibles"""
        self.load_available_rooms()

    def connect_signals(self):
        """Connecter les signaux de la vue"""
        self.view.reserve_clicked.connect(self.on_reserve_clicked)

    def load_available_rooms(self):
        """Charger et afficher les salles disponibles"""
        try:
            all_rooms = self.classroom_repo.get_all()

            if not all_rooms:
                self.view.show_no_rooms_message()
                return

            # Récupérer les réservations d'aujourd'hui
            today = date.today()
            reservations_today = self.reservation_repo.get_by_date(today)

            # Ne considérer occupées que les réservations non annulées
            active_today = [
                res for res in reservations_today
                if not (res.status and res.status.lower() == "annulée")
            ]
            reserved_classroom_ids = {res.id_classroom for res in active_today}

            self.view.clear_rooms()
            available_rooms_found = False

            for room in all_rooms:
                if room.id_classroom not in reserved_classroom_ids:
                    self.view.add_room(
                        room_id=room.id_classroom,
                        room_name=room.name,
                        capacity=room.capacity,
                        category=room.category,
                        stage=room.stage,
                    )
                    available_rooms_found = True

            if not available_rooms_found:
                self.view.show_no_rooms_message()

        except Exception as e:
            print(f"Erreur lors du chargement des salles: {e}")
            self.view.show_no_rooms_message()

    def on_reserve_clicked(self, classroom_id: int):
        """Gérer le clic sur le bouton de réservation"""
        room = self.classroom_repo.get_by_id(classroom_id)
        if not room:
            QMessageBox.warning(self.view, "Erreur", "Salle introuvable.")
            return

        dialog = ReservationDialog(
            classroom=room,
            current_user=self.current_user,
            reservation_repo=self.reservation_repo,
            parent=self.view,
        )

        if dialog.exec():
            # Si la réservation a été confirmée, rafraîchir les salles
            self.load_available_rooms()

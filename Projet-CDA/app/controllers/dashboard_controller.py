from datetime import date
from PySide6.QtWidgets import QMessageBox

from app.views.dashboard import DashboardView
from app.views.reservation_dialog import ReservationDialog
from app.views.add_classroom_dialog import AddClassroomDialog
from app.repositories.classroom_repository import ClassroomRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.building_repository import BuildingRepository
from app.models.user import User


class DashboardController:
    def __init__(
        self,
        view: DashboardView,
        classroom_repo: ClassroomRepository,
        reservation_repo: ReservationRepository,
        building_repo: BuildingRepository | None = None,
        current_user: User | None = None,
    ):
        self.view = view
        self.classroom_repo = classroom_repo
        self.reservation_repo = reservation_repo
        self.building_repo = building_repo or BuildingRepository()
        self.current_user = current_user

        self.cached_classrooms = []
        self.cached_today_reservations = []

        self._initialize()
        self.connect_signals()

    def _initialize(self):
        """Initialiser les données des onglets"""
        self.reload_all_data()

    def connect_signals(self):
        """Connecter les signaux de la vue aux méthodes du contrôleur"""
        self.view.reserve_clicked.connect(self.on_reserve_clicked)
        self.view.cancel_reservation_clicked.connect(self.on_cancel_reservation_clicked)
        self.view.add_classroom_clicked.connect(self.on_add_classroom_clicked)
        self.view.delete_classroom_clicked.connect(self.on_delete_classroom_clicked)
        self.view.filter_changed.connect(self.apply_rooms_filter)
        self.view.refresh_clicked.connect(self.reload_all_data)

    def reload_all_data(self):
        """Recharger l'ensemble des données (salles, réservations perso, administration)"""
        self.load_available_rooms()
        self.load_my_reservations()
        if self.current_user and self.current_user.id_role in (2, 3):
            self.load_admin_classrooms()

    # ------------------ Onglet 1 : Salles disponibles ------------------
    def load_available_rooms(self):
        """Récupère les salles et les réservations du jour, puis applique les filtres"""
        try:
            self.cached_classrooms = self.classroom_repo.get_all()
            today = date.today()
            all_today = self.reservation_repo.get_by_date(today)
            self.cached_today_reservations = [
                r for r in all_today if not (r.status and r.status.lower() == "annulée")
            ]
            self.apply_rooms_filter()
        except Exception as e:
            print(f"Erreur lors du chargement des salles: {e}")
            self.view.show_no_rooms_message(f"Erreur de chargement : {e}")

    def apply_rooms_filter(self):
        """Filtre les salles selon la recherche, la catégorie et la capacité"""
        search_text = self.view.search_input.text().strip().lower()
        selected_category = self.view.category_combo.currentData()
        min_capacity = self.view.capacity_combo.currentData() or 0

        self.view.clear_rooms()
        matched_rooms = []

        for room in self.cached_classrooms:
            # 1. Filtre recherche textuelle (nom)
            if search_text and search_text not in room.name.lower():
                continue

            # 2. Filtre catégorie
            if selected_category and selected_category != "all":
                if room.category.lower() != selected_category.lower():
                    continue

            # 3. Filtre capacité
            if room.capacity < min_capacity:
                continue

            matched_rooms.append(room)

        if not matched_rooms:
            self.view.show_no_rooms_message()
            return

        for room in matched_rooms:
            # Compter combien de réservations actives aujourd'hui
            occupied_count = sum(
                1 for r in self.cached_today_reservations if r.id_classroom == room.id_classroom
            )
            self.view.add_room_card(
                room_id=room.id_classroom,
                room_name=room.name,
                capacity=room.capacity,
                category=room.category,
                stage=room.stage,
                code_access=room.code_access,
                occupied_today_count=occupied_count,
            )

    def on_reserve_clicked(self, classroom_id: int):
        """Ouvre le formulaire de réservation pour la salle choisie"""
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
            # Actualiser les salles et les réservations après validation
            self.load_available_rooms()
            self.load_my_reservations()

    # ------------------ Onglet 2 : Mes réservations ------------------
    def load_my_reservations(self):
        """Charge les réservations de l'utilisateur connecté"""
        if not self.current_user:
            self.view.show_no_reservations_message()
            return

        try:
            reservations = self.reservation_repo.get_by_user(self.current_user.id_user)
            self.view.clear_my_reservations()

            if not reservations:
                self.view.show_no_reservations_message()
                return

            # Map des salles pour retrouver rapidement le nom
            classrooms_map = {room.id_classroom: room.name for room in self.cached_classrooms}

            for res in reservations:
                room_name = classrooms_map.get(
                    res.id_classroom, f"Salle #{res.id_classroom}"
                )
                start_str = res.start_time.strftime("%H:%M")
                end_str = res.end_time.strftime("%H:%M")
                status = res.status or "confirmée"

                self.view.add_my_reservation_card(
                    reservation_id=res.id_reservation,
                    room_name=room_name,
                    res_date=res.date_reservation,
                    start_time_str=start_str,
                    end_time_str=end_str,
                    status=status,
                )
        except Exception as e:
            print(f"Erreur lors du chargement des réservations : {e}")
            self.view.show_no_reservations_message()

    def on_cancel_reservation_clicked(self, reservation_id: int):
        """Gérer l'annulation d'une réservation"""
        confirm = QMessageBox.question(
            self.view,
            "Confirmer l'annulation",
            "Êtes-vous certain de vouloir annuler cette réservation ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            success = self.reservation_repo.cancel(reservation_id)
            if success:
                QMessageBox.information(
                    self.view, "Succès", "La réservation a été annulée avec succès."
                )
                self.load_my_reservations()
                self.load_available_rooms()
            else:
                QMessageBox.critical(
                    self.view, "Erreur", "Impossible d'annuler la réservation."
                )

    # ------------------ Onglet 3 : Administration ------------------
    def load_admin_classrooms(self):
        """Charger toutes les salles dans l'onglet administration"""
        try:
            rooms = self.classroom_repo.get_all()
            self.view.clear_admin_classrooms()

            for room in rooms:
                self.view.add_admin_classroom_card(
                    room_id=room.id_classroom,
                    room_name=room.name,
                    capacity=room.capacity,
                    category=room.category,
                    stage=room.stage,
                    code_access=room.code_access,
                )
        except Exception as e:
            print(f"Erreur lors du chargement de l'administration : {e}")

    def on_add_classroom_clicked(self):
        """Ouvrir la boîte de dialogue d'ajout d'une salle"""
        dialog = AddClassroomDialog(self.building_repo, parent=self.view)
        if dialog.exec() and dialog.classroom_data:
            try:
                self.classroom_repo.add(dialog.classroom_data)
                QMessageBox.information(
                    self.view,
                    "Succès",
                    f"La salle « {dialog.classroom_data['name']} » a été ajoutée avec succès !",
                )
                self.load_available_rooms()
                self.load_admin_classrooms()
            except Exception as e:
                QMessageBox.critical(
                    self.view, "Erreur", f"Impossible d'ajouter la salle : {e}"
                )

    def on_delete_classroom_clicked(self, classroom_id: int):
        """Supprimer une salle"""
        confirm = QMessageBox.question(
            self.view,
            "Confirmer la suppression",
            "Êtes-vous certain de vouloir supprimer cette salle ?\nToutes les réservations associées seront impactées.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                success = self.classroom_repo.delete(classroom_id)
                if success:
                    QMessageBox.information(
                        self.view, "Succès", "La salle a bien été supprimée."
                    )
                    self.load_available_rooms()
                    self.load_admin_classrooms()
                else:
                    QMessageBox.warning(
                        self.view, "Attention", "La salle n'a pas pu être trouvée."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self.view, "Erreur", f"Erreur lors de la suppression : {e}"
                )

from bcrypt import checkpw
from PySide6.QtWidgets import QMessageBox
from sqlalchemy.exc import OperationalError

from app.views.connexion import LoginView
from app.views.dashboard import DashboardView
from app.repositories.user_repository import UserRepository
from app.repositories.classroom_repository import ClassroomRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.building_repository import BuildingRepository
from app.controllers.dashboard_controller import DashboardController


class LoginController:
    def __init__(self, view: LoginView, repository: UserRepository):
        self.view = view
        self.repository = repository
        self.dashboard_view = None
        self.dashboard_controller = None
        self._initialize()
        self.connect_signal()

    def _initialize(self):
        pass

    def connect_signal(self):
        self.view.login_clicked.connect(self.on_login_clicked)

    def on_login_clicked(self, email: str, password: str):
        try:
            user = self.repository.get_by_email(email)
        except OperationalError:
            QMessageBox.critical(
                self.view,
                "Erreur de base de données",
                "Impossible de se connecter à la base de données. Vérifie tes identifiants ou ta configuration .env.",
            )
            return

        if user and self._verify_password(password, user.password):
            self._show_dashboard(user)
        else:
            self.view.invalid_credential()

    def _show_dashboard(self, user):
        """Afficher le dashboard après une connexion réussie"""
        try:
            # Créer la vue du dashboard avec l'utilisateur connecté
            self.dashboard_view = DashboardView(current_user=user)
            # Associer la vue de connexion pour la déconnexion
            self.dashboard_view.login_view = self.view

            # Repositories
            classroom_repo = ClassroomRepository()
            reservation_repo = ReservationRepository()
            building_repo = BuildingRepository()

            # Contrôleur
            self.dashboard_controller = DashboardController(
                self.dashboard_view,
                classroom_repo,
                reservation_repo,
                building_repo=building_repo,
                current_user=user,
            )

            # Titre fenêtre
            self.dashboard_view.setWindowTitle(f"Tableau de bord — {user.first_name} {user.name}")

            # Afficher le dashboard et masquer la connexion
            self.dashboard_view.show()
            self.view.hide()

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Erreur",
                f"Erreur lors du chargement du tableau de bord : {str(e)}",
            )

    def _verify_password(self, provided_password: str, stored_password: str) -> bool:
        return checkpw(
            provided_password.encode("utf-8"),
            stored_password.encode("utf-8"),
        )

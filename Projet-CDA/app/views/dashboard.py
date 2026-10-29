from datetime import datetime, date
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QPushButton,
    QFrame,
    QLineEdit,
    QComboBox,
    QTabWidget,
    QSizePolicy,
)

ROLE_NAMES = {
    1: "Utilisateur",
    2: "Administrateur",
    3: "Gestionnaire",
    4: "Enseignant",
    5: "Étudiant",
    6: "Technicien",
}


class DashboardView(QWidget):
    reserve_clicked = Signal(int)  # classroom_id
    cancel_reservation_clicked = Signal(int)  # reservation_id
    add_classroom_clicked = Signal()
    delete_classroom_clicked = Signal(int)  # classroom_id
    filter_changed = Signal()
    refresh_clicked = Signal()

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.login_view = None

        self.setObjectName("DashboardWidget")
        self.setWindowTitle("Tableau de bord — Réservation de salles")
        self.resize(1100, 780)
        self.setMinimumSize(900, 650)

        self._apply_styles()
        self._build_ui()
        self._start_clock()

    def _apply_styles(self):
        self.setStyleSheet(
            """
            QWidget#DashboardWidget {
                background-color: #0E1216;
                color: #E8EFF5;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #E8EFF5;
            }
            QTabWidget::pane {
                border: 1px solid #223147;
                background-color: #0E1216;
                border-radius: 12px;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #11161A;
                color: #9EA8B4;
                padding: 10px 22px;
                margin-right: 6px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 13px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #2D6AB7;
                color: #FFFFFF;
            }
            QTabBar::tab:hover:!selected {
                background-color: #1A222B;
                color: #FFFFFF;
            }
            QFrame.card {
                background-color: #11161A;
                border: 1px solid #223147;
                border-radius: 12px;
                padding: 14px;
            }
            QFrame.card:hover {
                border: 1px solid #2CCED2;
            }
            QLineEdit, QComboBox {
                background-color: #10161D;
                border: 1px solid #223147;
                border-radius: 8px;
                color: #FFFFFF;
                padding: 8px 12px;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2CCED2;
            }
            QPushButton.primaryBtn {
                background-color: #2D6AB7;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton.primaryBtn:hover {
                background-color: #3F7FD2;
            }
            QPushButton.dangerBtn {
                background-color: #2A1518;
                color: #FF8F8F;
                border: 1px solid #752932;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton.dangerBtn:hover {
                background-color: #401B20;
                color: #FFFFFF;
                border: 1px solid #FF5252;
            }
            QPushButton.secondaryBtn {
                background-color: #131A20;
                color: #E8EFF5;
                border: 1px solid #223147;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }
            QPushButton.secondaryBtn:hover {
                background-color: #1E2732;
                color: #FFFFFF;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            """
        )

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(18)

        # 1. En-tête supérieur
        top_bar = QHBoxLayout()
        top_bar.setSpacing(16)

        # Informations utilisateur
        user_info_layout = QVBoxLayout()
        user_info_layout.setSpacing(4)

        first_name = self.current_user.first_name if self.current_user else "Invité"
        last_name = self.current_user.name if self.current_user else ""
        role_id = self.current_user.id_role if self.current_user else 1
        role_name = ROLE_NAMES.get(role_id, "Utilisateur")

        self.welcome_label = QLabel(f"Bonjour, <b>{first_name} {last_name}</b>")
        self.welcome_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFFFFF;")
        user_info_layout.addWidget(self.welcome_label)

        # Badge de rôle
        role_badge = QLabel(f"  ● Rôle : {role_name}  ")
        if role_id in (2, 3):  # Admin / Gestionnaire
            role_badge.setStyleSheet(
                "background-color: rgba(255, 170, 90, 0.15); color: #FFAA5A; "
                "border: 1px solid rgba(255, 170, 90, 0.4); border-radius: 10px; font-size: 11px; font-weight: bold;"
            )
        else:
            role_badge.setStyleSheet(
                "background-color: rgba(44, 206, 210, 0.15); color: #2CCED2; "
                "border: 1px solid rgba(44, 206, 210, 0.4); border-radius: 10px; font-size: 11px; font-weight: bold;"
            )
        role_badge.setFixedHeight(22)
        user_info_layout.addWidget(role_badge)

        top_bar.addLayout(user_info_layout)
        top_bar.addStretch()

        # Horloge
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #A2D1FF; "
            "background-color: #11161A; border: 1px solid #223147; border-radius: 10px; padding: 6px 14px;"
        )
        top_bar.addWidget(self.clock_label)

        # Bouton Déconnexion
        logout_btn = QPushButton("Se déconnecter")
        logout_btn.setProperty("class", "secondaryBtn")
        logout_btn.setMinimumHeight(36)
        logout_btn.clicked.connect(self.on_logout_clicked)
        top_bar.addWidget(logout_btn)

        main_layout.addLayout(top_bar)

        # 2. Système d'onglets
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Onglet 1 : Salles disponibles
        self.tab_rooms = QWidget()
        self._build_rooms_tab()
        self.tabs.addTab(self.tab_rooms, "🏢 Salles disponibles")

        # Onglet 2 : Mes réservations
        self.tab_my_reservations = QWidget()
        self._build_my_reservations_tab()
        self.tabs.addTab(self.tab_my_reservations, "📅 Mes réservations")

        # Onglet 3 : Administration (si Admin ou Gestionnaire)
        is_admin = self.current_user and self.current_user.id_role in (2, 3)
        if is_admin:
            self.tab_admin = QWidget()
            self._build_admin_tab()
            self.tabs.addTab(self.tab_admin, "⚙️ Administration")

        main_layout.addWidget(self.tabs)

    def _build_rooms_tab(self):
        tab_layout = QVBoxLayout(self.tab_rooms)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        tab_layout.setSpacing(14)

        # Barre de filtres et recherche
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(12)

        # Recherche textuelle
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom de salle...")
        self.search_input.textChanged.connect(lambda: self.filter_changed.emit())
        filter_bar.addWidget(self.search_input, stretch=3)

        # Filtre Catégorie
        self.category_combo = QComboBox()
        self.category_combo.addItem("Toutes catégories", "all")
        self.category_combo.addItem("Informatique", "informatique")
        self.category_combo.addItem("Traditionnelle", "traditionnelle")
        self.category_combo.currentIndexChanged.connect(lambda: self.filter_changed.emit())
        filter_bar.addWidget(self.category_combo, stretch=2)

        # Filtre Capacité
        self.capacity_combo = QComboBox()
        self.capacity_combo.addItem("Toutes capacités", 0)
        self.capacity_combo.addItem("≥ 15 personnes", 15)
        self.capacity_combo.addItem("≥ 25 personnes", 25)
        self.capacity_combo.addItem("≥ 30 personnes", 30)
        self.capacity_combo.currentIndexChanged.connect(lambda: self.filter_changed.emit())
        filter_bar.addWidget(self.capacity_combo, stretch=2)

        # Bouton Actualiser
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setProperty("class", "secondaryBtn")
        refresh_btn.clicked.connect(lambda: self.refresh_clicked.emit())
        filter_bar.addWidget(refresh_btn)

        tab_layout.addLayout(filter_bar)

        # Zone déroulante des cartes de salles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.rooms_container = QWidget()
        self.rooms_layout = QVBoxLayout(self.rooms_container)
        self.rooms_layout.setSpacing(12)
        self.rooms_layout.setContentsMargins(0, 4, 0, 4)
        self.rooms_layout.addStretch()

        scroll.setWidget(self.rooms_container)
        tab_layout.addWidget(scroll)

    def _build_my_reservations_tab(self):
        tab_layout = QVBoxLayout(self.tab_my_reservations)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        tab_layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_title = QLabel("<b>Historique de mes réservations</b>")
        header_title.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        refresh_res_btn = QPushButton("🔄 Rafraîchir")
        refresh_res_btn.setProperty("class", "secondaryBtn")
        refresh_res_btn.clicked.connect(lambda: self.refresh_clicked.emit())
        header_layout.addWidget(refresh_res_btn)

        tab_layout.addLayout(header_layout)

        # Zone déroulante des réservations
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.reservations_container = QWidget()
        self.reservations_layout = QVBoxLayout(self.reservations_container)
        self.reservations_layout.setSpacing(12)
        self.reservations_layout.setContentsMargins(0, 4, 0, 4)
        self.reservations_layout.addStretch()

        scroll.setWidget(self.reservations_container)
        tab_layout.addWidget(scroll)

    def _build_admin_tab(self):
        tab_layout = QVBoxLayout(self.tab_admin)
        tab_layout.setContentsMargins(16, 16, 16, 16)
        tab_layout.setSpacing(14)

        header_layout = QHBoxLayout()
        header_title = QLabel("<b>Administration du parc de salles</b>")
        header_title.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        add_room_btn = QPushButton("+ Ajouter une nouvelle salle")
        add_room_btn.setProperty("class", "primaryBtn")
        add_room_btn.clicked.connect(lambda: self.add_classroom_clicked.emit())
        header_layout.addWidget(add_room_btn)

        tab_layout.addLayout(header_layout)

        # Zone déroulante administration
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.admin_rooms_container = QWidget()
        self.admin_rooms_layout = QVBoxLayout(self.admin_rooms_container)
        self.admin_rooms_layout.setSpacing(12)
        self.admin_rooms_layout.setContentsMargins(0, 4, 0, 4)
        self.admin_rooms_layout.addStretch()

        scroll.setWidget(self.admin_rooms_container)
        tab_layout.addWidget(scroll)

    # ------------------ Gestion de l'horloge ------------------
    def _start_clock(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_clock)
        self.timer.start(1000)
        self._update_clock()

    def _update_clock(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(f"🕐 {current_time}")

    # ------------------ Méthodes d'affichage : Salles ------------------
    def clear_rooms(self):
        while self.rooms_layout.count() > 1:
            item = self.rooms_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_room_card(
        self,
        room_id: int,
        room_name: str,
        capacity: int,
        category: str,
        stage: str,
        code_access: str | None,
        occupied_today_count: int,
    ):
        card = QFrame()
        card.setProperty("class", "card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(16)

        # Bloc informations
        info_box = QVBoxLayout()
        info_box.setSpacing(6)

        # Titre et Badge de catégorie
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        name_label = QLabel(f"<b>{room_name}</b>")
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        title_row.addWidget(name_label)

        cat_badge = QLabel(f"  {category.capitalize()}  ")
        if category.lower() == "informatique":
            cat_badge.setStyleSheet(
                "background-color: rgba(45, 106, 183, 0.2); color: #A2D1FF; "
                "border: 1px solid #2D6AB7; border-radius: 8px; font-size: 11px; font-weight: bold;"
            )
        else:
            cat_badge.setStyleSheet(
                "background-color: rgba(138, 79, 255, 0.2); color: #D1A2FF; "
                "border: 1px solid #7A3FB7; border-radius: 8px; font-size: 11px; font-weight: bold;"
            )
        cat_badge.setFixedHeight(20)
        title_row.addWidget(cat_badge)
        title_row.addStretch()

        info_box.addLayout(title_row)

        # Détails (Capacité, Étage, Code)
        details_row = QHBoxLayout()
        details_row.setSpacing(16)

        cap_label = QLabel(f"👥 Capacité : <b>{capacity}</b> places")
        cap_label.setStyleSheet("color: #DCE6F1; font-size: 12px;")
        details_row.addWidget(cap_label)

        stage_label = QLabel(f"🏢 Étage : <b>{stage}</b>")
        stage_label.setStyleSheet("color: #DCE6F1; font-size: 12px;")
        details_row.addWidget(stage_label)

        if code_access:
            code_label = QLabel(f"🔑 Code : <code>{code_access}</code>")
            code_label.setStyleSheet("color: #FFAA5A; font-size: 12px;")
            details_row.addWidget(code_label)

        details_row.addStretch()
        info_box.addLayout(details_row)

        # Statut du jour
        if occupied_today_count == 0:
            status_label = QLabel("🟢 Entièrement libre aujourd'hui")
            status_label.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: 600;")
        else:
            status_label = QLabel(f"🟡 {occupied_today_count} créneau(x) réservé(s) aujourd'hui")
            status_label.setStyleSheet("color: #FFAA5A; font-size: 11px; font-weight: 600;")
        info_box.addWidget(status_label)

        layout.addLayout(info_box, stretch=4)

        # Bouton Réserver
        reserve_btn = QPushButton("Réserver cette salle")
        reserve_btn.setProperty("class", "primaryBtn")
        reserve_btn.setMinimumHeight(40)
        reserve_btn.setMinimumWidth(160)
        reserve_btn.clicked.connect(lambda: self.reserve_clicked.emit(room_id))
        layout.addWidget(reserve_btn, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.rooms_layout.insertWidget(self.rooms_layout.count() - 1, card)

    def show_no_rooms_message(self, message: str = "Aucune salle ne correspond à vos critères de recherche."):
        self.clear_rooms()
        empty_lbl = QLabel(message)
        empty_lbl.setStyleSheet("color: #9EA8B4; font-size: 14px; padding: 40px; text-align: center;")
        empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rooms_layout.insertWidget(0, empty_lbl)

    # ------------------ Méthodes d'affichage : Mes Réservations ------------------
    def clear_my_reservations(self):
        while self.reservations_layout.count() > 1:
            item = self.reservations_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_my_reservation_card(
        self,
        reservation_id: int,
        room_name: str,
        res_date: date,
        start_time_str: str,
        end_time_str: str,
        status: str,
    ):
        card = QFrame()
        card.setProperty("class", "card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(16)

        info_box = QVBoxLayout()
        info_box.setSpacing(6)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title = QLabel(f"<b>{room_name}</b>")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        title_row.addWidget(title)

        # Statut badge
        is_canceled = status.lower() == "annulée"
        stat_badge = QLabel(f"  {status.capitalize()}  ")
        if is_canceled:
            stat_badge.setStyleSheet(
                "background-color: rgba(255, 107, 107, 0.15); color: #FF6B6B; "
                "border: 1px solid #752932; border-radius: 8px; font-size: 11px; font-weight: bold;"
            )
        else:
            stat_badge.setStyleSheet(
                "background-color: rgba(76, 175, 80, 0.15); color: #4CAF50; "
                "border: 1px solid #2E7D32; border-radius: 8px; font-size: 11px; font-weight: bold;"
            )
        stat_badge.setFixedHeight(20)
        title_row.addWidget(stat_badge)
        title_row.addStretch()

        info_box.addLayout(title_row)

        details = QLabel(
            f"📅 Date : <b>{res_date.strftime('%d/%m/%Y')}</b>   |   "
            f"⏰ Horaires : <b>{start_time_str}</b> à <b>{end_time_str}</b>"
        )
        details.setStyleSheet("color: #DCE6F1; font-size: 13px;")
        info_box.addWidget(details)

        layout.addLayout(info_box, stretch=4)

        # Bouton Annuler si la réservation est confirmée
        if not is_canceled:
            cancel_btn = QPushButton("Annuler la réservation")
            cancel_btn.setProperty("class", "dangerBtn")
            cancel_btn.setMinimumHeight(36)
            cancel_btn.clicked.connect(lambda: self.cancel_reservation_clicked.emit(reservation_id))
            layout.addWidget(cancel_btn, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)
        else:
            canceled_lbl = QLabel("Réservation annulée")
            canceled_lbl.setStyleSheet("color: #9EA8B4; font-size: 12px; font-style: italic;")
            layout.addWidget(canceled_lbl, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.reservations_layout.insertWidget(self.reservations_layout.count() - 1, card)

    def show_no_reservations_message(self):
        self.clear_my_reservations()
        empty_lbl = QLabel("Vous n'avez aucune réservation pour le moment.")
        empty_lbl.setStyleSheet("color: #9EA8B4; font-size: 14px; padding: 40px; text-align: center;")
        empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reservations_layout.insertWidget(0, empty_lbl)

    # ------------------ Méthodes d'affichage : Administration ------------------
    def clear_admin_classrooms(self):
        if hasattr(self, "admin_rooms_layout"):
            while self.admin_rooms_layout.count() > 1:
                item = self.admin_rooms_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

    def add_admin_classroom_card(
        self,
        room_id: int,
        room_name: str,
        capacity: int,
        category: str,
        stage: str,
        code_access: str | None,
    ):
        if not hasattr(self, "admin_rooms_layout"):
            return

        card = QFrame()
        card.setProperty("class", "card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        info_box = QVBoxLayout()
        info_box.setSpacing(4)

        title = QLabel(f"<b>{room_name}</b> (ID : {room_id})")
        title.setStyleSheet("font-size: 15px; color: #FFFFFF;")
        info_box.addWidget(title)

        code_str = f" | Code : {code_access}" if code_access else ""
        details = QLabel(
            f"Capacité : {capacity} places | Type : {category.capitalize()} | Étage : {stage}{code_str}"
        )
        details.setStyleSheet("color: #A2D1FF; font-size: 12px;")
        info_box.addWidget(details)

        layout.addLayout(info_box, stretch=4)

        delete_btn = QPushButton("🗑 Supprimer")
        delete_btn.setProperty("class", "dangerBtn")
        delete_btn.setMinimumHeight(34)
        delete_btn.clicked.connect(lambda: self.delete_classroom_clicked.emit(room_id))
        layout.addWidget(delete_btn, stretch=1, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.admin_rooms_layout.insertWidget(self.admin_rooms_layout.count() - 1, card)

    # ------------------ Gestion de la déconnexion ------------------
    def on_logout_clicked(self):
        if hasattr(self, "login_view") and self.login_view:
            self.login_view.email_input.clear()
            self.login_view.password_input.clear()
            self.login_view.show()
        self.close()

    def closeEvent(self, event):
        if hasattr(self, "timer"):
            self.timer.stop()
        super().closeEvent(event)

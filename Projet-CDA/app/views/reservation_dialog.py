from datetime import date, datetime, time
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDateEdit,
    QTimeEdit,
    QFrame,
    QMessageBox,
    QScrollArea,
    QWidget,
)

from app.models.classroom import Classroom
from app.models.user import User
from app.repositories.reservation_repository import ReservationRepository


class ReservationDialog(QDialog):
    def __init__(
        self,
        classroom: Classroom,
        current_user: User | None,
        reservation_repo: ReservationRepository,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.classroom = classroom
        self.current_user = current_user
        self.reservation_repo = reservation_repo

        self.setWindowTitle(f"Réservation — {classroom.name}")
        self.setMinimumWidth(520)
        self.setObjectName("ReservationDialog")
        self.setStyleSheet(
            """
            QDialog#ReservationDialog {
                background-color: #0E1216;
                color: #E8EFF5;
            }
            QLabel {
                color: #E8EFF5;
            }
            QFrame.card {
                background-color: #11161A;
                border: 1px solid #223147;
                border-radius: 10px;
                padding: 12px;
            }
            QDateEdit, QTimeEdit {
                background-color: #10161D;
                border: 1px solid #223147;
                border-radius: 8px;
                color: #FFFFFF;
                padding: 8px 10px;
                font-size: 13px;
                min-height: 20px;
            }
            QDateEdit:focus, QTimeEdit:focus {
                border: 1px solid #2CCED2;
            }
            QPushButton#confirmButton {
                background-color: #2D6AB7;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#confirmButton:hover {
                background-color: #3F7FD2;
            }
            QPushButton#confirmButton:pressed {
                background-color: #245B95;
            }
            QPushButton#cancelButton {
                background-color: #131A20;
                color: #9EA8B4;
                border: 1px solid #223147;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
            }
            QPushButton#cancelButton:hover {
                background-color: #1E2732;
                color: #FFFFFF;
            }
            QLabel#errorLabel {
                color: #FF8F8F;
                background-color: #35161A;
                border: 1px solid #752932;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }
            """
        )

        self._build_ui()
        self._refresh_existing_reservations()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        # En-tête : Informations sur la salle
        header_card = QFrame()
        header_card.setProperty("class", "card")
        header_layout = QVBoxLayout(header_card)
        header_layout.setSpacing(6)

        title_label = QLabel(f"<b>{self.classroom.name}</b>")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(title_label)

        details_text = (
            f"Capacité : {self.classroom.capacity} places  |  "
            f"Type : {self.classroom.category.capitalize()}  |  "
            f"Étage : {self.classroom.stage}"
        )
        details_label = QLabel(details_text)
        details_label.setStyleSheet("color: #A2D1FF; font-size: 12px;")
        header_layout.addWidget(details_label)

        if self.classroom.code_access:
            code_label = QLabel(f"Code d'accès : <code>{self.classroom.code_access}</code>")
            code_label.setStyleSheet("color: #FFAA5A; font-size: 12px;")
            header_layout.addWidget(code_label)

        main_layout.addWidget(header_card)

        # Formulaire de choix de date et heure
        form_card = QFrame()
        form_card.setProperty("class", "card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setSpacing(12)

        # Champ Date
        date_header_layout = QHBoxLayout()
        date_title = QLabel("Date de la réservation :")
        date_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        date_header_layout.addWidget(date_title)
        form_layout.addLayout(date_header_layout)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self._on_date_changed)
        form_layout.addWidget(self.date_edit)

        # Champs Horaires Début / Fin
        time_container = QHBoxLayout()
        time_container.setSpacing(16)

        # Début
        start_box = QVBoxLayout()
        start_label = QLabel("Heure de début :")
        start_label.setStyleSheet("font-size: 12px; color: #DCE6F1;")
        start_box.addWidget(start_label)

        now = datetime.now()
        default_start_hour = (now.hour + 1) if now.minute > 0 else now.hour
        if default_start_hour > 20:
            default_start_hour = 8

        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime(default_start_hour, 0))
        self.start_time_edit.timeChanged.connect(self._on_time_changed)
        start_box.addWidget(self.start_time_edit)
        time_container.addLayout(start_box)

        # Fin
        end_box = QVBoxLayout()
        end_label = QLabel("Heure de fin :")
        end_label.setStyleSheet("font-size: 12px; color: #DCE6F1;")
        end_box.addWidget(end_label)

        default_end_hour = min(default_start_hour + 1, 23)
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        self.end_time_edit.setTime(QTime(default_end_hour, 0))
        end_box.addWidget(self.end_time_edit)
        time_container.addLayout(end_box)

        form_layout.addLayout(time_container)
        main_layout.addWidget(form_card)

        # Panneau des créneaux déjà occupés pour la date sélectionnée
        occupied_card = QFrame()
        occupied_card.setProperty("class", "card")
        occupied_layout = QVBoxLayout(occupied_card)
        occupied_layout.setSpacing(8)

        occupied_title = QLabel("Créneaux occupés sur cette date :")
        occupied_title.setStyleSheet("font-weight: bold; font-size: 12px; color: #DCE6F1;")
        occupied_layout.addWidget(occupied_title)

        self.occupied_label = QLabel("Chargement des créneaux...")
        self.occupied_label.setWordWrap(True)
        self.occupied_label.setStyleSheet("color: #9EA8B4; font-size: 12px;")
        occupied_layout.addWidget(self.occupied_label)

        main_layout.addWidget(occupied_card)

        # Message d'erreur
        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)

        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        buttons_layout.addStretch()

        self.confirm_button = QPushButton("Confirmer la réservation")
        self.confirm_button.setObjectName("confirmButton")
        self.confirm_button.clicked.connect(self._on_submit)
        buttons_layout.addWidget(self.confirm_button)

        main_layout.addLayout(buttons_layout)

    def _on_date_changed(self):
        self._clear_error()
        self._refresh_existing_reservations()

    def _on_time_changed(self, new_time: QTime):
        # Ajuster automatiquement l'heure de fin si elle devient inférieure ou égale à l'heure de début
        if self.end_time_edit.time() <= new_time:
            new_end_hour = min(new_time.hour() + 1, 23)
            self.end_time_edit.setTime(QTime(new_end_hour, new_time.minute()))

    def _refresh_existing_reservations(self):
        selected_qdate = self.date_edit.date()
        selected_date = date(selected_qdate.year(), selected_qdate.month(), selected_qdate.day())

        try:
            reservations = self.reservation_repo.get_by_classroom_and_date(
                self.classroom.id_classroom, selected_date
            )
            # Ne garder que les réservations non annulées
            active_reservations = [
                r for r in reservations if not (r.status and r.status.lower() == "annulée")
            ]

            if not active_reservations:
                self.occupied_label.setText("✓ Aucune réservation : la salle est libre toute la journée.")
                self.occupied_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
            else:
                lines = []
                for res in active_reservations:
                    s_str = res.start_time.strftime("%H:%M")
                    e_str = res.end_time.strftime("%H:%M")
                    lines.append(f"• De {s_str} à {e_str}")
                self.occupied_label.setText("\n".join(lines))
                self.occupied_label.setStyleSheet("color: #FFAA5A; font-size: 12px;")
        except Exception as e:
            self.occupied_label.setText(f"Impossible de charger les créneaux : {e}")
            self.occupied_label.setStyleSheet("color: #FF6B6B; font-size: 12px;")

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()

    def _clear_error(self):
        self.error_label.clear()
        self.error_label.hide()

    def _on_submit(self):
        self._clear_error()

        if not self.current_user:
            self._show_error("Aucun utilisateur n'est connecté. Impossible de réserver.")
            return

        selected_qdate = self.date_edit.date()
        reservation_date = date(selected_qdate.year(), selected_qdate.month(), selected_qdate.day())

        start_qtime = self.start_time_edit.time()
        end_qtime = self.end_time_edit.time()
        start_time_val = time(start_qtime.hour(), start_qtime.minute())
        end_time_val = time(end_qtime.hour(), end_qtime.minute())

        # Validation de l'ordre des heures
        if start_time_val >= end_time_val:
            self._show_error("L'heure de fin doit être postérieure à l'heure de début.")
            return

        # Validation que le créneau n'est pas dans le passé
        now = datetime.now()
        if reservation_date < now.date():
            self._show_error("La date sélectionnée est déjà passée.")
            return

        if reservation_date == now.date() and start_time_val <= now.time():
            self._show_error("L'heure de début sélectionnée est déjà passée.")
            return

        # Vérification des conflits de créneau
        conflict = self.reservation_repo.check_conflict(
            classroom_id=self.classroom.id_classroom,
            date_reservation=reservation_date,
            start_time=start_time_val,
            end_time=end_time_val,
        )

        if conflict:
            c_start = conflict.start_time.strftime("%H:%M")
            c_end = conflict.end_time.strftime("%H:%M")
            self._show_error(
                f"Créneau indisponible : la salle est déjà réservée de {c_start} à {c_end}."
            )
            return

        # Création de la réservation
        try:
            reservation_data = {
                "date_reservation": reservation_date,
                "start_time": start_time_val,
                "end_time": end_time_val,
                "status": "confirmée",
                "id_classroom": self.classroom.id_classroom,
                "id_user": self.current_user.id_user,
            }
            self.reservation_repo.add(reservation_data)

            QMessageBox.information(
                self,
                "Réservation confirmée",
                f"Votre réservation pour la salle « {self.classroom.name} » le "
                f"{reservation_date.strftime('%d/%m/%Y')} de {start_time_val.strftime('%H:%M')} "
                f"à {end_time_val.strftime('%H:%M')} a bien été enregistrée !",
            )
            self.accept()

        except Exception as e:
            self._show_error(f"Une erreur est survenue lors de l'enregistrement : {e}")


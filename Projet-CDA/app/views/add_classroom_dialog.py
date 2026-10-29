from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QFrame,
    QMessageBox,
    QWidget,
)

from app.repositories.building_repository import BuildingRepository


class AddClassroomDialog(QDialog):
    def __init__(self, building_repo: BuildingRepository, parent: QWidget | None = None):
        super().__init__(parent)
        self.building_repo = building_repo
        self.classroom_data: dict | None = None

        self.setWindowTitle("Ajouter une salle")
        self.setMinimumWidth(480)
        self.setObjectName("AddClassroomDialog")
        self.setStyleSheet(
            """
            QDialog#AddClassroomDialog {
                background-color: #0E1216;
                color: #E8EFF5;
            }
            QLabel {
                color: #E8EFF5;
            }
            QFrame.card {
                background-color: #11161A;
                border: 1px solid #223147;
                border-radius: 12px;
                padding: 16px;
            }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #10161D;
                border: 1px solid #223147;
                border-radius: 8px;
                color: #FFFFFF;
                padding: 8px 10px;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #2CCED2;
            }
            QPushButton#submitBtn {
                background-color: #2D6AB7;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#submitBtn:hover {
                background-color: #3F7FD2;
            }
            QPushButton#cancelBtn {
                background-color: #131A20;
                color: #9EA8B4;
                border: 1px solid #223147;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
            }
            QPushButton#cancelBtn:hover {
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

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title = QLabel("<b>Ajouter une nouvelle salle</b>")
        title.setStyleSheet("font-size: 20px; color: #FFFFFF;")
        main_layout.addWidget(title)

        card = QFrame()
        card.setProperty("class", "card")
        form_layout = QVBoxLayout(card)
        form_layout.setSpacing(12)

        # Nom de la salle
        name_label = QLabel("Nom de la salle :")
        name_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        form_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ex: Salle Turing (101)")
        form_layout.addWidget(self.name_input)

        # Capacité et Catégorie
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        capa_box = QVBoxLayout()
        capa_label = QLabel("Capacité (places) :")
        capa_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        capa_box.addWidget(capa_label)
        self.capacity_input = QSpinBox()
        self.capacity_input.setRange(1, 500)
        self.capacity_input.setValue(24)
        capa_box.addWidget(self.capacity_input)
        row1.addLayout(capa_box)

        cat_box = QVBoxLayout()
        cat_label = QLabel("Catégorie :")
        cat_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        cat_box.addWidget(cat_label)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["informatique", "traditionnelle"])
        cat_box.addWidget(self.category_combo)
        row1.addLayout(cat_box)

        form_layout.addLayout(row1)

        # Étage et Code d'accès
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        stage_box = QVBoxLayout()
        stage_label = QLabel("Étage :")
        stage_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        stage_box.addWidget(stage_label)
        self.stage_input = QLineEdit()
        self.stage_input.setPlaceholderText("Ex: 1er, 2e, RDC")
        self.stage_input.setText("1er")
        stage_box.addWidget(self.stage_input)
        row2.addLayout(stage_box)

        code_box = QVBoxLayout()
        code_label = QLabel("Code d'accès (optionnel) :")
        code_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        code_box.addWidget(code_label)
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("4 caractères (ex: 4521)")
        self.code_input.setMaxLength(4)
        code_box.addWidget(self.code_input)
        row2.addLayout(code_box)

        form_layout.addLayout(row2)

        # Bâtiment
        bldg_label = QLabel("Bâtiment :")
        bldg_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        form_layout.addWidget(bldg_label)
        self.building_combo = QComboBox()
        buildings = self.building_repo.get_all()
        if buildings:
            for b in buildings:
                self.building_combo.addItem(f"{b.name} (ID: {b.id_building})", b.id_building)
        else:
            self.building_combo.addItem("Bâtiment par défaut (ID: 1)", 1)
        form_layout.addWidget(self.building_combo)

        main_layout.addWidget(card)

        # Erreur
        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)

        # Boutons
        btns = QHBoxLayout()
        btns.setSpacing(12)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)

        btns.addStretch()

        submit_btn = QPushButton("Ajouter la salle")
        submit_btn.setObjectName("submitBtn")
        submit_btn.clicked.connect(self._on_submit)
        btns.addWidget(submit_btn)

        main_layout.addLayout(btns)

    def _show_error(self, msg: str):
        self.error_label.setText(msg)
        self.error_label.show()

    def _on_submit(self):
        name = self.name_input.text().strip()
        if len(name) < 3:
            self._show_error("Le nom de la salle doit contenir au moins 3 caractères.")
            return

        stage = self.stage_input.text().strip()
        if not stage:
            self._show_error("L'étage doit être spécifié.")
            return

        code = self.code_input.text().strip() or None
        if code and len(code) != 4:
            self._show_error("Le code d'accès doit comporter exactement 4 caractères s'il est renseigné.")
            return

        building_id = self.building_combo.currentData() or 1

        self.classroom_data = {
            "name": name,
            "capacity": self.capacity_input.value(),
            "category": self.category_combo.currentText(),
            "stage": stage,
            "code_access": code,
            "id_building": building_id,
            "floor_id": 1,
        }
        self.accept()

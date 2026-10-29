# Projet-CDA — Réservation de salles

## Présentation

Application de bureau développée en Python avec **PySide6** (Qt) et **SQLAlchemy** pour la gestion et la réservation de salles au sein d'un établissement.

Le projet suit une architecture **MVC (Modèle - Vue - Contrôleur)** claire, modulaire et conforme aux conventions et standards de l'écosystème Python et du titre professionnel Concepteur Développeur d'Applications (CDA).

---

## Fonctionnalités principales

### 1. Authentification & Sécurité
- **Connexion** avec vérification des identifiants et hachage sécurisé des mots de passe via `bcrypt`.
- **Inscription** avec formulaire complet (Nom, Prénom, Email, Genre, Rôle, Mot de passe).
- Validation stricte des données d'inscription via **Pydantic** (format email, robustesse du mot de passe).
- Gestion des rôles utilisateurs (*Administrateur*, *Gestionnaire*, *Enseignant*, *Étudiant*, *Technicien*, *Utilisateur*).
- Gestion de session utilisateur et bouton de déconnexion.

### 2. Tableau de bord interactif (Navigation par onglets)
- **🏢 Salles disponibles** :
  - Recherche instantanée par nom de salle.
  - Filtres par catégorie (*Informatique*, *Traditionnelle*) et par capacité minimale (*≥ 15*, *≥ 25*, *≥ 30 places*).
  - Cartes modernes affichant la capacité, l'étage, le code d'accès et le statut de disponibilité du jour (🟢 *Libre* ou 🟡 *Occupée sur certains créneaux*).
  - Bouton rapide d'actualisation des données.

- **📅 Réservation de salles** :
  - Boîte de dialogue modale dédiée pour chaque salle.
  - Sélection de la date (calendrier bloqué au minimum sur la date du jour).
  - Choix précis de la plage horaire (heure de début et heure de fin).
  - **Affichage en direct des créneaux déjà occupés** pour la date sélectionnée.
  - **Détection automatique des conflits de créneaux** (chevauchements horaires interdits et signalés).

- **📋 Mes réservations** :
  - Historique des réservations effectuées par l'utilisateur connecté.
  - Détail de chaque réservation (salle, date, horaires, badge de statut).
  - Possibilité d'**annuler une réservation** en un clic avec confirmation.

- **⚙️ Espace Administration** *(accessible aux rôles Administrateur et Gestionnaire)* :
  - **Ajout de nouvelle salle** via formulaire dédié (nom, capacité, type, étage, code d'accès, bâtiment).
  - **Suppression de salle** avec confirmation.

---

## Technologies utilisées

- **Langage** : Python 3.14+
- **Interface graphique** : PySide6 (Qt pour Python)
- **ORM & Accès aux données** : SQLAlchemy 2.0
- **Base de données** : MySQL / MariaDB avec le pilote `PyMySQL`
- **Validation des données** : Pydantic 2
- **Sécurité / Hachage** : bcrypt
- **Migrations & Schéma** : Alembic
- **Tests automatisés** : pytest (avec base SQLite en mémoire pour isolation)

---

## Prérequis

- Python 3.14 ou plus récent
- Un serveur MySQL ou MariaDB démarré (ex: Laragon, WAMP, XAMPP ou Docker)
- Gestionnaire de paquets `pip`

---

## Installation

Depuis le dossier `Projet-CDA` :

### Sous Windows (PowerShell) :

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Sous macOS ou Linux (Bash) :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration de la base de données

Copiez le fichier `.env.example` vers `.env` et adaptez les variables à votre installation locale :

```dotenv
DB_user=root
DB_password=
DB_name=resa-salle
DB_host=localhost
DB_port=3307
DB_driver=mysql+pymysql
```

> **Note :** La base indiquée par `DB_name` doit être créée sur votre serveur MySQL avant de démarrer l'application.

### Initialiser les tables et données de référence

Depuis le dossier `Projet-CDA` :

```powershell
# Créer les tables
python -c "import app.models; from app.database.init_db import init_db; init_db()"

# (Optionnel) Insérer des données initiales de test
python -m app.database.seeders.init_data
```

---

## Lancer l'application

Depuis le dossier `Projet-CDA`, vous pouvez lancer l'application via le point d'entrée principal :

```powershell
python main.py
```

Ou en mode module :

```powershell
python -m app
```

---

## Lancer les tests automatisés

Le projet inclut une suite de tests unitaires couvrant les repositories et la logique de détection des conflits de réservation (exécutée sur une base SQLite en mémoire pour ne pas altérer votre base de données réelle) :

```powershell
pytest
```

Ou en ciblant explicitement le dossier :

```powershell
pytest tests/
```

---

## Organisation du projet (Architecture MVC standard)

```text
Projet-CDA/
├── app/                        # Package principal de l'application
│   ├── controllers/            # Contrôleurs (logique métier reliant vues et données)
│   │   ├── dashboard_controller.py
│   │   └── login_controller.py
│   ├── database/               # Moteur de base de données et initialisation
│   │   ├── seeders/            # Scripts d'insertion de données de test
│   │   │   ├── buildings_seeder.py
│   │   │   ├── floors_seeder.py
│   │   │   ├── init_data.py
│   │   │   ├── roles_seeder.py
│   │   │   └── rooms_seeder.py
│   │   ├── base.py
│   │   ├── engine.py
│   │   └── init_db.py
│   ├── models/                 # Modèles SQLAlchemy (tables de la BDD)
│   │   ├── building.py
│   │   ├── classroom.py
│   │   ├── floor.py
│   │   ├── reservation.py
│   │   ├── role.py
│   │   └── user.py
│   ├── repositories/           # Couche d'accès aux données (requêtes CRUD)
│   │   ├── building_repository.py
│   │   ├── classroom_repository.py
│   │   ├── reservation_repository.py
│   │   └── user_repository.py
│   ├── ui/                     # Interfaces Qt compilées (.py générés depuis .ui)
│   │   └── Register_ui.py
│   ├── validators/             # Schémas de validation Pydantic
│   │   └── user_validator.py
│   ├── views/                  # Vues et composants graphiques PySide6
│   │   ├── add_classroom_dialog.py
│   │   ├── connexion.py
│   │   ├── dashboard.py
│   │   ├── register.py
│   │   └── reservation_dialog.py
│   ├── app.py                  # Initialisation et démarrage de l'application Qt
│   └── __main__.py             # Point d'entrée pour 'python -m app'
├── tests/                      # Tests unitaires automatisés (séparés du code applicatif)
│   ├── conftest.py
│   ├── test_reservation_repository.py
│   └── test_user_repository.py
├── .env.example                # Modèle de configuration des variables d'environnement
├── alembic.ini                 # Configuration des migrations de schéma Alembic
├── main.py                     # Point d'entrée exécutable (python main.py)
├── requirements.txt            # Dépendances du projet
└── README.md                   # Documentation complète du projet
```

# Projet-CDA — Réservation de salles

## Présentation

Application de bureau en cours de développement pour gérer des salles et leurs réservations. Le projet comprend notamment des écrans de connexion et d'inscription, un tableau de bord présentant les salles, ainsi que des modèles pour les utilisateurs, les rôles, les bâtiments, les étages, les salles et les réservations.

## Technologies

- Python 3.14 ou plus récent
- PySide6 pour l'interface graphique
- SQLAlchemy pour l'accès aux données
- MySQL avec PyMySQL
- Alembic, avec une configuration pour les migrations de schéma

## Prérequis

- Python 3.14+
- Un serveur MySQL accessible
- `pip`

## Installation

Depuis le dossier `Projet-CDA` :

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Sous macOS ou Linux, créez et activez l'environnement virtuel avec :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration de la base de données

Copiez `.env.example` vers `.env`, puis renseignez les paramètres de connexion MySQL. Les noms ci-dessous correspondent aux variables lues par l'application :

```dotenv
DB_user=root
DB_password=
DB_name=resa_salles
DB_host=localhost
DB_port=3307
DB_driver=mysql+pymysql
```

Adaptez l'utilisateur, le mot de passe et le port à votre installation. Le serveur doit être démarré et la base indiquée par `DB_name` doit exister avant de lancer l'application. Ne partagez pas votre fichier `.env` et n'y inscrivez pas de mot de passe réel dans le dépôt.

Une fois la base créée et les paramètres configurés, créez les tables définies par les modèles :

```powershell
python -c "import app.models; from app.database.init_db import init_db; init_db()"
```

Exécutez cette commande depuis `Projet-CDA`, avec l'environnement virtuel activé.

## Lancer l'application

Depuis `Projet-CDA` :

```powershell
python -m app
```

## Organisation du projet

```text
app/
  controllers/  Logique de liaison entre vues et données
  database/     Connexion, initialisation et données de référence
  models/       Modèles SQLAlchemy
  repositories/ Accès aux données
  tests/        Tests automatisés
  validators/   Validation des données
  views/        Interfaces PySide6
pages/          Autres écrans d'interface
requirements.txt
```

# Resa-salle

Dépôt contenant l'application de bureau pour la gestion et la réservation de salles **Projet-CDA**.

---

## Structure du dépôt

```text
Resa-salle/
├── Projet-CDA/                 # Code source complet de l'application
│   ├── app/                    # Architecture MVC (controllers, database, models, repositories, ui, views)
│   ├── tests/                  # Tests unitaires automatisés pytest (16 tests)
│   ├── main.py                 # Script de démarrage
│   ├── requirements.txt        # Dépendances Python
│   └── README.md               # Guide complet de l'application
└── README.md                   # Ce fichier de présentation
```

---

## Démarrage rapide

1. Rendez-vous dans le dossier du projet :
   ```powershell
   cd Projet-CDA
   ```

2. Installez les dépendances et configurez la base de données :
   - Suivez les instructions dans [**`Projet-CDA/README.md`**](./Projet-CDA/README.md) pour renseigner votre `.env`.

3. Lancement de l'application :
   ```powershell
   python main.py
   ```

4. Lancement de la suite de tests :
   ```powershell
   pytest
   ```

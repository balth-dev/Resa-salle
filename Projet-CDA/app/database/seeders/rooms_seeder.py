from app.database.engine import SessionLocal
from app.models.building import Building
from app.models.classroom import Classroom

def seed_rooms():
    with SessionLocal() as session:
        if session.query(Classroom).count() > 0:
            print("Changement annulé : les salles existent déjà dans la base de données.")
            return

        bat_k1 = session.query(Building).filter_by(name="K1").first()
        bat_k2 = session.query(Building).filter_by(name="K2").first()

        if not bat_k1 or not bat_k2:
            print("Erreur : les bâtiments K1 ou K2 sont introuvables.")
            print("Veuillez exécuter buildings_seeder.py avant ce script.")
            return

        rooms_to_add = [
            Classroom(name="Salle K1-01", capacity=30, category="traditionnelle", stage="RDC", id_building=bat_k1.id_building),
            Classroom(name="Salle K1-02", capacity=24, category="traditionnelle", stage="RDC", id_building=bat_k1.id_building),
            Classroom(name="Salle K1-101", capacity=35, category="informatique", stage="1er", id_building=bat_k1.id_building),
            Classroom(name="Salle K2-01", capacity=20, category="traditionnelle", stage="RDC", id_building=bat_k2.id_building),
        ]

        session.add_all(rooms_to_add)
        session.commit()
        print("Salles de cours semées avec succès.")

if __name__ == "__main__":
    seed_rooms()

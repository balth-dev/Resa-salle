from app.database import engine as db_engine
from app.models.building import Building

class BuildingRepository:
    def get_all(self) -> list[Building]:
        with db_engine.SessionLocal() as session:
            buildings = session.query(Building).all()
            for b in buildings:
                session.expunge(b)
            return buildings

    def get_by_id(self, building_id: int) -> Building | None:
        with db_engine.SessionLocal() as session:
            building = session.query(Building).filter(Building.id_building == building_id).first()
            if building:
                session.expunge(building)
            return building


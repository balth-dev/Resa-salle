from sqlalchemy import BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class Classroom(Base):
    __tablename__ = "classroom"

    id_classroom: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # informatique ou traditionnelle
    stage: Mapped[str] = mapped_column("Stage", String(50), nullable=False)
    code_access: Mapped[str] = mapped_column(String(4), unique=True, nullable=True)
    id_building: Mapped[int] = mapped_column(BigInteger, ForeignKey("building.id_building"), nullable=False)

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vaga_titulo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    vaga_texto: Mapped[str] = mapped_column(Text)
    curriculo_texto: Mapped[str] = mapped_column(Text)

    score: Mapped[float] = mapped_column(Float)
    similaridade_texto: Mapped[float] = mapped_column(Float)
    cobertura_competencias: Mapped[float] = mapped_column(Float)

    competencias_encontradas: Mapped[list[str]] = mapped_column(JSON, default=list)
    competencias_faltantes: Mapped[list[str]] = mapped_column(JSON, default=list)
    sugestoes: Mapped[list[str]] = mapped_column(JSON, default=list)
    fonte_sugestoes: Mapped[str] = mapped_column(String(20))  # "llm" ou "regras"

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

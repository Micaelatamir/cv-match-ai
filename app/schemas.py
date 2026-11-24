from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisCreate(BaseModel):
    vaga_titulo: str | None = Field(default=None, max_length=200, examples=["Desenvolvedor Backend Júnior"])
    vaga_texto: str = Field(min_length=30, description="Descrição completa da vaga")
    curriculo_texto: str = Field(min_length=30, description="Texto do currículo")
    usar_ia: bool = Field(default=True, description="Gerar sugestões com LLM (se configurado)")


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vaga_titulo: str | None
    score: float = Field(description="Compatibilidade geral de 0 a 100")
    similaridade_texto: float = Field(description="Similaridade TF-IDF entre os textos (0 a 100)")
    cobertura_competencias: float = Field(description="% das competências da vaga presentes no currículo")
    competencias_encontradas: list[str]
    competencias_faltantes: list[str]
    sugestoes: list[str]
    fonte_sugestoes: str
    criado_em: datetime


class AnalysisSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vaga_titulo: str | None
    score: float
    criado_em: datetime

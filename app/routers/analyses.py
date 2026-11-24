from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis
from app.schemas import AnalysisCreate, AnalysisOut, AnalysisSummary
from app.services.llm import generate_suggestions
from app.services.matcher import analyze
from app.services.pdf import extract_text_from_pdf

router = APIRouter(prefix="/analyses", tags=["Análises"])

MAX_PDF_BYTES = 5 * 1024 * 1024  # 5 MB, currículo nenhum passa disso


def _create_analysis(
    db: Session, vaga_titulo: str | None, vaga_texto: str, curriculo_texto: str, usar_ia: bool
) -> Analysis:
    result = analyze(vaga_texto, curriculo_texto)
    sugestoes, fonte = generate_suggestions(vaga_texto, curriculo_texto, result, usar_ia)

    analysis = Analysis(
        vaga_titulo=vaga_titulo,
        vaga_texto=vaga_texto,
        curriculo_texto=curriculo_texto,
        score=result.score,
        similaridade_texto=result.similaridade_texto,
        cobertura_competencias=result.cobertura_competencias,
        competencias_encontradas=result.competencias_encontradas,
        competencias_faltantes=result.competencias_faltantes,
        sugestoes=sugestoes,
        fonte_sugestoes=fonte,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.post("", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
def create_analysis(payload: AnalysisCreate, db: Session = Depends(get_db)):
    """Compara o texto do currículo com o texto da vaga."""
    return _create_analysis(
        db, payload.vaga_titulo, payload.vaga_texto, payload.curriculo_texto, payload.usar_ia
    )


@router.post("/pdf", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_analysis_from_pdf(
    curriculo: UploadFile = File(..., description="Currículo em PDF"),
    vaga_texto: str = Form(..., min_length=30),
    vaga_titulo: str | None = Form(default=None),
    usar_ia: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    """Mesma coisa, mas o currículo vem em PDF."""
    # alguns navegadores mandam PDF como octet-stream, por isso aceito os dois
    if curriculo.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Envie o currículo em PDF.")

    data = await curriculo.read()
    if len(data) > MAX_PDF_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "O PDF deve ter no máximo 5 MB.")

    try:
        curriculo_texto = extract_text_from_pdf(data)
    except Exception:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Não foi possível ler o PDF.")

    # PDF escaneado vira imagem e não tem texto pra extrair
    if len(curriculo_texto) < 30:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "O PDF não tem texto legível (pode ser uma imagem escaneada).",
        )

    return _create_analysis(db, vaga_titulo, vaga_texto, curriculo_texto, usar_ia)


@router.get("", response_model=list[AnalysisSummary])
def list_analyses(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Histórico, das mais novas pras mais antigas."""
    stmt = select(Analysis).order_by(Analysis.criado_em.desc(), Analysis.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Análise não encontrada.")
    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    analysis = db.get(Analysis, analysis_id)
    if analysis is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Análise não encontrada.")
    db.delete(analysis)
    db.commit()

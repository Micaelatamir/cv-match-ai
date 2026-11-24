from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.skills import extract_skills, normalize

# Dei mais peso pras competências porque é o que o ATS e o recrutador olham primeiro.
# A similaridade do texto entra mais como desempate.
PESO_COMPETENCIAS = 0.7
PESO_SIMILARIDADE = 0.3

STOPWORDS_PT = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas",
    "um", "uma", "uns", "umas", "para", "por", "com", "sem", "que", "se", "ao", "aos", "ou",
    "como", "mais", "muito", "sua", "seu", "suas", "seus", "ser", "sera", "ter", "tem", "sao",
    "voce", "nossa", "nosso", "vaga", "empresa", "pelo", "pela", "entre", "sobre", "ate",
    "the", "and", "or", "of", "to", "in", "for", "with", "on", "is", "are", "you", "we",
}


@dataclass
class MatchResult:
    score: float
    similaridade_texto: float
    cobertura_competencias: float
    competencias_encontradas: list[str]
    competencias_faltantes: list[str]


def text_similarity(texto_a: str, texto_b: str) -> float:
    # TF-IDF + cosseno, volta um valor entre 0 e 1
    vectorizer = TfidfVectorizer(
        preprocessor=normalize,
        stop_words=list(STOPWORDS_PT),
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b[\w#+.]{2,}\b",
    )
    try:
        matriz = vectorizer.fit_transform([texto_a, texto_b])
    except ValueError:  # acontece quando o texto vem vazio ou só com stopword
        return 0.0
    return float(cosine_similarity(matriz[0], matriz[1])[0][0])


def analyze(vaga_texto: str, curriculo_texto: str) -> MatchResult:
    skills_vaga = extract_skills(vaga_texto)
    skills_cv = extract_skills(curriculo_texto)

    encontradas = sorted(skills_vaga & skills_cv)
    faltantes = sorted(skills_vaga - skills_cv)

    cobertura = len(encontradas) / len(skills_vaga) if skills_vaga else 0.0
    similaridade = text_similarity(vaga_texto, curriculo_texto)

    if skills_vaga:
        score = PESO_COMPETENCIAS * cobertura + PESO_SIMILARIDADE * similaridade
    else:
        # se não achei nenhuma competência na vaga, fico só com a similaridade
        score = similaridade

    return MatchResult(
        score=round(score * 100, 1),
        similaridade_texto=round(similaridade * 100, 1),
        cobertura_competencias=round(cobertura * 100, 1),
        competencias_encontradas=encontradas,
        competencias_faltantes=faltantes,
    )

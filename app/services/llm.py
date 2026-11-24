# Sugestões pro currículo.
# Uso o formato /chat/completions da OpenAI porque quase todo provedor aceita
# (Groq, OpenRouter, Ollama...). Se não tiver chave ou a chamada der erro,
# volta pras sugestões por regra, assim a API nunca fica sem resposta.

import json
import logging

import httpx

from app.config import settings
from app.services.matcher import MatchResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Você é um recrutador técnico experiente em vagas de tecnologia no Brasil. "
    "Analise o currículo em relação à vaga e devolva de 3 a 6 sugestões objetivas "
    "para aumentar as chances de aprovação em filtros ATS e com recrutadores. "
    "Nunca sugira inventar experiências. Se faltar uma competência, sugira destacá-la "
    "apenas caso a pessoa realmente a tenha, ou indique como desenvolvê-la. "
    'Responda SOMENTE com JSON no formato {"sugestoes": ["...", "..."]}.'
)


def rule_based_suggestions(result: MatchResult) -> list[str]:
    sugestoes: list[str] = []
    if result.competencias_faltantes:
        lista = ", ".join(result.competencias_faltantes[:6])
        sugestoes.append(
            f"A vaga pede {lista}. Se você tem experiência com algum desses itens, "
            "cite-o com as mesmas palavras usadas na vaga."
        )
    if result.cobertura_competencias < 50:
        sugestoes.append(
            "Menos da metade das competências da vaga aparece no currículo. "
            "Avalie se a vaga é aderente ou adapte o resumo profissional para ela."
        )
    if result.similaridade_texto < 20:
        sugestoes.append(
            "O vocabulário do currículo está distante da vaga. Use termos da descrição "
            "da vaga no resumo e na descrição dos projetos."
        )
    if result.competencias_encontradas:
        sugestoes.append(
            "Destaque no topo do currículo as competências que já combinam com a vaga: "
            + ", ".join(result.competencias_encontradas[:6])
            + "."
        )
    sugestoes.append("Descreva cada projeto com o problema resolvido, as tecnologias e o resultado.")
    return sugestoes


def _parse_suggestions(content: str) -> list[str]:
    # às vezes o modelo devolve o json dentro de ```json ... ```, então limpo antes
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`").removeprefix("json").strip()
    data = json.loads(content)
    sugestoes = [str(s).strip() for s in data.get("sugestoes", []) if str(s).strip()]
    if not sugestoes:
        raise ValueError("Resposta do LLM sem sugestões")
    return sugestoes


def llm_suggestions(vaga_texto: str, curriculo_texto: str, result: MatchResult) -> list[str]:
    # aqui deixo o erro subir mesmo, quem trata é o generate_suggestions
    user_prompt = (
        f"VAGA:\n{vaga_texto}\n\nCURRÍCULO:\n{curriculo_texto}\n\n"
        f"Competências encontradas: {', '.join(result.competencias_encontradas) or 'nenhuma'}\n"
        f"Competências faltantes: {', '.join(result.competencias_faltantes) or 'nenhuma'}\n"
        f"Score calculado: {result.score}/100"
    )
    response = httpx.post(
        f"{settings.llm_base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": settings.llm_model,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=settings.llm_timeout_seconds,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return _parse_suggestions(content)


def generate_suggestions(
    vaga_texto: str, curriculo_texto: str, result: MatchResult, usar_ia: bool = True
) -> tuple[list[str], str]:
    # a fonte ("llm" ou "regras") vai junto pra dar pra saber de onde veio a sugestão
    if usar_ia and settings.llm_api_key:
        try:
            return llm_suggestions(vaga_texto, curriculo_texto, result), "llm"
        except Exception as exc:  # timeout, chave errada, json quebrado... tudo cai nas regras
            logger.warning("Falha ao gerar sugestões com LLM, usando regras: %s", exc)
    return rule_based_suggestions(result), "regras"

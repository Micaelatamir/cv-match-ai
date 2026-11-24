# Lista das competências que o analisador reconhece.
# A chave é o nome que aparece na resposta e a lista são os jeitos que
# o pessoal costuma escrever (postgres, springboot...). Tudo é comparado
# em minúsculo e sem acento, então não precisa repetir variações.

import re
import unicodedata

SKILLS: dict[str, list[str]] = {
    # Linguagens
    "Java": ["java"],
    "Python": ["python"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "C#": ["c#", "csharp"],
    "Go": ["golang"],
    "Kotlin": ["kotlin"],
    "PHP": ["php"],
    "SQL": ["sql"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    # Frameworks e bibliotecas
    "Spring Boot": ["spring boot", "springboot"],
    "Spring Security": ["spring security"],
    "Hibernate/JPA": ["hibernate", "jpa"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Node.js": ["node.js", "nodejs", "node"],
    "React": ["react", "react.js", "reactjs"],
    ".NET": [".net", "dotnet", "asp.net"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "LangChain": ["langchain"],
    # Bancos de dados
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "Oracle": ["oracle"],
    "SQL Server": ["sql server", "sqlserver"],
    # DevOps e nuvem
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "CI/CD": ["ci/cd", "ci cd", "github actions", "gitlab ci", "jenkins"],
    "Linux": ["linux"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Maven": ["maven"],
    "Gradle": ["gradle"],
    # Conceitos
    "APIs REST": ["rest", "restful", "api rest", "apis rest"],
    "Microsserviços": ["microsservicos", "microservicos", "microservices"],
    "Mensageria": ["kafka", "rabbitmq", "mensageria"],
    "Testes automatizados": ["testes unitarios", "testes automatizados", "junit", "pytest", "tdd"],
    "JWT": ["jwt"],
    "OAuth": ["oauth", "oauth2"],
    "Clean Code": ["clean code", "solid"],
    "Scrum/Ágil": ["scrum", "agil", "kanban"],
    # IA
    "Inteligência Artificial": ["inteligencia artificial", "ia", "artificial intelligence"],
    "Machine Learning": ["machine learning", "aprendizado de maquina", "ml"],
    "LLMs": ["llm", "llms", "large language model", "modelos de linguagem"],
    "OpenAI API": ["openai", "chatgpt", "gpt"],
    "NLP": ["nlp", "processamento de linguagem natural"],
    "Automação": ["automacao", "automation", "rpa"],
    # Idiomas
    "Inglês": ["ingles", "english"],
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def _pattern(alias: str) -> re.Pattern[str]:
    # \b não funciona bem com c# e .net, então fiz a borda na mão.
    # O ponto antes é pra não pegar o "js" de "node.js" como JavaScript.
    return re.compile(rf"(?<![a-z0-9.]){re.escape(alias)}(?![a-z0-9])")


_COMPILED: dict[str, list[re.Pattern[str]]] = {
    name: [_pattern(normalize(a)) for a in aliases] for name, aliases in SKILLS.items()
}


def extract_skills(text: str) -> set[str]:
    norm = normalize(text)
    return {name for name, patterns in _COMPILED.items() if any(p.search(norm) for p in patterns)}

# CV Match AI

API que compara um currículo com uma vaga, dá uma nota de compatibilidade de 0 a 100, mostra quais competências da vaga estão faltando e sugere melhorias usando IA.

## Por que eu fiz esse projeto

Passei muito tempo mandando currículo sem receber retorno. Fui pesquisar e descobri que boa parte dos currículos é descartada por filtros automáticos (ATS) antes de alguém ler. Então resolvi construir uma ferramenta pra entender como esses filtros enxergam um currículo e pra adaptar o meu a cada vaga antes de me candidatar.

Hoje eu uso o CV Match AI nas minhas próprias candidaturas.

## O que ele faz

- Calcula uma **nota de compatibilidade** entre o currículo e a vaga
- Lista as **competências encontradas** e as que **estão faltando**
- Gera **sugestões de melhoria com um LLM** (funciona com OpenAI, Groq, OpenRouter, Ollama ou qualquer API no mesmo formato)
- Se a IA não estiver configurada ou sair do ar, **continua funcionando** com sugestões por regras
- Aceita o currículo em **texto ou em PDF**
- Salva o **histórico das análises** no PostgreSQL
- Tem um **script de automação** que compara o currículo com várias vagas de uma vez e gera um ranking em CSV

## Tecnologias

- **Python 3.12** e **FastAPI**
- **PostgreSQL** com **SQLAlchemy 2.0**
- **scikit-learn** (TF-IDF e similaridade de cosseno)
- **httpx** pra integração com o LLM
- **pypdf** pra ler os PDFs
- **Docker** e **Docker Compose**
- **pytest** e **GitHub Actions**

## Como a nota é calculada

A nota junta duas coisas:

```
nota = 70% cobertura de competências + 30% similaridade do texto
```

- **Cobertura de competências:** quantas das tecnologias que a vaga pede aparecem no currículo. Dei mais peso pra essa parte porque é o que o ATS e o recrutador olham primeiro.
- **Similaridade do texto:** transformo a vaga e o currículo em vetores TF-IDF e comparo os dois com similaridade de cosseno. Isso mede o quanto o vocabulário dos dois textos se parece.

Pra reconhecer as competências, montei um catálogo com mais de 60 tecnologias e as variações mais comuns de escrita (`postgres` → PostgreSQL, `springboot` → Spring Boot), comparando tudo sem acento e em minúsculo.

## Estrutura

```
app/
├── main.py              # aplicação FastAPI
├── config.py            # configurações (.env)
├── database.py          # conexão com o banco
├── models.py            # tabela de análises
├── schemas.py           # validação de entrada e saída
├── routers/
│   └── analyses.py      # rotas da API
└── services/
    ├── skills.py        # catálogo e extração de competências
    ├── matcher.py       # cálculo da nota
    ├── llm.py           # sugestões com LLM + fallback
    └── pdf.py           # leitura de PDF
scripts/
└── analisar_lote.py     # ranking de várias vagas
tests/                   # testes
```

## Como rodar

### Com Docker

```bash
cp .env.example .env
docker compose up --build
```

A documentação da API (Swagger) fica em **http://localhost:8000/docs**.

### Sem Docker

Precisa de Python 3.12+ e um PostgreSQL rodando.

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # ajuste o DATABASE_URL
uvicorn app.main:app --reload
```

### Ligando a IA

Sem chave, a API usa as sugestões por regras. Pra usar um LLM, é só preencher no `.env`:

```env
LLM_API_KEY=sua-chave
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

Eu uso a Groq, que tem plano gratuito. Pra trocar de provedor, basta mudar a URL e o modelo.

## Rotas

| Método | Rota | O que faz |
|---|---|---|
| `POST` | `/analyses` | Analisa currículo e vaga em texto |
| `POST` | `/analyses/pdf` | Analisa um currículo em PDF |
| `GET` | `/analyses` | Lista o histórico (com `limit` e `offset`) |
| `GET` | `/analyses/{id}` | Mostra uma análise |
| `DELETE` | `/analyses/{id}` | Apaga uma análise |
| `GET` | `/health` | Status da API |

### Exemplo

```bash
curl -X POST http://localhost:8000/analyses \
  -H "Content-Type: application/json" \
  -d '{
    "vaga_titulo": "Backend Java Júnior",
    "vaga_texto": "Requisitos: Java, Spring Boot, APIs REST, PostgreSQL, Docker. Desejável: Kafka e JUnit.",
    "curriculo_texto": "Desenvolvedora backend com Java, Spring Boot, PostgreSQL, Docker e APIs REST."
  }'
```

Resposta (resumida):

```json
{
  "id": 1,
  "score": 62.4,
  "cobertura_competencias": 71.4,
  "competencias_encontradas": ["APIs REST", "Docker", "Java", "PostgreSQL", "Spring Boot"],
  "competencias_faltantes": ["Mensageria", "Testes automatizados"],
  "sugestoes": ["..."],
  "fonte_sugestoes": "llm"
}
```

Com PDF:

```bash
curl -X POST http://localhost:8000/analyses/pdf \
  -F "curriculo=@meu_curriculo.pdf" \
  -F "vaga_texto=Requisitos: Python, FastAPI, SQL e Git..."
```

## Ranking de vagas

Essa é a parte que eu mais uso. Salvo cada vaga num `.txt` dentro de uma pasta e rodo:

```bash
python -m scripts.analisar_lote --curriculo meu_curriculo.pdf --vagas exemplos/vagas --saida ranking.csv
```

```
3 vagas analisadas. Ranking salvo em ranking.csv

 1. backend_java_junior                       57.6/100
 2. estagio_python_ia                         19.9/100
 3. fullstack_node_react                       7.6/100
```

Assim eu vejo em quais vagas vale mais a pena me candidatar e o que preciso destacar em cada uma. O CSV abre direto no Excel.

## Testes

```bash
pytest -q
```

Os testes usam SQLite em memória e simulam o LLM, então rodam rápido e sem gastar crédito de API. O GitHub Actions roda tudo a cada push.

## Próximos passos

- Deixar o usuário cadastrar competências próprias no catálogo
- Gerar uma versão do resumo profissional adaptada pra cada vaga
- Usar Alembic pras migrações do banco

---

Feito por **Micaela Tamires** · [LinkedIn](https://www.linkedin.com/in/micaela-tamires-aa320b312/) · [GitHub](https://github.com/Micaelatamir)

# Script que eu uso pra decidir em quais vagas vale a pena me candidatar.
# Salvo cada vaga num .txt dentro de uma pasta e rodo:
#
#   python -m scripts.analisar_lote --curriculo meu_cv.pdf --vagas vagas/ --saida ranking.csv
#
# Gera um CSV com as vagas da mais compatível pra menos compatível.
# Não usa banco, roda direto.

import argparse
import csv
import sys
from pathlib import Path

from app.services.matcher import analyze
from app.services.pdf import extract_text_from_pdf


def ler_curriculo(caminho: Path) -> str:
    if caminho.suffix.lower() == ".pdf":
        return extract_text_from_pdf(caminho.read_bytes())
    return caminho.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ranking de vagas por compatibilidade com o currículo.")
    parser.add_argument("--curriculo", required=True, type=Path, help="Currículo em .pdf ou .txt")
    parser.add_argument("--vagas", required=True, type=Path, help="Pasta com uma vaga por arquivo .txt")
    parser.add_argument("--saida", type=Path, default=Path("ranking_vagas.csv"), help="Arquivo CSV de saída")
    args = parser.parse_args(argv)

    if not args.curriculo.is_file():
        print(f"Currículo não encontrado: {args.curriculo}", file=sys.stderr)
        return 1
    arquivos = sorted(args.vagas.glob("*.txt")) if args.vagas.is_dir() else []
    if not arquivos:
        print(f"Nenhum arquivo .txt encontrado em: {args.vagas}", file=sys.stderr)
        return 1

    curriculo = ler_curriculo(args.curriculo)
    linhas = []
    for arquivo in arquivos:
        resultado = analyze(arquivo.read_text(encoding="utf-8"), curriculo)
        linhas.append(
            {
                "vaga": arquivo.stem,
                "score": resultado.score,
                "cobertura_competencias": resultado.cobertura_competencias,
                "similaridade_texto": resultado.similaridade_texto,
                "competencias_faltantes": ", ".join(resultado.competencias_faltantes),
            }
        )

    linhas.sort(key=lambda linha: linha["score"], reverse=True)

    # utf-8-sig pro Excel abrir com acento certinho
    with args.saida.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        writer.writeheader()
        writer.writerows(linhas)

    print(f"{len(linhas)} vagas analisadas. Ranking salvo em {args.saida}\n")
    for posicao, linha in enumerate(linhas, start=1):
        print(f"{posicao:>2}. {linha['vaga']:<40} {linha['score']:>5}/100")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

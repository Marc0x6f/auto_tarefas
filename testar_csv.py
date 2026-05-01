import sys
import unicodedata
import pandas as pd
from leitor_csv import (
    ler_csv_sed,
    converter_nota_para_escala_10,
    remover_duplicatas_maior_nota,
)

def remover_acentos(texto):
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

def testar_csv(caminho):
    print(f"\nArquivo: {caminho}\n")

    try:
        df = ler_csv_sed(caminho)
        df = converter_nota_para_escala_10(df)
        df = remover_duplicatas_maior_nota(df)
    except ValueError as e:
        print(f"[ERRO] {e}")
        sys.exit(1)

    print(f"{'#':<4} {'Nome (buscado no site)':<40} {'Nota enviada'}")
    print("-" * 62)

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        nome_original = row["Nome do Aluno"]
        nome_busca = remover_acentos(nome_original)
        nota = str(round(row["Nota (%)"], 1)).replace(".", ",")
        print(f"{i:<4} {nome_busca:<40} {nota}")

    print("-" * 62)
    print(f"\nTotal de alunos que receberao nota: {len(df)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        caminho = input("Caminho do arquivo CSV: ").strip().strip('"')
    else:
        caminho = sys.argv[1]

    testar_csv(caminho)

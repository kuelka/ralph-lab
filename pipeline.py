"""Pipeline de vendas: join de vendas.csv com lojas.csv."""
import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VENDAS = RAIZ / "vendas.csv"
LOJAS = RAIZ / "lojas.csv"
VENDAS_LOJAS = RAIZ / "vendas_lojas.csv"
VENDAS_ORFAS = RAIZ / "vendas_orfas.csv"


def ler_csv(caminho):
    with open(caminho, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ler_vendas(caminho=VENDAS):
    vendas = ler_csv(caminho)
    for v in vendas:
        v["receita_brl"] = float(v["receita_brl"])
    return vendas


def ler_lojas(caminho=LOJAS):
    return {loja["id_loja"]: loja for loja in ler_csv(caminho)}


def juntar(vendas, lojas):
    """Inner join por id_loja. Retorna (vendas_com_loja, vendas_orfas)."""
    juntas, orfas = [], []
    for v in vendas:
        loja = lojas.get(v["id_loja"])
        if loja is None:
            orfas.append(v)
        else:
            juntas.append({**v, **{k: val for k, val in loja.items() if k != "id_loja"}})
    return juntas, orfas


def escrever_csv(caminho, linhas, colunas):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        w.writerows(linhas)


def main():
    vendas = ler_vendas()
    lojas = ler_lojas()
    juntas, orfas = juntar(vendas, lojas)
    colunas_vendas = list(vendas[0].keys())
    colunas_lojas = [c for c in next(iter(lojas.values())).keys() if c != "id_loja"]
    escrever_csv(VENDAS_LOJAS, juntas, colunas_vendas + colunas_lojas)
    escrever_csv(VENDAS_ORFAS, orfas, colunas_vendas)
    return juntas, orfas


if __name__ == "__main__":
    juntas, orfas = main()
    print(f"join: {len(juntas)} linhas, receita {sum(v['receita_brl'] for v in juntas):.2f}")
    print(f"orfas: {len(orfas)} linhas, receita {sum(v['receita_brl'] for v in orfas):.2f}")

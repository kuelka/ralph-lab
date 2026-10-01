"""Pipeline de vendas: join de vendas.csv com lojas.csv, pivot regiao x mes e index.html."""
import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VENDAS = RAIZ / "vendas.csv"
LOJAS = RAIZ / "lojas.csv"
VENDAS_LOJAS = RAIZ / "vendas_lojas.csv"
VENDAS_ORFAS = RAIZ / "vendas_orfas.csv"
PIVOT_RECEITA = RAIZ / "pivot_receita.csv"
INDEX_HTML = RAIZ / "index.html"
MESES = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]


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


def pivotar(juntas):
    """Receita por regiao x mes (floats sem arredondar), regioes em ordem alfabetica."""
    regioes = sorted({v["regiao"] for v in juntas})
    pivot = {r: {m: 0.0 for m in MESES} for r in regioes}
    for v in juntas:
        pivot[v["regiao"]][v["data"][:7]] += v["receita_brl"]
    return pivot


def escrever_pivot(caminho, pivot):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["regiao"] + MESES)
        for regiao, meses in pivot.items():
            w.writerow([regiao] + [f"{meses[m]:.2f}" for m in MESES])


def ler_pivot(caminho=PIVOT_RECEITA):
    """Le pivot_receita.csv como dict regiao -> lista de floats na ordem de MESES."""
    return {l["regiao"]: [float(l[m]) for m in MESES] for l in ler_csv(caminho)}


def brl(valor):
    """Formata numero como R$ 1.234,56."""
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def conclusao(pivot, orfas, lojas_sem_vendas):
    totais = {r: sum(v) for r, v in pivot.items()}
    lider = max(totais, key=totais.get)
    total = sum(totais.values())
    orfas_total = sum(v["receita_brl"] for v in orfas)
    ids_orfas = ", ".join(sorted({v["id_loja"] for v in orfas}))
    sem_vendas = "; ".join(f"loja {l['id_loja']} ({l['nome_loja']}/{l['uf']}, regiao {l['regiao']})"
                           for l in lojas_sem_vendas)
    regioes_afetadas = sorted({l["regiao"] for l in lojas_sem_vendas})
    texto = (
        f"No primeiro semestre de 2026 a receita somou {brl(total)} e a regiao lider foi o {lider}, "
        f"com {brl(totais[lider])}. Ficaram fora da analise {len(orfas)} vendas ({brl(orfas_total)}) "
        f"registradas com loja inexistente (id_loja {ids_orfas}), que nao puderam ser atribuidas a nenhuma regiao."
    )
    if lojas_sem_vendas:
        texto += (
            f" Alem disso, a {sem_vendas} nao teve vendas no periodo, entao o "
            f"{', '.join(regioes_afetadas)} aparece menor que a operacao real da regiao."
        )
    return texto


def gerar_html(caminho, pivot, orfas, lojas_sem_vendas):
    datasets = [{"label": r, "data": [round(v, 2) for v in valores]} for r, valores in pivot.items()]
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Receita mensal por regiao - 1o semestre 2026</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.5}}</style>
</head>
<body>
<h1>Receita mensal por regiao (R$)</h1>
<canvas id="grafico"></canvas>
<p>{conclusao(pivot, orfas, lojas_sem_vendas)}</p>
<script>
new Chart(document.getElementById("grafico"), {{
  type: "line",
  data: {{ labels: {json.dumps(MESES)}, datasets: {json.dumps(datasets, ensure_ascii=False)} }},
  options: {{ scales: {{ y: {{ beginAtZero: true }} }} }}
}});
</script>
</body>
</html>
"""
    caminho.write_text(html, encoding="utf-8")


def main():
    vendas = ler_vendas()
    lojas = ler_lojas()
    juntas, orfas = juntar(vendas, lojas)
    colunas_vendas = list(vendas[0].keys())
    colunas_lojas = [c for c in next(iter(lojas.values())).keys() if c != "id_loja"]
    escrever_csv(VENDAS_LOJAS, juntas, colunas_vendas + colunas_lojas)
    escrever_csv(VENDAS_ORFAS, orfas, colunas_vendas)
    escrever_pivot(PIVOT_RECEITA, pivotar(juntas))
    ids_com_venda = {v["id_loja"] for v in juntas}
    lojas_sem_vendas = [l for i, l in lojas.items() if i not in ids_com_venda]
    gerar_html(INDEX_HTML, ler_pivot(), orfas, lojas_sem_vendas)
    return juntas, orfas


if __name__ == "__main__":
    juntas, orfas = main()
    print(f"join: {len(juntas)} linhas, receita {sum(v['receita_brl'] for v in juntas):.2f}")
    print(f"orfas: {len(orfas)} linhas, receita {sum(v['receita_brl'] for v in orfas):.2f}")

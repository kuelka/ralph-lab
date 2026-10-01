import csv
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline  # noqa: E402


@pytest.fixture(scope="module")
def saida():
    pipeline.main()


def ler(caminho):
    with open(caminho, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_join_tem_420_linhas(saida):
    linhas = ler(pipeline.VENDAS_LOJAS)
    assert len(linhas) == 420
    assert "receita_brl" in linhas[0] and "regiao" in linhas[0]


def test_join_receita_total(saida):
    total = sum(float(l["receita_brl"]) for l in ler(pipeline.VENDAS_LOJAS))
    assert total == pytest.approx(931274.06, abs=0.50)


def test_receita_lida_como_float():
    assert all(isinstance(v["receita_brl"], float) for v in pipeline.ler_vendas())


def test_tres_vendas_orfas(saida):
    orfas = ler(pipeline.VENDAS_ORFAS)
    assert len(orfas) == 3
    assert all(o["id_loja"] == "999" for o in orfas)
    assert sum(float(o["receita_brl"]) for o in orfas) == pytest.approx(8120.00, abs=0.01)


def test_pivot_forma_e_cabecalho(saida):
    with open(pipeline.PIVOT_RECEITA, newline="", encoding="utf-8") as f:
        linhas = list(csv.reader(f))
    assert linhas[0] == ["regiao", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
    assert [l[0] for l in linhas[1:]] == ["Centro-Oeste", "Nordeste", "Sudeste", "Sul"]
    assert all(len(l) == 7 for l in linhas)
    for l in linhas[1:]:
        for valor in l[1:]:
            assert re.fullmatch(r"\d+\.\d{2}", valor)


def test_pivot_totais(saida):
    pivot = ler(pipeline.PIVOT_RECEITA)
    total = sum(float(l[m]) for l in pivot for m in pipeline.MESES)
    assert total == pytest.approx(931274.06, abs=0.50)
    sudeste = next(l for l in pivot if l["regiao"] == "Sudeste")
    assert sum(float(sudeste[m]) for m in pipeline.MESES) == pytest.approx(265077.49, abs=0.50)

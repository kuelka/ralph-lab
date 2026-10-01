# PRD: Pipeline de vendas — do CSV ao gráfico

## Introdução

Construir um pipeline em Python que junta `vendas.csv` com `lojas.csv`, calcula a receita por região e mês e publica uma página estática com um gráfico e uma conclusão. Os dados têm duas armadilhas propositais: 3 vendas com `id_loja=999` (loja inexistente) e a loja 108 (Batel/PR), que não teve nenhuma venda.

## Objetivos

- Entregar o inner join `vendas_lojas.csv` com 420 linhas e receita total de R$ 931.274,06
- Entregar `pivot_receita.csv` (região × mês) cuja soma também dá 931274.06
- Entregar `index.html` com gráfico Chart.js e parágrafo de conclusão
- Tornar explícito, e não silencioso, o que ficou de fora do relatório

## Histórias de usuário

### US-001: Join de vendas com lojas
**Descrição:** Como analista, quero as vendas enriquecidas com os dados da loja para poder agrupar por região.

**Critérios de aceite:**
- [ ] Script `pipeline.py` lê `vendas.csv` e `lojas.csv` sem alterar os arquivos de origem
- [ ] `receita_brl` é lido como número (float), não como texto
- [ ] Inner join por `id_loja` salvo em `vendas_lojas.csv` na raiz, mantendo a coluna `receita_brl` com esse nome
- [ ] `vendas_lojas.csv` tem exatamente 420 linhas de dados e soma de `receita_brl` = 931274.06 (± 0,50)
- [ ] As 3 vendas órfãs (`id_loja` sem loja correspondente) são salvas em `vendas_orfas.csv` (soma R$ 8.120,00)
- [ ] Testes em `tests/test_pipeline.py` cobrem linhas do join, receita total e as 3 órfãs; `python -m pytest -q` passa

### US-002: Pivot receita por região × mês
**Descrição:** Como gestor, quero a receita mensal de cada região numa tabela.

**Critérios de aceite:**
- [ ] `pivot_receita.csv` na raiz com cabeçalho exato `regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06`
- [ ] 4 linhas de dados (Centro-Oeste, Nordeste, Sudeste, Sul), em ordem alfabética, 7 colunas
- [ ] Valores com ponto decimal e 2 casas, sem `R$` e sem separador de milhar; arredondar só ao escrever
- [ ] Soma de todas as células numéricas = 931274.06 (± 0,50); Sudeste soma 265077.49
- [ ] Testes de forma, cabeçalho e total do pivot; `python -m pytest -q` passa

### US-003: Página com gráfico e conclusão
**Descrição:** Como leitor do relatório, quero ver a receita mensal por região num gráfico e entender o que ficou de fora.

**Critérios de aceite:**
- [ ] `index.html` na raiz, gerado pelo pipeline a partir de `pivot_receita.csv`
- [ ] Gráfico Chart.js (via CDN) com uma série por região e os 6 meses no eixo X, dados embutidos no HTML
- [ ] Um `<p>` de conclusão com pelo menos 300 caracteres que cite a região líder, informe que 3 vendas (R$ 8.120,00) com loja inexistente ficaram fora e que a loja 108 (Batel/PR) não teve vendas, então o Sul aparece menor que a operação real
- [ ] Teste verifica que o HTML contém o gráfico e o parágrafo com 300+ caracteres; `python -m pytest -q` passa

## Requisitos funcionais

- FR-1: Inner join por `id_loja`; nunca apagar linhas dos CSVs de origem
- FR-2: Não inventar dados nem preencher lojas faltantes
- FR-3: Órfãs registradas em `vendas_orfas.csv`, não descartadas em silêncio
- FR-4: Os três entregáveis ficam na raiz do repo
- FR-5: A suíte `pytest` completa tem pelo menos 4 testes e fica verde

## Fora do escopo

- Corrigir os dados de origem ou adivinhar a loja das vendas órfãs
- Servidor web, banco de dados ou build de frontend

## Considerações técnicas

- Python 3 com pandas; rodar no Windows com `python`
- Trabalhar direto na branch `main`

## Métrica de sucesso

- Todos os valores de conferência batem: 420 linhas, R$ 931.274,06, Sudeste líder com R$ 265.077,49

from flask import Flask, render_template, request
from google.cloud import bigquery

app = Flask(__name__)


def conectar_bigquery():
    """Conectar-se ao BigQuery."""
    return bigquery.Client()


def consultar_pagina(client, tabela, pagina=1, resultados_por_pagina=5, coluna=None, direcao=None):
    """Consultar uma página específica da tabela com possibilidade de ordenação."""
    offset = (pagina - 1) * resultados_por_pagina
    query_select = f"""
        SELECT ticker, data_pregao, preco_fechamento
        FROM `{tabela}`
        """
    if coluna:
        query_select += f" ORDER BY {coluna} {direcao}"
    query_select += f"""
        LIMIT {resultados_por_pagina}
        OFFSET {offset}
    """
    query_job = client.query(query_select)
    dados_pagina = list(query_job.result())
    return dados_pagina


def obter_total_linhas(client, tabela):
    """Retorna o total de linhas na tabela."""
    consulta_total = f"""
        SELECT COUNT(*) AS total_linhas
        FROM `{tabela}`
    """
    total_linhas = list(client.query(consulta_total).result())[0].total_linhas
    return total_linhas


# Calcular o número total de páginas apenas uma vez
cliente_bigquery = conectar_bigquery()
tabela = 'precoacao-412114.tickers_pricing.tickers_prices'
resultados_por_pagina = 10
total_linhas = obter_total_linhas(cliente_bigquery, tabela)
total_paginas = (total_linhas + resultados_por_pagina - 1) // resultados_por_pagina


@app.route('/')
def index():
    pagina = int(request.args.get('pagina', 1))
    coluna = request.args.get('coluna')
    direcao = request.args.get('direcao', 'asc')

    # Consultar uma página específica com classificação opcional
    dados_pagina = consultar_pagina(cliente_bigquery, tabela, pagina, resultados_por_pagina, coluna, direcao)

    return render_template('asc_desc.html', dados=dados_pagina, pagina=pagina, total_paginas=total_paginas, coluna=coluna, direcao=direcao)


if __name__ == "__main__":
    app.run(debug=True)

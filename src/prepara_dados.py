# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Parte 2
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Síntese:
    Lê os CSVs brutos das estações do CGE (Centro de Gerenciamento de
    Emergências Climáticas da Prefeitura de São Paulo), recorta a janela
    temporal comum a todas as estações (01/01/2024 a 30/04/2024) e gera
    dados/estacoes_resumo.csv, com um registro por estação contendo as
    coordenadas e os atributos climáticos agregados na janela:
        - precipitação acumulada (mm)
        - temperatura média (°C)
        - umidade relativa média (%)
    Este script é executado apenas uma vez; o restante do projeto usa
    somente o CSV resumido (não depende dos dados brutos).

Uso:
    python src/prepara_dados.py <pasta_com_csvs_do_cge_2024>
"""

import glob
import os
import sys

import pandas as pd

INICIO_JANELA = "2024-01-01 00:00:00"
FIM_JANELA = "2024-04-30 23:50:00"

# Estações da rede: código do posto no CGE -> (rótulo, latitude, longitude).
# Coordenadas herdadas do levantamento feito no projeto de Iniciação
# Científica (grafo 003.graphml).
ESTACOES = {
    "1000880": ("Santana de Parnaiba", -23.436410, -46.909258),
    "515":     ("Pirituba", -23.479444, -46.730556),
    "509":     ("Freguesia do O", -23.486944, -46.693889),
    "510":     ("Santana/Tucuruvi", -23.477222, -46.607222),
    "540":     ("Vila Maria/Guilherme", -23.509167, -46.607222),
    "1000887": ("Penha", -23.521111, -46.523333),
    "1000862": ("Sao Miguel Paulista", -23.502778, -46.439167),
    "1000882": ("Itaim Paulista", -23.503333, -46.386111),
    "1000864": ("Itaquera", -23.535000, -46.454444),
    "1000844": ("Sao Mateus", -23.600000, -46.480556),
    "1000876": ("Maua", -23.667778, -46.460833),
    "400":     ("Riacho Grande", -23.778889, -46.528333),
    "1000300": ("Marsilac", -23.936389, -46.708611),
    "1000857": ("Parelheiros/Rodoanel", -23.682778, -46.711389),
    "846":     ("Capela do Socorro", -23.587778, -46.716667),
    "1000850": ("M Boi Mirim", -23.688611, -46.770556),
    "1000854": ("Campo Limpo", -23.632778, -46.766111),
    "1000848": ("Lapa", -23.524444, -46.705833),
    "1000635": ("Pinheiros", -23.565833, -46.689444),
    "503":     ("Se - CGE", -23.546111, -46.631944),
    "1000860": ("Mooca", -23.562778, -46.597778),
    "1000859": ("Vila Formosa", -23.568611, -46.546944),
    "524":     ("Vila Prudente", -23.592500, -46.573889),
    "495":     ("Vila Mariana", -23.588333, -46.634444),
    "1000840": ("Ipiranga", -23.588889, -46.605278),
    "634":     ("Jabaquara", -23.652222, -46.647500),
    "504":     ("Perus", -23.409722, -46.742778),
    "507":     ("Parelheiros/Barragem", -23.825278, -46.705556),
    "592":     ("Cidade Ademar", -23.675000, -46.654722),
    "1000842": ("Butanta", -23.568889, -46.729167),
    "1000852": ("Santo Amaro", -23.642500, -46.699444),
    "1000944": ("Tremembe", -23.412222, -46.587222),
}


def ler_csv_cge(caminho):
    """Lê um CSV do CGE. O cabeçalho possui uma coluna vazia espúria logo
    após DATA, que não existe nas linhas de dados; por isso os nomes são
    reatribuídos manualmente."""
    cabecalho = pd.read_csv(caminho, nrows=0, encoding_errors="replace")
    nomes = [c for c in cabecalho.columns if not c.startswith("Unnamed")]
    df = pd.read_csv(caminho, header=None, skiprows=1, names=nomes,
                     index_col=False, encoding_errors="replace")
    df = df.rename(columns={"PLU(mm)": "plu", "Temp(oC)": "temp",
                            "Umid.Rel.(%)": "umid"})
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
    df = df.dropna(subset=["DATA"]).drop_duplicates(subset="DATA")
    return df.set_index("DATA").sort_index()


def precipitacao_acumulada(plu):
    """O PLU do CGE é um acumulador que zera uma vez por dia. A chuva de
    cada intervalo é o incremento do acumulador; quando ele zera (diferença
    negativa), o incremento é o próprio valor lido."""
    plu = plu.dropna()
    incremento = plu.diff()
    incremento[incremento < 0] = plu[incremento < 0]
    return float(incremento.clip(lower=0).sum())


def main():
    if len(sys.argv) < 2:
        print("Uso: python src/prepara_dados.py <pasta_csvs_cge_2024>")
        sys.exit(1)
    pasta = sys.argv[1]
    linhas = []
    for caminho in sorted(glob.glob(os.path.join(pasta, "*.csv"))):
        df = ler_csv_cge(caminho)
        posto = str(int(df["Posto"].iloc[0]))
        if posto not in ESTACOES:
            continue
        rotulo, lat, lon = ESTACOES[posto]
        janela = df.loc[INICIO_JANELA:FIM_JANELA]
        linhas.append({
            "posto": posto,
            "rotulo": rotulo,
            "lat": lat,
            "lon": lon,
            "precip_mm": round(precipitacao_acumulada(janela["plu"]), 1),
            "temp_media_c": round(janela["temp"].mean(), 2),
            "umid_media_pct": round(janela["umid"].mean(), 1),
            "cobertura_pct": round(100 * janela["temp"].notna().sum()
                                   / 17424, 1),  # 121 dias x 144 registros
        })
    resumo = pd.DataFrame(linhas).sort_values("lat", ascending=False)
    destino = os.path.join(os.path.dirname(__file__), "..", "dados",
                           "estacoes_resumo.csv")
    resumo.to_csv(destino, index=False)
    print(resumo.to_string(index=False))
    print(f"\n{len(resumo)} estações gravadas em {os.path.normpath(destino)}")


if __name__ == "__main__":
    main()

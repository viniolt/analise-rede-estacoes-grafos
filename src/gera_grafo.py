# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Parte 2
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Síntese:
    Constrói o grafo da rede de estações a partir de dados/estacoes_resumo.csv
    e grava:
        - grafo.txt              (formato exigido pela disciplina, tipo 3)
        - dados/estacoes.graphml (para visualização no Gephi, com lat/lon)
    Regra de criação das arestas (k vizinhos mais próximos, k = 4):
        cada estação é ligada às 4 estações geograficamente mais próximas;
        como o grafo é não orientado, a relação é simetrizada (a aresta
        {u, v} existe se v está entre os 4 mais próximos de u OU u está entre
        os 4 mais próximos de v). O peso da aresta é a distância geográfica
        (fórmula de Haversine) em km. O peso do vértice é a precipitação
        acumulada (mm) na janela 01/01/2024 a 30/04/2024.
    Usa somente a biblioteca padrão do Python.

Uso:
    python src/gera_grafo.py [k]
"""

import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafo import Grafo  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ARQ_RESUMO = os.path.join(RAIZ, "dados", "estacoes_resumo.csv")
ARQ_GRAFO = os.path.join(RAIZ, "grafo.txt")
ARQ_GRAPHML = os.path.join(RAIZ, "dados", "estacoes.graphml")
RAIO_TERRA_KM = 6371.0
K_PADRAO = 4


def haversine_km(lat1, lon1, lat2, lon2):
    """Distância sobre a superfície terrestre entre dois pontos (em km)."""
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    a = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * RAIO_TERRA_KM * math.asin(math.sqrt(a))


def ler_estacoes(caminho):
    with open(caminho, encoding="utf-8") as arq:
        return list(csv.DictReader(arq))


def construir_grafo_knn(estacoes, k):
    """Monta um Grafo (tipo 3) ligando cada estação aos k vizinhos mais
    próximos."""
    n = len(estacoes)
    grafo = Grafo(tipo=3)
    for est in estacoes:
        grafo.insereV(est["rotulo"], float(est["precip_mm"]))

    coords = [(float(e["lat"]), float(e["lon"])) for e in estacoes]
    for v in range(n):
        distancias = sorted(
            (haversine_km(*coords[v], *coords[w]), w)
            for w in range(n) if w != v)
        for dist, w in distancias[:k]:
            # insereA ignora a aresta se ela já existir (simetrização)
            grafo.insereA(v, w, round(dist, 2))
    return grafo


def gravar_graphml(grafo, estacoes, caminho):
    """Grava o grafo em GraphML com atributos para o Gephi (latitude e
    longitude permitem usar o layout geográfico)."""
    linhas = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
        '  <key id="lat" for="node" attr.name="latitude" attr.type="double"/>',
        '  <key id="lon" for="node" attr.name="longitude" attr.type="double"/>',
        '  <key id="precip" for="node" attr.name="precip_mm" attr.type="double"/>',
        '  <key id="temp" for="node" attr.name="temp_media_c" attr.type="double"/>',
        '  <key id="umid" for="node" attr.name="umid_media_pct" attr.type="double"/>',
        '  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>',
        '  <graph edgedefault="undirected">',
    ]
    for v, est in enumerate(estacoes):
        linhas.append(f'    <node id="{v}">')
        linhas.append(f'      <data key="label">{est["rotulo"]}</data>')
        linhas.append(f'      <data key="lat">{est["lat"]}</data>')
        linhas.append(f'      <data key="lon">{est["lon"]}</data>')
        linhas.append(f'      <data key="precip">{est["precip_mm"]}</data>')
        linhas.append(f'      <data key="temp">{est["temp_media_c"]}</data>')
        linhas.append(f'      <data key="umid">{est["umid_media_pct"]}</data>')
        linhas.append('    </node>')
    for v, w, peso in grafo.arestas():
        linhas.append(f'    <edge source="{v}" target="{w}">'
                      f'<data key="weight">{peso}</data></edge>')
    linhas += ['  </graph>', '</graphml>']
    with open(caminho, "w", encoding="utf-8") as arq:
        arq.write("\n".join(linhas) + "\n")


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else K_PADRAO
    estacoes = ler_estacoes(ARQ_RESUMO)
    grafo = construir_grafo_knn(estacoes, k)
    grafo.gravarArquivo(ARQ_GRAFO)
    gravar_graphml(grafo, estacoes, ARQ_GRAPHML)
    graus = [grafo.grau(v) for v in range(grafo.n)]
    print(f"k = {k}: n = {grafo.n} vértices, m = {grafo.m} arestas")
    print(f"grau mínimo = {min(graus)}, máximo = {max(graus)}, "
          f"médio = {sum(graus) / grafo.n:.2f}")
    print(f"Gravados: {os.path.normpath(ARQ_GRAFO)} e "
          f"{os.path.normpath(ARQ_GRAPHML)}")


if __name__ == "__main__":
    main()

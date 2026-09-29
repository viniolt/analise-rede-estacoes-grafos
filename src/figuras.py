# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Parte 2
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Síntese:
    Gera as figuras do relatório (requer matplotlib):
      - figuras/grafo_mapa.png: o grafo desenhado nas coordenadas reais das
        estações, com a cor do vértice indicando a precipitação acumulada;
      - figuras/testes/teste_XX.png: imagem de cada saída de teste gravada
        em testes/saidas/ (captura da tela do terminal).

Uso:
    python src/figuras.py

"""

import csv
import glob
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafo import Grafo  # noqa: E402

RAIZ = os.path.normpath(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), ".."))
FIGS = os.path.join(RAIZ, "figuras")


def figura_mapa():
    grafo = Grafo.lerArquivo(os.path.join(RAIZ, "grafo.txt"))
    with open(os.path.join(RAIZ, "dados", "estacoes_resumo.csv"),
              encoding="utf-8") as arq:
        estacoes = list(csv.DictReader(arq))
    lat = [float(e["lat"]) for e in estacoes]
    lon = [float(e["lon"]) for e in estacoes]

    fig, ax = plt.subplots(figsize=(9, 10))
    for v, w, peso in grafo.arestas():
        ax.plot([lon[v], lon[w]], [lat[v], lat[w]], color="#9aa5b1",
                linewidth=1, zorder=1)
        ax.text((lon[v] + lon[w]) / 2, (lat[v] + lat[w]) / 2,
                f"{peso:.1f}", fontsize=5.5, color="#52606d",
                ha="center", va="center", zorder=2)
    pontos = ax.scatter(lon, lat, c=grafo.pesosV, cmap="Blues", s=160,
                        edgecolors="#1f2933", linewidths=0.8, zorder=3)
    for v in range(grafo.n):
        ax.annotate(f"{v} {grafo.rotulos[v]}", (lon[v], lat[v]),
                    xytext=(6, 4), textcoords="offset points", fontsize=7,
                    zorder=4)
    fig.colorbar(pontos, ax=ax, shrink=0.6,
                 label="Precipitação acumulada 01/01–30/04/2024 (mm)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"Rede de estações do CGE – k-NN (k = 4): "
                 f"n = {grafo.n}, m = {grafo.m}\n"
                 "peso da aresta = distância de Haversine (km)")
    ax.set_aspect(1 / 0.917)  # correção aproximada de escala em -23.6°
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, "grafo_mapa.png"), dpi=200)
    plt.close(fig)


def figuras_testes():
    destino = os.path.join(FIGS, "testes")
    os.makedirs(destino, exist_ok=True)
    for caminho in sorted(glob.glob(os.path.join(RAIZ, "testes", "saidas",
                                                 "teste_*.txt"))):
        with open(caminho, encoding="utf-8") as arq:
            linhas = arq.read().rstrip("\n").split("\n")
        titulo, linhas = linhas[0].lstrip("# "), linhas[1:]
        # linhas muito longas (listas de componentes) são quebradas
        quebradas = []
        for linha in linhas:
            while len(linha) > 110:
                quebradas.append(linha[:110])
                linha = "      " + linha[110:]
            quebradas.append(linha)
        altura = 0.16 * len(quebradas) + 0.5
        fig = plt.figure(figsize=(9.5, altura))
        fig.patch.set_facecolor("#1e1e1e")
        fig.text(0.01, 1 - 0.18 / altura, titulo, color="#9cdcfe",
                 family="monospace", fontsize=8, va="top", weight="bold")
        fig.text(0.01, 1 - 0.42 / altura, "\n".join(quebradas),
                 color="#e6e6e6", family="monospace", fontsize=7.2, va="top",
                 linespacing=1.25)
        nome = os.path.splitext(os.path.basename(caminho))[0]
        fig.savefig(os.path.join(destino, f"{nome}.png"), dpi=160,
                    facecolor=fig.get_facecolor())
        plt.close(fig)


if __name__ == "__main__":
    os.makedirs(FIGS, exist_ok=True)
    figura_mapa()
    figuras_testes()
    print("Figuras gravadas em", FIGS)

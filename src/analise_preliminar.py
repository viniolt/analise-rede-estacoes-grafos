# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Parte 2
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Síntese:
    Resultados parciais obtidos diretamente da estrutura do grafo (sem
    qualquer modelo de aprendizado):
      1) estatísticas estruturais: n, m, densidade, graus;
      2) comparação de cada estação com a sua vizinhança no grafo:
            D(v) = x(v) - média dos x(w), w adjacente a v
         onde x é a precipitação acumulada (peso do vértice). O valor é
         padronizado (escore z) para indicar estações cujo comportamento
         é discrepante em relação às vizinhas. Trata-se de uma análise
         exploratória, a ser aprofundada na Parte 3 com centralidades e
         detecção de comunidades.
    Grava a tabela em dados/discrepancia_preliminar.csv.

Uso:
    python src/analise_preliminar.py
"""

import csv
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafo import Grafo  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LIMIAR_Z = 1.5  # |z| acima deste valor: comportamento discrepante


def diferenca_vizinhanca(grafo):
    """D(v) = peso de v menos a média dos pesos dos vizinhos de v."""
    diferencas = []
    for v in range(grafo.n):
        vizinhos = [w for w, _ in grafo.listaAdj[v]]
        media = sum(grafo.pesosV[w] for w in vizinhos) / len(vizinhos)
        diferencas.append((v, grafo.pesosV[v], media, grafo.pesosV[v] - media))
    return diferencas


def main():
    grafo = Grafo.lerArquivo(os.path.join(RAIZ, "grafo.txt"))
    graus = [grafo.grau(v) for v in range(grafo.n)]
    pesos_a = [p for _, _, p in grafo.arestas()]
    densidade = 2 * grafo.m / (grafo.n * (grafo.n - 1))
    print(f"n = {grafo.n}, m = {grafo.m}, densidade = {densidade:.3f}")
    print(f"grau: mín {min(graus)}, máx {max(graus)}, "
          f"médio {statistics.mean(graus):.2f}")
    print(f"distância das arestas (km): mín {min(pesos_a):.2f}, "
          f"máx {max(pesos_a):.2f}, média {statistics.mean(pesos_a):.2f}")
    hist = {g: graus.count(g) for g in sorted(set(graus))}
    print("distribuição de graus:", hist)
    maior = max(graus)
    print("maior grau:", ", ".join(
        grafo.rotulos[v] for v in range(grafo.n) if graus[v] == maior))

    diferencas = diferenca_vizinhanca(grafo)
    valores = [d for *_, d in diferencas]
    media, desvio = statistics.mean(valores), statistics.pstdev(valores)
    linhas = []
    for v, x, media_viz, d in diferencas:
        z = (d - media) / desvio
        linhas.append({"vertice": v, "estacao": grafo.rotulos[v],
                       "grau": graus[v], "precip_mm": x,
                       "media_vizinhos_mm": round(media_viz, 1),
                       "diferenca_mm": round(d, 1), "z": round(z, 2),
                       "discrepante": "sim" if abs(z) > LIMIAR_Z else "não"})
    linhas.sort(key=lambda l: -abs(l["z"]))
    with open(os.path.join(RAIZ, "dados", "discrepancia_preliminar.csv"),
              "w", newline="", encoding="utf-8") as arq:
        escritor = csv.DictWriter(arq, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f"\nEstações mais discrepantes em relação às vizinhas "
          f"(|z| > {LIMIAR_Z}):")
    print(f"{'Estação':<22}{'grau':>5}{'x (mm)':>9}{'viz. (mm)':>11}"
          f"{'D (mm)':>9}{'z':>7}")
    for l in linhas[:8]:
        marca = " *" if l["discrepante"] == "sim" else ""
        print(f"{l['estacao']:<22}{l['grau']:>5}{l['precip_mm']:>9.1f}"
              f"{l['media_vizinhos_mm']:>11.1f}{l['diferenca_mm']:>9.1f}"
              f"{l['z']:>7.2f}{marca}")


if __name__ == "__main__":
    main()

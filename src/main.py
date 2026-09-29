# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Parte 2
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Síntese:
    Aplicação com menu de opções para manipular o grafo da rede de estações
    meteorológicas do CGE (São Paulo) armazenado em grafo.txt:
        a) ler grafo.txt            f) remover aresta
        b) gravar grafo.txt         g) mostrar conteúdo do arquivo
        c) inserir vértice          h) mostrar grafo (lista de adjacência)
        d) inserir aresta           i) conexidade e grafo reduzido
        e) remover vértice          j) encerrar

Uso:
    python src/main.py

"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafo import DESCRICAO_TIPOS, Grafo, formatar_numero  # noqa: E402

ARQ_PADRAO = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "grafo.txt"))

TITULO = "REDE DE ESTAÇÕES METEOROLÓGICAS - ANÁLISE DE PADRÕES CLIMÁTICOS"

MENU = """
==================================================================
  {titulo}
==================================================================
  a) Ler dados do arquivo grafo.txt
  b) Gravar dados no arquivo grafo.txt
  c) Inserir vértice (estação)
  d) Inserir aresta (vizinhança)
  e) Remover vértice
  f) Remover aresta
  g) Mostrar conteúdo do arquivo
  h) Mostrar grafo (lista de adjacência)
  i) Apresentar a conexidade do grafo e o reduzido
  j) Encerrar a aplicação
------------------------------------------------------------------"""


def ler(mensagem):
    """input() que encerra de forma limpa se a entrada acabar."""
    try:
        return input(mensagem).strip()
    except EOFError:
        print()
        sys.exit(0)


def ler_inteiro(mensagem):
    texto = ler(mensagem)
    try:
        return int(texto)
    except ValueError:
        print(f"  [erro] '{texto}' não é um número inteiro.")
        return None


def ler_real(mensagem, padrao=0.0):
    texto = ler(mensagem)
    if texto == "":
        return padrao
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        print(f"  [erro] '{texto}' não é um número; usando {padrao}.")
        return padrao


def pedir_arquivo():
    nome = ler(f"  Arquivo [{ARQ_PADRAO}]: ")
    return nome or ARQ_PADRAO


def grafo_carregado(grafo):
    if grafo is None:
        print("  [aviso] Nenhum grafo em memória. Use a opção a) primeiro.")
        return False
    return True


def descrever_vertice(grafo, v):
    return f"{v} ({grafo.rotulos[v]})"


# ----------------------------------------------------------------------
# Opções do menu
# ----------------------------------------------------------------------
def opcao_ler():
    caminho = pedir_arquivo()
    try:
        grafo = Grafo.lerArquivo(caminho)
    except FileNotFoundError:
        print(f"  [erro] Arquivo '{caminho}' não encontrado.")
        return None
    except (ValueError, IndexError) as erro:
        print(f"  [erro] Arquivo com formato inválido: {erro}")
        return None
    print(f"  Grafo lido: tipo {grafo.tipo} ({DESCRICAO_TIPOS[grafo.tipo]}),"
          f" n = {grafo.n}, m = {grafo.m}.")
    return grafo


def opcao_gravar(grafo):
    caminho = pedir_arquivo()
    try:
        grafo.gravarArquivo(caminho)
    except OSError as erro:
        print(f"  [erro] Não foi possível gravar: {erro}")
        return
    print(f"  Grafo gravado em '{caminho}' (n = {grafo.n}, m = {grafo.m}).")


def opcao_inserir_vertice(grafo):
    rotulo = ler("  Rótulo (nome da estação): ")
    if not rotulo:
        print("  [erro] O rótulo não pode ser vazio.")
        return
    peso = 0.0
    if grafo.temPesoVertice():
        peso = ler_real("  Peso do vértice (precipitação acumulada, mm): ")
    try:
        v = grafo.insereV(rotulo, peso)
    except ValueError as erro:
        print(f"  [erro] {erro}")
        return
    print(f"  Vértice {descrever_vertice(grafo, v)} inserido. n = {grafo.n}.")


def opcao_inserir_aresta(grafo):
    v = ler_inteiro("  Vértice de origem: ")
    w = ler_inteiro("  Vértice de destino: ")
    if v is None or w is None:
        return
    if not (grafo.verticeValido(v) and grafo.verticeValido(w)):
        print(f"  [erro] Os vértices devem estar entre 0 e {grafo.n - 1}.")
        return
    peso = 1.0
    if grafo.temPesoAresta():
        peso = ler_real("  Peso da aresta (distância, km): ", 1.0)
    if grafo.insereA(v, w, peso):
        print(f"  Aresta {descrever_vertice(grafo, v)} - "
              f"{descrever_vertice(grafo, w)} inserida. m = {grafo.m}.")
    else:
        print("  [aviso] Aresta não inserida: já existe ou é um laço.")


def opcao_remover_vertice(grafo):
    v = ler_inteiro("  Vértice a remover: ")
    if v is None:
        return
    if not grafo.verticeValido(v):
        print(f"  [erro] O vértice deve estar entre 0 e {grafo.n - 1}.")
        return
    rotulo = grafo.rotulos[v]
    grafo.removeV(v)
    print(f"  Vértice {v} ({rotulo}) e suas arestas removidos. "
          f"n = {grafo.n}, m = {grafo.m}.")
    print("  Os vértices seguintes foram renumerados (w -> w - 1).")


def opcao_remover_aresta(grafo):
    v = ler_inteiro("  Vértice de origem: ")
    w = ler_inteiro("  Vértice de destino: ")
    if v is None or w is None:
        return
    if not (grafo.verticeValido(v) and grafo.verticeValido(w)):
        print(f"  [erro] Os vértices devem estar entre 0 e {grafo.n - 1}.")
        return
    if grafo.removeA(v, w):
        print(f"  Aresta {v} - {w} removida. m = {grafo.m}.")
    else:
        print(f"  [aviso] A aresta {v} - {w} não existe.")


def opcao_mostrar_arquivo():
    """Mostra o conteúdo do arquivo em formato legível (não usa a memória)."""
    caminho = pedir_arquivo()
    try:
        grafo = Grafo.lerArquivo(caminho)
    except FileNotFoundError:
        print(f"  [erro] Arquivo '{caminho}' não encontrado.")
        return
    except (ValueError, IndexError) as erro:
        print(f"  [erro] Arquivo com formato inválido: {erro}")
        return
    print(f"\n  Arquivo: {caminho}")
    print(f"  Tipo {grafo.tipo}: {DESCRICAO_TIPOS[grafo.tipo]}")
    print(f"\n  VÉRTICES (n = {grafo.n})")
    print(f"  {'Nº':>3}  {'Estação':<24}{'Precip. (mm)':>13}")
    print("  " + "-" * 42)
    for v in range(grafo.n):
        print(f"  {v:>3}  {grafo.rotulos[v]:<24}"
              f"{formatar_numero(grafo.pesosV[v]):>13}")
    print(f"\n  ARESTAS (m = {grafo.m})")
    print(f"  {'v':>3} {'w':>3}  {'Estação v':<22}{'Estação w':<22}"
          f"{'Dist. (km)':>10}")
    print("  " + "-" * 62)
    for v, w, peso in grafo.arestas():
        print(f"  {v:>3} {w:>3}  {grafo.rotulos[v][:21]:<22}"
              f"{grafo.rotulos[w][:21]:<22}{formatar_numero(peso):>10}")


def opcao_conexidade(grafo):
    situacao, componentes = grafo.conexidade()
    if not grafo.ehOrientado():
        print(f"  O grafo (não orientado) é {situacao}.")
        print(f"  Componentes conexas: {len(componentes)}")
        for i, comp in enumerate(componentes):
            nomes = ", ".join(grafo.rotulos[v] for v in comp)
            print(f"   C{i} ({len(comp)} vértices): {nomes}")
        print("  (Grafo reduzido só se aplica a grafos orientados.)")
        return
    print(f"  Categoria de conexidade (grafo orientado): {situacao}")
    componentes, arestas = grafo.grafoReduzido()
    print(f"  Componentes fortemente conexas (FCONEX): {len(componentes)}")
    for i, comp in enumerate(componentes):
        print(f"   C{i}: {comp}")
    print("  Grafo reduzido (arestas entre componentes):")
    if not arestas:
        print("   (nenhuma aresta)")
    for a, b in arestas:
        print(f"   C{a} -> C{b}")


def main():
    grafo = None
    while True:
        print(MENU.format(titulo=TITULO))
        opcao = ler("  Opção: ").lower()
        print()
        if opcao == "a":
            novo = opcao_ler()
            if novo is not None:
                grafo = novo
        elif opcao == "g":
            opcao_mostrar_arquivo()
        elif opcao == "j":
            print("  Aplicação encerrada.")
            break
        elif opcao in ("b", "c", "d", "e", "f", "h", "i"):
            if not grafo_carregado(grafo):
                continue
            {"b": opcao_gravar,
             "c": opcao_inserir_vertice,
             "d": opcao_inserir_aresta,
             "e": opcao_remover_vertice,
             "f": opcao_remover_aresta,
             "h": lambda g: g.show(),
             "i": opcao_conexidade}[opcao](grafo)
        else:
            print(f"  [erro] Opção '{opcao}' inválida.")


if __name__ == "__main__":
    main()

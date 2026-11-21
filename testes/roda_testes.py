# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Partes 2 e 3
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Histórico de alterações:
    28/09/2026 - Vinícius Pereira Rodrigues - testes das opções a) a j).
    21/11/2026 - Vinícius Pereira Rodrigues - Parte 3: testes das novas
                 opções j) a o); encerrar passou a ser a opção p);
                 novo grafo de exemplo testes/grafo_pequeno.txt.

Síntese:
    Executa a aplicação (src/main.py) com entradas pré-definidas: pelo menos
    dois testes para cada opção do menu (a-p). Cada sessão é gravada em
    testes/saidas/teste_<opção><nº>.txt com as entradas digitadas ecoadas,
    como apareceriam no terminal. O grafo.txt original nunca é alterado:
    as gravações usam arquivos dentro de testes/saidas/.

Uso:
    python testes/roda_testes.py
"""

import builtins
import contextlib
import io
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "src"))
import main  # noqa: E402

SAIDAS = os.path.join(AQUI, "saidas")
GRAVADO = os.path.join(SAIDAS, "grafo_gravado.txt")
ORIENTADO = os.path.join(AQUI, "grafo_orientado.txt")
# grafo do slide de percursos eulerianos (G'12): semi-euleriano, com uma
# ponte b-e, logo sem ciclo hamiltoniano
PEQUENO = os.path.join(AQUI, "grafo_pequeno.txt")

# Remove as 4 arestas da estação 31 (Marsilac), deixando-a isolada
ISOLAR_MARSILAC = ["f", "27", "31", "f", "28", "31", "f", "29", "31",
                   "f", "30", "31"]

# (identificador, descrição, entradas). "" = Enter (arquivo padrão).
TESTES = [
    ("a1", "Ler o grafo.txt da rede de estações", ["a", "", "p"]),
    ("a2", "Ler arquivo inexistente", ["a", "nao_existe.txt", "p"]),
    ("b1", "Gravar o grafo após inserir uma estação",
     ["a", "", "c", "IAG-USP", "700", "b", GRAVADO, "p"]),
    ("b2", "Gravar sem grafo carregado", ["b", "p"]),
    ("c1", "Inserir a estação IAG-USP", ["a", "", "c", "IAG-USP", "700", "p"]),
    ("c2", "Inserir estação com rótulo vazio", ["a", "", "c", "", "p"]),
    ("d1", "Inserir aresta IAG-USP - Jabaquara (3,3 km)",
     ["a", "", "c", "IAG-USP", "700", "d", "32", "24", "3.3", "p"]),
    ("d2", "Inserir aresta já existente (Perus - Pirituba)",
     ["a", "", "d", "0", "4", "7.85", "p"]),
    ("e1", "Remover o vértice 31 (Marsilac)",
     ["a", "", "e", "31", "h", "p"]),
    ("e2", "Remover vértice inexistente", ["a", "", "e", "99", "p"]),
    ("f1", "Remover aresta Perus - Pirituba", ["a", "", "f", "0", "4", "p"]),
    ("f2", "Remover aresta inexistente (Perus - Marsilac)",
     ["a", "", "f", "0", "31", "p"]),
    ("g1", "Mostrar o conteúdo do grafo.txt", ["g", "", "p"]),
    ("g2", "Mostrar o arquivo gravado no teste b1", ["g", GRAVADO, "p"]),
    ("h1", "Mostrar o grafo (lista de adjacência)", ["a", "", "h", "p"]),
    ("h2", "Mostrar grafo sem grafo carregado", ["h", "p"]),
    ("i1", "Conexidade da rede de estações", ["a", "", "i", "p"]),
    ("i2", "Isolar Marsilac (remover suas 4 arestas) e verificar",
     ["a", ""] + ISOLAR_MARSILAC + ["i", "p"]),
    ("i3", "Conexidade e grafo reduzido de um grafo orientado",
     ["a", ORIENTADO, "i", "f", "2", "3", "i", "p"]),
    # ---------------- Parte 3: solução do problema ----------------
    ("j1", "Regiões de chuva homogênea com k padrão (4)",
     ["a", "", "j", "", "p"]),
    ("j2", "Regiões com k inválido (40) e depois k = 2",
     ["a", "", "j", "40", "j", "2", "p"]),
    ("j3", "Regiões em grafo orientado (não se aplica)",
     ["a", ORIENTADO, "j", "p"]),
    ("k1", "Rota mínima Perus -> Marsilac e estação central",
     ["a", "", "k", "0", "31", "p"]),
    ("k2", "Rota até Marsilac isolada (sem caminho; grafo desconexo)",
     ["a", ""] + ISOLAR_MARSILAC + ["k", "0", "31", "p"]),
    ("k3", "Rota com estação inexistente", ["a", "", "k", "0", "99", "p"]),
    # ---------------- Parte 3: características do grafo ----------------
    ("l1", "Graus dos vértices da rede de estações", ["a", "", "l", "p"]),
    ("l2", "Graus de entrada e saída de um grafo orientado",
     ["a", ORIENTADO, "l", "p"]),
    ("m1", "Coloração sequencial da rede de estações", ["a", "", "m", "p"]),
    ("m2", "Coloração sequencial do grafo pequeno", ["a", PEQUENO, "m", "p"]),
    ("n1", "Rede de estações é euleriana?", ["a", "", "n", "p"]),
    ("n2", "Grafo pequeno (G'12 da aula) é euleriano?",
     ["a", PEQUENO, "n", "p"]),
    ("o1", "Rede de estações é hamiltoniana?", ["a", "", "o", "p"]),
    ("o2", "Grafo pequeno (com ponte) é hamiltoniano?",
     ["a", PEQUENO, "o", "p"]),
    ("o3", "Hamiltoniano sem grafo carregado", ["o", "p"]),
    ("p1", "Encerrar a aplicação", ["p"]),
    ("p2", "Opção inválida seguida de encerramento", ["x", "p"]),
]


def executar(entradas, esconder_menu_repetido=True):
    """Roda main.main() com as entradas dadas e devolve o texto da tela."""
    fila = list(entradas)
    tela = io.StringIO()
    original = builtins.input

    def input_falso(prompt=""):
        valor = fila.pop(0)
        print(f"{prompt}{valor}")
        return valor

    builtins.input = input_falso
    try:
        with contextlib.redirect_stdout(tela):
            main.main()
    finally:
        builtins.input = original

    texto = tela.getvalue()
    if esconder_menu_repetido:
        # O menu completo aparece só na primeira vez; nas seguintes fica
        # apenas a linha da opção escolhida, para as saídas ficarem curtas.
        menu = main.MENU.format(titulo=main.TITULO)
        primeira = texto.find(menu) + len(menu)
        texto = texto[:primeira] + texto[primeira:].replace(
            menu, "\n  [... menu ...]")
    return texto


def main_testes():
    os.makedirs(SAIDAS, exist_ok=True)
    # apaga as saídas antigas para não sobrar teste que não existe mais
    for nome in os.listdir(SAIDAS):
        if nome.startswith("teste_") and nome.endswith(".txt"):
            os.remove(os.path.join(SAIDAS, nome))
    for ident, descricao, entradas in TESTES:
        texto = executar(entradas)
        # caminhos absolutos ficam relativos à raiz do projeto
        raiz = os.path.normpath(os.path.join(AQUI, "..")) + os.sep
        texto = texto.replace(raiz, "")
        cabecalho = f"# Teste {ident}: {descricao}\n"
        with open(os.path.join(SAIDAS, f"teste_{ident}.txt"), "w",
                  encoding="utf-8") as arq:
            arq.write(cabecalho + texto)
        print(f"ok  teste_{ident}: {descricao}")


if __name__ == "__main__":
    main_testes()

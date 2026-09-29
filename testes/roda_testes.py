# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Parte 2
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Síntese:
    Executa a aplicação (src/main.py) com entradas pré-definidas: dois testes
    para cada opção do menu (a-j). Cada sessão é gravada em
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

# (identificador, descrição, entradas). "" = Enter (arquivo padrão).
TESTES = [
    ("a1", "Ler o grafo.txt da rede de estações", ["a", "", "j"]),
    ("a2", "Ler arquivo inexistente", ["a", "nao_existe.txt", "j"]),
    ("b1", "Gravar o grafo após inserir uma estação",
     ["a", "", "c", "IAG-USP", "700", "b", GRAVADO, "j"]),
    ("b2", "Gravar sem grafo carregado", ["b", "j"]),
    ("c1", "Inserir a estação IAG-USP", ["a", "", "c", "IAG-USP", "700", "j"]),
    ("c2", "Inserir estação com rótulo vazio", ["a", "", "c", "", "j"]),
    ("d1", "Inserir aresta IAG-USP - Jabaquara (3,3 km)",
     ["a", "", "c", "IAG-USP", "700", "d", "32", "24", "3.3", "j"]),
    ("d2", "Inserir aresta já existente (Perus - Pirituba)",
     ["a", "", "d", "0", "4", "7.85", "j"]),
    ("e1", "Remover o vértice 31 (Marsilac)",
     ["a", "", "e", "31", "h", "j"]),
    ("e2", "Remover vértice inexistente", ["a", "", "e", "99", "j"]),
    ("f1", "Remover aresta Perus - Pirituba", ["a", "", "f", "0", "4", "j"]),
    ("f2", "Remover aresta inexistente (Perus - Marsilac)",
     ["a", "", "f", "0", "31", "j"]),
    ("g1", "Mostrar o conteúdo do grafo.txt", ["g", "", "j"]),
    ("g2", "Mostrar o arquivo gravado no teste b1", ["g", GRAVADO, "j"]),
    ("h1", "Mostrar o grafo (lista de adjacência)", ["a", "", "h", "j"]),
    ("h2", "Mostrar grafo sem grafo carregado", ["h", "j"]),
    ("i1", "Conexidade da rede de estações", ["a", "", "i", "j"]),
    ("i2", "Isolar Marsilac (remover suas 4 arestas) e verificar",
     ["a", "", "f", "27", "31", "f", "28", "31", "f", "29", "31",
      "f", "30", "31", "i", "j"]),
    ("i3", "Conexidade e grafo reduzido de um grafo orientado",
     ["a", ORIENTADO, "i", "f", "2", "3", "i", "j"]),
    ("j1", "Encerrar a aplicação", ["j"]),
    ("j2", "Opção inválida seguida de encerramento", ["x", "j"]),
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

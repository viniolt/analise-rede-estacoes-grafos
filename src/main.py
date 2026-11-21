# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Partes 2 e 3
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Histórico de alterações:
    28/09/2026 - Vinícius Pereira Rodrigues - versão da Parte 2: menu com
                 as opções a) a j).
    21/11/2026 - Vinícius Pereira Rodrigues - Parte 3: novas opções j) a
                 o) (solução do problema e características do grafo); a
                 opção de encerrar passou de j) para p).

Síntese:
    Aplicação com menu de opções para manipular e analisar o grafo da rede
    de estações meteorológicas do CGE (São Paulo) armazenado em grafo.txt:
      Parte 2 - manipulação do grafo
        a) ler grafo.txt            f) remover aresta
        b) gravar grafo.txt         g) mostrar conteúdo do arquivo
        c) inserir vértice          h) mostrar grafo (lista de adjacência)
        d) inserir aresta           i) conexidade e grafo reduzido
        e) remover vértice
      Parte 3 - solução do problema (técnicas da disciplina)
        j) regiões de chuva homogênea (AGM - Kruskal)
        k) rota mínima entre estações e estação central (Dijkstra)
      Parte 3 - características do grafo
        l) graus dos vértices       n) grafo euleriano?
        m) coloração sequencial     o) grafo hamiltoniano?
        p) encerrar

Uso:
    python src/main.py

"""

import os
import sys
import textwrap

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
  ---------------- Solução do problema (Parte 3) -----------------
  j) Regiões de chuva homogênea (árvore geradora mínima - Kruskal)
  k) Rota mínima entre estações e estação central (Dijkstra)
  -------------- Características do grafo (Parte 3) --------------
  l) Graus dos vértices
  m) Coloração dos vértices (coloração sequencial)
  n) Verificar se o grafo é euleriano
  o) Verificar se o grafo é hamiltoniano
  ----------------------------------------------------------------
  p) Encerrar a aplicação
------------------------------------------------------------------"""

K_REGIOES_PADRAO = 4  # quantidade padrão de regiões da opção j)


def ler(mensagem):
    """input() que encerra de forma limpa se a entrada acabar."""
    try:
        return input(mensagem).strip()
    except EOFError:
        print()
        sys.exit(0)


def ler_inteiro(mensagem, padrao=None):
    """Lê um inteiro. Se padrao for dado, Enter (vazio) devolve padrao."""
    texto = ler(mensagem)
    if texto == "" and padrao is not None:
        return padrao
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


# ----------------------------------------------------------------------
# Parte 3 - funções auxiliares
# ----------------------------------------------------------------------
def exige_nao_orientado(grafo):
    """As técnicas das opções j), n) e o) foram vistas em aula para grafos
    não orientados; para grafos orientados a opção é recusada."""
    if grafo.ehOrientado():
        print("  [aviso] Esta opção se aplica apenas a grafos NÃO orientados.")
        return False
    return True


def nomes_dos_vertices(grafo, vertices):
    return ", ".join(grafo.rotulos[v] for v in vertices)


def imprimir_texto_longo(texto, recuo="     "):
    """Quebra um texto longo em linhas de até 74 caracteres."""
    print(textwrap.fill(texto, width=74, initial_indent=recuo,
                        subsequent_indent=recuo))


def imprimir_em_linhas(itens, por_linha=3, recuo="   "):
    """Imprime uma lista de textos em colunas, para saídas mais curtas."""
    for i in range(0, len(itens), por_linha):
        print(recuo + "".join(f"{item:<26}" for item in itens[i:i + por_linha]))


# ----------------------------------------------------------------------
# Parte 3 - solução do problema
# ----------------------------------------------------------------------
def opcao_regioes(grafo):
    """j) Regiões de chuva homogênea.

    1. Monta o "grafo de diferenças": mesmas estações e mesmas ligações de
       vizinhança, mas o peso da aresta v-w é |chuva(v) - chuva(w)|.
    2. Calcula a árvore geradora mínima desse grafo com Kruskal: ela liga
       todas as estações usando as vizinhanças de chuva mais parecida.
    3. Retira as k - 1 arestas mais pesadas da árvore (as maiores
       diferenças de chuva). A árvore se divide em k regiões; estações que
       ficam sozinhas têm chuva muito diferente de todas as vizinhas.
    """
    if not exige_nao_orientado(grafo):
        return
    if not grafo.temPesoVertice():
        print("  [aviso] O grafo não tem peso nos vértices (precipitação).")
        return
    if grafo.n < 2:
        print("  [aviso] São necessários pelo menos 2 vértices.")
        return
    k = ler_inteiro(f"  Quantidade de regiões k (2 a {grafo.n}) "
                    f"[Enter = {K_REGIOES_PADRAO}]: ", K_REGIOES_PADRAO)
    if k is None:
        return
    if not 2 <= k <= grafo.n:
        print(f"  [erro] k deve estar entre 2 e {grafo.n}.")
        return

    diferencas = grafo.grafoDiferencaPesos()
    arvore, regioes, cortadas = diferencas.regioesPorAGM(k)

    print("  Grafo de diferenças: peso da aresta = |chuva(v) - chuva(w)| (mm)")
    print(f"\n  Árvore geradora mínima (Kruskal): {len(arvore)} arestas, "
          f"custo total = {formatar_numero(round(sum(p for *_, p in arvore), 2))} mm")
    imprimir_em_linhas([f"{v}-{w} ({formatar_numero(p)})" for v, w, p in arvore])
    if len(arvore) < grafo.n - 1:
        print("  (grafo desconexo: o resultado é uma floresta geradora)")

    print(f"\n  Arestas retiradas da árvore ({len(cortadas)} = k - 1, as de "
          "maior diferença de chuva):")
    for v, w, p in cortadas:
        print(f"   {descrever_vertice(grafo, v)} - "
              f"{descrever_vertice(grafo, w)}: {formatar_numero(p)} mm")

    print(f"\n  REGIÕES DE CHUVA HOMOGÊNEA ({len(regioes)})")
    regioes.sort(key=len, reverse=True)
    for i, regiao in enumerate(regioes, start=1):
        chuvas = [grafo.pesosV[v] for v in regiao]
        media = sum(chuvas) / len(chuvas)
        print(f"\n   Região {i}: {len(regiao)} estação(ões), chuva média "
              f"{media:.1f} mm (mín {formatar_numero(min(chuvas))}, "
              f"máx {formatar_numero(max(chuvas))})")
        imprimir_texto_longo(nomes_dos_vertices(grafo, regiao))
        if len(regiao) == 1:
            print("     -> estação DISCREPANTE: chuva muito diferente de "
                  "todas as vizinhas.")


def opcao_rota_e_centro(grafo):
    """k) Rota mínima (Dijkstra) entre duas estações e estação central.

    A estação central é a de menor excentricidade, isto é, a que tem a
    menor distância até a estação mais longe dela (centro do grafo). É o
    melhor ponto para uma base de manutenção que atende toda a rede."""
    if grafo.n == 0:
        print("  [aviso] O grafo não possui vértices.")
        return
    origem = ler_inteiro("  Estação de origem: ")
    destino = ler_inteiro("  Estação de destino: ")
    if origem is None or destino is None:
        return
    if not (grafo.verticeValido(origem) and grafo.verticeValido(destino)):
        print(f"  [erro] Os vértices devem estar entre 0 e {grafo.n - 1}.")
        return

    dist, anterior = grafo.dijkstra(origem)
    print(f"\n  ROTA MÍNIMA (Dijkstra) de {descrever_vertice(grafo, origem)}"
          f" até {descrever_vertice(grafo, destino)}:")
    if dist[destino] == float("inf"):
        print("   Não existe caminho entre as duas estações.")
    else:
        caminho = Grafo.montarCaminho(anterior, destino)
        for a, b in zip(caminho, caminho[1:]):
            print(f"   {descrever_vertice(grafo, a):<28} -> "
                  f"{descrever_vertice(grafo, b):<28}"
                  f"{formatar_numero(grafo.pesoA(a, b)):>7} km")
        print(f"   Total: {dist[destino]:.2f} km em {len(caminho) - 1} "
              "trecho(s).")

    excentricidades = grafo.excentricidades()
    menor = min(excentricidades)
    print("\n  ESTAÇÃO CENTRAL (centro do grafo = menor excentricidade):")
    if menor == float("inf"):
        print("   Grafo desconexo: nenhuma estação alcança todas as outras.")
        return
    ordem = sorted(range(grafo.n), key=lambda v: excentricidades[v])
    print("   As 5 estações mais centrais (excentricidade em km):")
    for v in ordem[:5]:
        print(f"    {descrever_vertice(grafo, v):<30}"
              f"{excentricidades[v]:>8.2f}")
    centro = [v for v in range(grafo.n) if excentricidades[v] == menor]
    print(f"   Centro: {nomes_dos_vertices(grafo, centro)} - nenhuma "
          f"estação fica a mais de {menor:.2f} km dela pela rede.")


# ----------------------------------------------------------------------
# Parte 3 - características do grafo
# ----------------------------------------------------------------------
def opcao_graus(grafo):
    """l) Grau de cada vértice e verificação dos teoremas vistos em aula:
    soma dos graus = 2m e quantidade par de vértices de grau ímpar."""
    if grafo.n == 0:
        print("  [aviso] O grafo não possui vértices.")
        return
    graus = [grafo.grauTotal(v) for v in range(grafo.n)]
    if grafo.ehOrientado():
        print(f"  {'v':>3}  {'Vértice':<24}{'entrada':>8}{'saída':>7}"
              f"{'grau':>6}")
        for v in range(grafo.n):
            print(f"  {v:>3}  {grafo.rotulos[v][:23]:<24}"
                  f"{grafo.grauEntrada(v):>8}{grafo.grau(v):>7}"
                  f"{graus[v]:>6}")
    else:
        itens = [f"{v:>2} {grafo.rotulos[v][:18]}: {graus[v]}"
                 for v in range(grafo.n)]
        print("  Grau de cada vértice:")
        for i in range(0, len(itens), 2):
            print("   " + "".join(f"{item:<32}" for item in itens[i:i + 2]))

    print(f"\n  Grau mínimo: {min(graus)}   Grau máximo: {max(graus)}   "
          f"Grau médio: {sum(graus) / grafo.n:.2f}")
    distribuicao = {g: graus.count(g) for g in sorted(set(graus))}
    print("  Distribuição (grau: qtde de vértices): " +
          ", ".join(f"{g}: {q}" for g, q in distribuicao.items()))
    maior = max(graus)
    print(f"  Vértice(s) de maior grau ({maior}): " +
          nomes_dos_vertices(grafo, [v for v in range(grafo.n)
                                     if graus[v] == maior]))
    impares = sum(1 for g in graus if g % 2 == 1)
    print(f"\n  Teorema: soma dos graus = {sum(graus)} = 2 x m "
          f"(m = {grafo.m}) -> {'OK' if sum(graus) == 2 * grafo.m else 'ERRO'}")
    print(f"  Teorema: vértices de grau ímpar = {impares} "
          f"(quantidade par) -> {'OK' if impares % 2 == 0 else 'ERRO'}")
    densidade = 0.0
    if grafo.n > 1:
        pares = grafo.n * (grafo.n - 1)
        densidade = grafo.m / pares if grafo.ehOrientado() \
            else 2 * grafo.m / pares
    print(f"  Densidade: {densidade:.3f}")


def opcao_coloracao(grafo):
    """m) Coloração sequencial (vista em aula) em duas ordens de entrada
    dos vértices; a menor quantidade de cores obtida é um limite
    superior para o número cromático X(G)."""
    if grafo.n == 0:
        print("  [aviso] O grafo não possui vértices.")
        return
    natural = grafo.coloracaoSequencial()
    por_grau = grafo.coloracaoPorGrau()
    print("  Coloração sequencial:")
    print(f"   - ordem natural dos vértices (0, 1, 2, ...): "
          f"{len(natural)} cores")
    print(f"   - ordem decrescente de grau:                "
          f"{len(por_grau)} cores")
    melhor = natural if len(natural) <= len(por_grau) else por_grau
    print(f"\n  PARTIÇÃO CROMÁTICA com {len(melhor)} classes "
          f"(X(G) <= {len(melhor)}):")
    for i, classe in enumerate(melhor, start=1):
        print(f"   Cor {i} ({len(classe)} vértices):")
        imprimir_texto_longo(nomes_dos_vertices(grafo, sorted(classe)))
    print("\n  Interpretação: estações da mesma cor não são vizinhas entre "
          "si; cada\n  classe pode ficar em manutenção ao mesmo tempo sem que duas estações"
          "\n  vizinhas fiquem desligadas juntas (as vizinhas cobrem a área).")


def opcao_euleriano(grafo):
    """n) Teorema visto em aula: grafo conexo com 0 vértices de grau ímpar
    é euleriano; com exatamente 2 possui caminho euleriano aberto."""
    if not exige_nao_orientado(grafo):
        return
    situacao, impares = grafo.classificacaoEuleriana()
    print(f"  Conexo: {'sim' if grafo.ehConexo() else 'não'}")
    print(f"  Vértices de grau ímpar: {len(impares)}")
    if impares:
        imprimir_em_linhas([f"{v} {grafo.rotulos[v][:16]} ({grafo.grau(v)})"
                            for v in impares])
    print(f"\n  Resultado: {situacao}")
    if situacao == "EULERIANO":
        print("  Existe um circuito que percorre cada ligação uma única vez "
              "e volta ao início.")
    elif situacao == "SEMI-EULERIANO":
        print(f"  Existe um caminho euleriano aberto, de "
              f"{grafo.rotulos[impares[0]]} até {grafo.rotulos[impares[1]]}.")
    else:
        print("  Não existe percurso que use cada ligação exatamente uma vez."
              "\n  Uma inspeção de todas as ligações teria que repetir "
              "trechos (problema\n  do carteiro chinês).")


def opcao_hamiltoniano(grafo):
    """o) Teoremas 1 (Ore) e 2 (Dirac) vistos em aula, que são condições
    suficientes, e busca de um ciclo hamiltoniano por tentativa e erro."""
    if not exige_nao_orientado(grafo):
        return
    if grafo.n < 3:
        print("  [aviso] São necessários pelo menos 3 vértices.")
        return
    minimo = min(grafo.grau(v) for v in range(grafo.n))
    dirac = grafo.teoremaDirac()
    print(f"  Teorema 2 (Dirac): todo vértice com grau >= n/2 = "
          f"{formatar_numero(grafo.n / 2)}? Grau mínimo = {minimo} -> "
          f"{'satisfeito' if dirac else 'NÃO satisfeito'}")
    ore, falhas = grafo.teoremaOre()
    print(f"  Teorema 1 (Ore): pares não adjacentes com soma dos graus "
          f">= n = {grafo.n}? -> "
          f"{'satisfeito' if ore else f'NÃO satisfeito ({falhas} pares falham)'}")
    if dirac or ore:
        print("  Pelos teoremas, o grafo É hamiltoniano.")
    else:
        print("  Os teoremas são apenas condições suficientes: nada se pode "
              "concluir\n  por eles. Buscando um ciclo por tentativa e erro...")

    ciclo, conclusivo = grafo.cicloHamiltoniano()
    if ciclo is not None:
        total = sum(grafo.pesoA(a, b) for a, b in zip(ciclo, ciclo[1:]))
        print(f"\n  Resultado: HAMILTONIANO. Ciclo encontrado "
              f"({len(ciclo) - 1} arestas, {total:.2f} km):")
        imprimir_em_linhas([f"{v} {grafo.rotulos[v][:20]}" for v in ciclo])
        print("\n  Interpretação: é uma rota de manutenção que visita cada "
              "estação uma única\n  vez, andando só entre estações vizinhas, "
              "e volta ao ponto de partida.")
    elif conclusivo:
        print("\n  Resultado: NÃO HAMILTONIANO (a busca testou todas as "
              "possibilidades).")
    else:
        print("\n  Resultado: INCONCLUSIVO (o limite de tentativas foi "
              "atingido).")


def main():
    grafo = None
    # opções que precisam de um grafo em memória
    opcoes_com_grafo = {
        "b": opcao_gravar,
        "c": opcao_inserir_vertice,
        "d": opcao_inserir_aresta,
        "e": opcao_remover_vertice,
        "f": opcao_remover_aresta,
        "h": lambda g: g.show(),
        "i": opcao_conexidade,
        "j": opcao_regioes,
        "k": opcao_rota_e_centro,
        "l": opcao_graus,
        "m": opcao_coloracao,
        "n": opcao_euleriano,
        "o": opcao_hamiltoniano,
    }
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
        elif opcao == "p":
            print("  Aplicação encerrada.")
            break
        elif opcao in opcoes_com_grafo:
            if grafo_carregado(grafo):
                opcoes_com_grafo[opcao](grafo)
        else:
            print(f"  [erro] Opção '{opcao}' inválida.")


if __name__ == "__main__":
    main()

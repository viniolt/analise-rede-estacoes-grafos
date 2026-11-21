# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Partes 2 e 3
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

Histórico de alterações:
    28/09/2026 - Vinícius Pereira Rodrigues - versão da Parte 2: lista de
                 adjacência, leitura/gravação do grafo.txt e conexidade.
    21/11/2026 - Vinícius Pereira Rodrigues - Parte 3: algoritmos de
                 Kruskal (AGM e agrupamento em regiões), Dijkstra
                 (caminho mínimo e excentricidade), graus, coloração
                 sequencial, percursos euleriano e hamiltoniano.

Síntese:
    Classe Grafo implementada como LISTA DE ADJACÊNCIA, derivada da classe
    Grafo (grafoLista.py) apresentada em aula pelo Prof. Ivan. Foram
    mantidos os nomes dos métodos originais (insereA, removeA, show) e
    acrescentados:
        - tipo do grafo (0 a 7, conforme o enunciado);
        - rótulo e peso de cada vértice;
        - peso das arestas (cada item da lista é o par [destino, peso]);
        - inserção e remoção de vértices (com renumeração);
        - leitura e gravação no formato do arquivo grafo.txt;
        - conexidade: conexo/desconexo (não orientado) ou categorias
          C3, C2, C1, C0 (orientado), componentes fortemente conexas pelo
          algoritmo FCONEX e grafo reduzido.
    Parte 3 (técnicas vistas em aula):
        - árvore geradora de custo mínimo (Kruskal) e divisão da árvore
          em k regiões (retirada das arestas mais pesadas);
        - caminho mínimo (Dijkstra) e excentricidade / centro do grafo;
        - graus dos vértices;
        - coloração sequencial (partições cromáticas);
        - verificação de grafo euleriano (teorema dos graus ímpares);
        - verificação de grafo hamiltoniano (teoremas de Ore e Dirac e
          busca de ciclo por tentativa e erro).
    Em grafos não orientados cada aresta {v, w} é guardada nas duas listas
    (v -> w e w -> v), mas conta como UMA aresta em m.
"""

import shlex

# Descrição de cada tipo de grafo aceito no arquivo grafo.txt
DESCRICAO_TIPOS = {
    0: "grafo não orientado sem peso",
    1: "grafo não orientado com peso no vértice",
    2: "grafo não orientado com peso na aresta",
    3: "grafo não orientado com peso nos vértices e arestas",
    4: "grafo orientado sem peso",
    5: "grafo orientado com peso no vértice",
    6: "grafo orientado com peso na aresta",
    7: "grafo orientado com peso nos vértices e arestas",
}


def formatar_numero(valor):
    """Mostra 3.0 como 3 e 3.25 como 3.25 (evita zeros desnecessários)."""
    return f"{valor:g}"


class Grafo:
    TAM_MAX_DEFAULT = 100  # qtde de vértices máxima default (classe original)

    # construtor da classe grafo
    def __init__(self, tipo=3):
        self.tipo = tipo
        self.n = 0          # número de vértices
        self.m = 0          # número de arestas
        self.listaAdj = []  # listaAdj[v] = lista de pares [w, peso]
        self.rotulos = []   # rótulo (apelido) de cada vértice
        self.pesosV = []    # peso de cada vértice

    # ------------------------------------------------------------------
    # Propriedades do tipo
    # ------------------------------------------------------------------
    def ehOrientado(self):
        return self.tipo >= 4

    def temPesoVertice(self):
        return self.tipo in (1, 3, 5, 7)

    def temPesoAresta(self):
        return self.tipo in (2, 3, 6, 7)

    def verticeValido(self, v):
        return 0 <= v < self.n

    # ------------------------------------------------------------------
    # Vértices
    # ------------------------------------------------------------------
    def insereV(self, rotulo, peso=0.0):
        """Insere um novo vértice (sem arestas) e devolve o seu número."""
        if self.n >= self.TAM_MAX_DEFAULT:
            raise ValueError(f"limite de {self.TAM_MAX_DEFAULT} vértices")
        self.listaAdj.append([])
        self.rotulos.append(rotulo)
        self.pesosV.append(peso)
        self.n += 1
        return self.n - 1

    def removeV(self, v):
        """Remove o vértice v, todas as arestas incidentes a ele, e
        renumera os vértices seguintes (w > v passa a ser w - 1)."""
        if not self.verticeValido(v):
            raise ValueError(f"vértice {v} inexistente")
        # remove arestas que saem de v e que chegam em v
        for w, _ in list(self.listaAdj[v]):
            self.removeA(v, w)
        for u in range(self.n):
            if self.existeA(u, v):
                self.removeA(u, v)
        del self.listaAdj[v]
        del self.rotulos[v]
        del self.pesosV[v]
        self.n -= 1
        # renumera os destinos das arestas restantes
        for lista in self.listaAdj:
            for par in lista:
                if par[0] > v:
                    par[0] -= 1

    # ------------------------------------------------------------------
    # Arestas
    # ------------------------------------------------------------------
    def existeA(self, v, w):
        return any(destino == w for destino, _ in self.listaAdj[v])

    def pesoA(self, v, w):
        for destino, peso in self.listaAdj[v]:
            if destino == w:
                return peso
        return None

    # Insere uma aresta no Grafo tal que v é adjacente a w.
    # Devolve False se a aresta já existia ou é um laço.
    def insereA(self, v, w, peso=1.0):
        if not (self.verticeValido(v) and self.verticeValido(w)):
            raise ValueError("vértice inexistente")
        if v == w or self.existeA(v, w):
            return False
        self.listaAdj[v].append([w, peso])
        if not self.ehOrientado():
            self.listaAdj[w].append([v, peso])
        self.m += 1
        return True

    # remove uma aresta v->w do Grafo (e w->v se não orientado).
    # Devolve False se a aresta não existia.
    def removeA(self, v, w):
        if not (self.verticeValido(v) and self.verticeValido(w)):
            raise ValueError("vértice inexistente")
        if not self.existeA(v, w):
            return False
        self.listaAdj[v] = [p for p in self.listaAdj[v] if p[0] != w]
        if not self.ehOrientado():
            self.listaAdj[w] = [p for p in self.listaAdj[w] if p[0] != v]
        self.m -= 1
        return True

    def arestas(self):
        """Lista (v, w, peso) de cada aresta, sem repetir as não orientadas."""
        resultado = []
        for v in range(self.n):
            for w, peso in self.listaAdj[v]:
                if self.ehOrientado() or v < w:
                    resultado.append((v, w, peso))
        return resultado

    def grau(self, v):
        """Grau (não orientado) ou grau de saída (orientado)."""
        return len(self.listaAdj[v])

    # ------------------------------------------------------------------
    # Arquivo grafo.txt
    # ------------------------------------------------------------------
    @classmethod
    def lerArquivo(cls, caminho):
        """Lê o arquivo no formato:
            tipo
            n
            <v> "<rótulo>" <peso do vértice>     (n linhas)
            m
            <v> <w> <peso da aresta>             (m linhas)
        Rótulo e pesos são opcionais conforme o tipo."""
        with open(caminho, encoding="utf-8") as arq:
            linhas = [l.strip() for l in arq if l.strip()]
        tipo = int(linhas[0])
        if tipo not in DESCRICAO_TIPOS:
            raise ValueError(f"tipo de grafo inválido: {tipo}")
        grafo = cls(tipo)
        n = int(linhas[1])
        for i in range(n):
            campos = shlex.split(linhas[2 + i])
            if int(campos[0]) != i:
                raise ValueError(f"vértices fora de ordem na linha {3 + i}")
            rotulo = campos[1] if len(campos) > 1 else str(i)
            peso = float(campos[2]) if len(campos) > 2 else 0.0
            grafo.insereV(rotulo, peso)
        m = int(linhas[2 + n])
        for j in range(m):
            campos = linhas[3 + n + j].split()
            v, w = int(campos[0]), int(campos[1])
            peso = float(campos[2]) if len(campos) > 2 else 1.0
            grafo.insereA(v, w, peso)
        return grafo

    def gravarArquivo(self, caminho):
        """Grava o grafo da memória no mesmo formato usado na leitura."""
        linhas = [str(self.tipo), str(self.n)]
        for v in range(self.n):
            linha = f'{v} "{self.rotulos[v]}"'
            if self.temPesoVertice():
                linha += f" {formatar_numero(self.pesosV[v])}"
            linhas.append(linha)
        arestas = self.arestas()
        linhas.append(str(len(arestas)))
        for v, w, peso in arestas:
            linha = f"{v} {w}"
            if self.temPesoAresta():
                linha += f" {formatar_numero(peso)}"
            linhas.append(linha)
        with open(caminho, "w", encoding="utf-8") as arq:
            arq.write("\n".join(linhas) + "\n")

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------
    # Apresenta o Grafo contendo número de vértices, arestas
    # e a LISTA de adjacência obtida
    def show(self):
        print(f"\n n: {self.n:2d} m: {self.m:2d}  ({DESCRICAO_TIPOS[self.tipo]})")
        for v in range(self.n):
            cabeca = f"{v:2d} {self.rotulos[v][:22]:<22}"
            if self.temPesoVertice():
                cabeca += f" [{formatar_numero(self.pesosV[v]):>6}]"
            itens = []
            for w, peso in self.listaAdj[v]:
                if self.temPesoAresta():
                    itens.append(f"{w}({formatar_numero(peso)})")
                else:
                    itens.append(str(w))
            print(f"{cabeca} -> " + ", ".join(itens))
        print("\nfim da impressao do grafo.")

    # ------------------------------------------------------------------
    # Conexidade
    # ------------------------------------------------------------------
    def _alcancaveis(self, origem, adjacencia):
        """Busca em largura: conjunto de vértices alcançáveis a partir de
        origem usando a lista de adjacência informada."""
        visitados = {origem}
        fila = [origem]
        while fila:
            v = fila.pop(0)
            for w in adjacencia[v]:
                if w not in visitados:
                    visitados.add(w)
                    fila.append(w)
        return visitados

    def _adjSimples(self):
        return [[w for w, _ in self.listaAdj[v]] for v in range(self.n)]

    def _adjInversa(self):
        inversa = [[] for _ in range(self.n)]
        for v in range(self.n):
            for w, _ in self.listaAdj[v]:
                inversa[w].append(v)
        return inversa

    def _adjSubjacente(self):
        """Grafo não orientado subjacente (ignora o sentido das arestas)."""
        adj = self._adjSimples()
        for v in range(self.n):
            for w, _ in self.listaAdj[v]:
                if v not in adj[w]:
                    adj[w].append(v)
        return adj

    def componentesConexas(self):
        """Componentes conexas do grafo não orientado (ou do subjacente)."""
        adj = self._adjSubjacente()
        restantes = set(range(self.n))
        componentes = []
        while restantes:
            origem = min(restantes)
            comp = self._alcancaveis(origem, adj)
            componentes.append(sorted(comp))
            restantes -= comp
        return componentes

    def fconex(self):
        """Algoritmo FCONEX: a componente fortemente conexa de v é a
        interseção do fecho transitivo direto R+(v) com o inverso R-(v)."""
        direta, inversa = self._adjSimples(), self._adjInversa()
        restantes = set(range(self.n))
        componentes = []
        while restantes:
            v = min(restantes)
            comp = (self._alcancaveis(v, direta)
                    & self._alcancaveis(v, inversa) & restantes)
            componentes.append(sorted(comp))
            restantes -= comp
        return componentes

    def grafoReduzido(self):
        """Grafo reduzido: cada componente fortemente conexa vira um
        vértice; há aresta Ci -> Cj se alguma aresta liga Ci a Cj."""
        componentes = self.fconex()
        comp_de = {}
        for i, comp in enumerate(componentes):
            for v in comp:
                comp_de[v] = i
        arestas = set()
        for v in range(self.n):
            for w, _ in self.listaAdj[v]:
                if comp_de[v] != comp_de[w]:
                    arestas.add((comp_de[v], comp_de[w]))
        return componentes, sorted(arestas)

    def categoriaConexidade(self):
        """Grafo orientado: C3 (fortemente conexo), C2 (unilateralmente
        conexo), C1 (fracamente conexo) ou C0 (desconexo)."""
        if self.n == 0:
            return "C0"
        componentes, arestas = self.grafoReduzido()
        if len(componentes) == 1:
            return "C3"
        if len(self.componentesConexas()) > 1:
            return "C0"
        # Unilateral se o grafo reduzido (acíclico) possui caminho que passa
        # por todos os seus vértices: em uma ordenação topológica, cada par
        # consecutivo precisa estar ligado por uma aresta.
        k = len(componentes)
        grau_entrada = [0] * k
        saidas = [[] for _ in range(k)]
        for a, b in arestas:
            saidas[a].append(b)
            grau_entrada[b] += 1
        ordem = []
        fontes = [c for c in range(k) if grau_entrada[c] == 0]
        while fontes:
            if len(fontes) > 1:
                return "C1"  # duas fontes: não há caminho único
            c = fontes.pop()
            ordem.append(c)
            for d in saidas[c]:
                grau_entrada[d] -= 1
                if grau_entrada[d] == 0:
                    fontes.append(d)
        return "C2"

    def conexidade(self):
        """Texto descrevendo a conexidade conforme o tipo do grafo."""
        if not self.ehOrientado():
            componentes = self.componentesConexas()
            situacao = "CONEXO" if len(componentes) <= 1 else "DESCONEXO"
            return situacao, componentes
        return self.categoriaConexidade(), self.fconex()

    def ehConexo(self):
        """True se o grafo (ou o seu subjacente, se orientado) é conexo."""
        return len(self.componentesConexas()) <= 1

    # ==================================================================
    # PARTE 3 - Solução do problema
    # ==================================================================

    # ------------------------------------------------------------------
    # Árvore geradora de custo mínimo - algoritmo de Kruskal
    # ------------------------------------------------------------------
    def kruskal(self):
        """Algoritmo de Kruskal (grafo não orientado).

        As arestas são examinadas em ordem não decrescente de peso; uma
        aresta é escolhida se NÃO fecha ciclo com as já escolhidas. Para
        saber se fecha ciclo, cada vértice guarda o número da sua
        "componente" (subárvore): a aresta v-w fecha ciclo quando v e w já
        estão na mesma componente. Ao escolher a aresta, as duas
        componentes são unidas (todos os vértices de uma recebem o número
        da outra).

        Devolve a lista de arestas (v, w, peso) escolhidas. Se o grafo for
        conexo são n - 1 arestas (árvore); senão, uma floresta.
        """
        componente = list(range(self.n))  # no início, cada vértice sozinho
        escolhidas = []
        for v, w, peso in sorted(self.arestas(), key=lambda a: a[2]):
            if componente[v] != componente[w]:  # não fecha ciclo
                escolhidas.append((v, w, peso))
                antiga, nova = componente[w], componente[v]
                for u in range(self.n):
                    if componente[u] == antiga:
                        componente[u] = nova
            if len(escolhidas) == self.n - 1:
                break
        return escolhidas

    def grafoDiferencaPesos(self):
        """Devolve um NOVO grafo (não orientado, mesmos vértices e mesmas
        arestas) em que o peso de cada aresta v-w passa a ser a diferença
        absoluta entre os pesos dos vértices: |peso(v) - peso(w)|.

        No projeto: as arestas continuam ligando estações vizinhas, mas o
        peso passa a medir o quanto a chuva acumulada das duas é diferente
        (0 = chuva igual)."""
        novo = Grafo(tipo=3)
        for v in range(self.n):
            novo.insereV(self.rotulos[v], self.pesosV[v])
        for v, w, _ in self.arestas():
            diferenca = round(abs(self.pesosV[v] - self.pesosV[w]), 2)
            novo.insereA(v, w, diferenca)
        return novo

    def regioesPorAGM(self, k):
        """Divide os vértices em k regiões usando a árvore geradora mínima
        (agrupamento por AGM).

        Ideia: na AGM, as arestas mais pesadas são as que ligam grupos de
        vértices "diferentes" entre si. Retirando as k - 1 arestas MAIS
        PESADAS da árvore, ela se parte em k subárvores; cada subárvore é
        uma região. Aplicado ao grafo de diferenças de chuva, cada região
        reúne estações vizinhas com chuva parecida.

        Devolve (arvore, regioes, arestas_cortadas), em que arvore são as
        arestas da AGM e regioes é uma lista de listas de vértices.
        """
        arvore = self.kruskal()
        arvore.sort(key=lambda a: a[2])
        qtde_cortes = max(0, min(k - 1, len(arvore)))
        cortadas = arvore[len(arvore) - qtde_cortes:]
        mantidas = arvore[:len(arvore) - qtde_cortes]

        # lista de adjacência só com as arestas mantidas da árvore
        adj = [[] for _ in range(self.n)]
        for v, w, _ in mantidas:
            adj[v].append(w)
            adj[w].append(v)

        # cada componente (busca em largura) é uma região
        restantes = set(range(self.n))
        regioes = []
        while restantes:
            origem = min(restantes)
            regiao = self._alcancaveis(origem, adj)
            regioes.append(sorted(regiao))
            restantes -= regiao
        return arvore, regioes, cortadas

    # ------------------------------------------------------------------
    # Caminho mínimo - algoritmo de Dijkstra
    # ------------------------------------------------------------------
    def dijkstra(self, origem):
        """Algoritmo de Dijkstra (pesos das arestas não negativos).

        Versão simples, como vista em aula: a cada passo escolhe-se, entre
        os vértices ainda não fechados, o de menor distância estimada; ele
        é fechado e as distâncias dos seus vizinhos são relaxadas.

        Devolve (dist, anterior):
            dist[v]     = menor distância de origem até v (inf se não há
                          caminho);
            anterior[v] = vértice anterior a v no caminho mínimo.
        """
        infinito = float("inf")
        dist = [infinito] * self.n
        anterior = [None] * self.n
        fechado = [False] * self.n
        dist[origem] = 0

        for _ in range(self.n):
            # vértice aberto com a menor distância
            v = None
            for u in range(self.n):
                if not fechado[u] and (v is None or dist[u] < dist[v]):
                    v = u
            if v is None or dist[v] == infinito:
                break  # os restantes são inalcançáveis
            fechado[v] = True
            # relaxamento das arestas que saem de v
            for w, peso in self.listaAdj[v]:
                if dist[v] + peso < dist[w]:
                    dist[w] = dist[v] + peso
                    anterior[w] = v
        return dist, anterior

    @staticmethod
    def montarCaminho(anterior, destino):
        """Reconstrói o caminho (lista de vértices) até destino a partir do
        vetor anterior devolvido pelo Dijkstra."""
        caminho = []
        v = destino
        while v is not None:
            caminho.append(v)
            v = anterior[v]
        caminho.reverse()
        return caminho

    def excentricidades(self):
        """Excentricidade de cada vértice: a maior das menores distâncias
        dele até os demais (calculada com Dijkstra a partir de cada
        vértice). O(s) vértice(s) de menor excentricidade forma(m) o
        CENTRO do grafo."""
        resultado = []
        for v in range(self.n):
            dist, _ = self.dijkstra(v)
            resultado.append(max(dist))
        return resultado

    # ==================================================================
    # PARTE 3 - Características do grafo
    # ==================================================================

    # ------------------------------------------------------------------
    # Graus
    # ------------------------------------------------------------------
    def grauEntrada(self, v):
        """Grau de entrada (semigrau interior) de v, em grafo orientado."""
        return sum(1 for u in range(self.n) if self.existeA(u, v))

    def grauTotal(self, v):
        """Grau de v: no grafo orientado, grau de entrada + grau de saída."""
        if self.ehOrientado():
            return self.grau(v) + self.grauEntrada(v)
        return self.grau(v)

    # ------------------------------------------------------------------
    # Coloração de vértices - coloração sequencial
    # ------------------------------------------------------------------
    def coloracaoSequencial(self, ordem=None):
        """Coloração sequencial (heurística vista em aula).

        Os vértices são introduzidos um a um (na ordem dada; por padrão
        0, 1, ..., n-1). Para cada vértice procura-se a classe de cor de
        MENOR ordem que não contém nenhum vizinho dele; se nenhuma classe
        aberta serve, abre-se uma nova classe.

        Devolve a lista de classes (cada classe é uma lista de vértices).
        A quantidade de classes é um limite superior do número cromático.
        """
        if ordem is None:
            ordem = range(self.n)
        adj = self._adjSubjacente()
        classes = []
        for v in ordem:
            vizinhos = set(adj[v])
            k = 0
            while k < len(classes) and vizinhos & set(classes[k]):
                k += 1  # a classe k tem vizinho de v: tenta a próxima
            if k == len(classes):
                classes.append([])  # abre uma nova classe de cor
            classes[k].append(v)
        return classes

    def coloracaoPorGrau(self):
        """Coloração sequencial com os vértices em ordem decrescente de
        grau (os mais "difíceis" de colorir entram primeiro)."""
        ordem = sorted(range(self.n), key=lambda v: -self.grauTotal(v))
        return self.coloracaoSequencial(ordem)

    # ------------------------------------------------------------------
    # Percurso euleriano
    # ------------------------------------------------------------------
    def verticesGrauImpar(self):
        return [v for v in range(self.n) if self.grauTotal(v) % 2 == 1]

    def classificacaoEuleriana(self):
        """Teorema visto em aula: um grafo conexo possui caminho euleriano
        se, e somente se, tem 0 ou 2 vértices de grau ímpar.
            0 ímpares -> EULERIANO (circuito euleriano, caminho fechado)
            2 ímpares -> SEMI-EULERIANO (caminho euleriano aberto)
            senão     -> NÃO possui percurso euleriano
        (Para grafos não orientados.)"""
        impares = self.verticesGrauImpar()
        if not self.ehConexo():
            return "NÃO EULERIANO (grafo desconexo)", impares
        if len(impares) == 0:
            return "EULERIANO", impares
        if len(impares) == 2:
            return "SEMI-EULERIANO", impares
        return "NÃO EULERIANO", impares

    # ------------------------------------------------------------------
    # Percurso hamiltoniano
    # ------------------------------------------------------------------
    def teoremaDirac(self):
        """Teorema 2 da aula (condição suficiente): se todo vértice tem
        grau >= n/2, o grafo possui ciclo hamiltoniano."""
        return self.n >= 3 and all(self.grau(v) >= self.n / 2
                                   for v in range(self.n))

    def teoremaOre(self):
        """Teorema 1 da aula (condição suficiente): se, para todo par de
        vértices NÃO adjacentes, a soma dos graus é >= n, o grafo é
        hamiltoniano. Devolve (satisfeito, qtde de pares que falham)."""
        falhas = 0
        for v in range(self.n):
            for w in range(v + 1, self.n):
                if not self.existeA(v, w) and \
                        self.grau(v) + self.grau(w) < self.n:
                    falhas += 1
        return self.n >= 3 and falhas == 0, falhas

    def _buscaHamiltoniana(self, adj, inicio, limite):
        """Tentativa e erro (backtracking) de um ciclo hamiltoniano que
        começa e termina em inicio. Devolve (ciclo ou None, esgotou), em
        que esgotou = True se TODAS as possibilidades foram testadas
        (o limite de passos não foi atingido)."""
        caminho = [inicio]
        no_caminho = [False] * self.n
        no_caminho[inicio] = True
        passos = [0]  # lista para poder ser alterada dentro de tentar()

        def ainda_possivel():
            """Poda: cada vértice fora do caminho precisa de pelo menos 2
            vizinhos ainda "livres" (para entrar e sair dele no ciclo).
            Contam como livres os vértices fora do caminho, a ponta atual
            do caminho e o vértice inicial (onde o ciclo fecha)."""
            ponta = caminho[-1]
            for u in range(self.n):
                if no_caminho[u]:
                    continue
                livres = sum(1 for x in adj[u]
                             if not no_caminho[x] or x in (ponta, inicio))
                if livres < 2:
                    return False
            return True

        def tentar():
            passos[0] += 1
            if passos[0] > limite:
                return False
            v = caminho[-1]
            if len(caminho) == self.n:
                return inicio in adj[v]  # fecha o ciclo no vértice inicial
            if not ainda_possivel():
                return False
            # tenta primeiro os vizinhos com menos opções livres, para não
            # deixar vértices "presos" para o final
            candidatos = [w for w in adj[v] if not no_caminho[w]]
            candidatos.sort(key=lambda w: sum(1 for x in adj[w]
                                              if not no_caminho[x]))
            for w in candidatos:
                caminho.append(w)
                no_caminho[w] = True
                if tentar():
                    return True
                caminho.pop()  # volta atrás (backtracking)
                no_caminho[w] = False
            return False

        if tentar():
            return caminho + [inicio], True
        return None, passos[0] <= limite

    def cicloHamiltoniano(self, limite_por_inicio=50_000):
        """Procura um ciclo hamiltoniano (grafo não orientado).

        Como o problema é NP-completo, a busca por tentativa e erro pode
        demorar muito dependendo do vértice de partida. Por isso ela é
        feita a partir de cada vértice, com um limite de passos para cada
        partida. Devolve (ciclo, conclusivo):
            ciclo      = lista de vértices (o primeiro se repete no fim),
                         ou None se nenhum ciclo foi encontrado;
            conclusivo = True se o resultado é certo. Quando alguma busca
                         testa TODAS as possibilidades sem achar ciclo,
                         então o grafo não possui ciclo hamiltoniano
                         (todo ciclo hamiltoniano passa por qualquer
                         vértice de partida).
        """
        if self.n < 3 or not self.ehConexo():
            return None, True
        adj = self._adjSubjacente()
        for inicio in range(self.n):
            ciclo, esgotou = self._buscaHamiltoniana(adj, inicio,
                                                     limite_por_inicio)
            if ciclo is not None:
                return ciclo, True
            if esgotou:
                return None, True  # busca completa: não existe ciclo
        return None, False  # todas as buscas pararam no limite

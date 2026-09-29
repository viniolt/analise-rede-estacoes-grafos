# -*- coding: utf-8 -*-
"""
Projeto de Teoria dos Grafos - Parte 2
Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas
por meio da Teoria dos Grafos

Integrantes:
    Vinícius Pereira Rodrigues - RA 10729470

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

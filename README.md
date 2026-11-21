# Análise de Padrões Climáticos em uma Rede de Estações Meteorológicas por meio da Teoria dos Grafos

Projeto da disciplina **Teoria dos Grafos** – Universidade Presbiteriana Mackenzie,
Ciência da Computação, turma 6ºG – Prof. Dr. Ivan Carlos Alcântara de Oliveira.

| Integrante | RA |
|---|---|
| Vinícius Pereira Rodrigues | 10729470 |

## O problema

A rede de estações meteorológicas automáticas do **CGE** (Centro de Gerenciamento de
Emergências Climáticas da Prefeitura de São Paulo) é modelada como um grafo para estudar
como as estações se relacionam no espaço. O objetivo é identificar agrupamentos, estações
centrais e estações com comportamento discrepante em relação às suas vizinhas, usando
somente conceitos e algoritmos de Teoria dos Grafos.

## Modelagem

| Elemento | Definição |
|---|---|
| Vértice | Estação do CGE (32 estações) – rótulo: nome da estação |
| Peso do vértice | Precipitação acumulada (mm) de 01/01/2024 a 30/04/2024 |
| Aresta | Vizinhança geográfica: k vizinhos mais próximos (k = 4), simetrizada |
| Peso da aresta | Distância de Haversine (km) |
| Categoria | **Tipo 3** – não orientado, com peso nos vértices e nas arestas |

Resultado: **n = 32, m = 84**, grafo conexo, grau entre 4 e 7.

![Grafo](figuras/grafo_mapa.png)

## Estrutura

```
grafo.txt                    grafo modelado (formato do enunciado)
src/grafo.py                 classe Grafo (lista de adjacência) – base: classe de aula
src/main.py                  aplicação com o menu a) a p)
src/prepara_dados.py         leitura dos CSVs do CGE e agregação na janela comum
src/gera_grafo.py            regra k-NN + Haversine -> grafo.txt e dados/estacoes.graphml
src/analise_preliminar.py    métricas estruturais e comparação com a vizinhança
src/figuras.py               figuras do grafo, das regiões (Parte 3) e dos testes
dados/estacoes_resumo.csv    atributos agregados por estação
dados/estacoes.graphml       grafo para abrir no Gephi (com latitude/longitude)
testes/roda_testes.py        2 ou 3 testes por opção do menu (saídas em testes/saidas/)
testes/grafo_orientado.txt   dígrafo de exemplo para conexidade C0–C3 e grafo reduzido
testes/grafo_pequeno.txt     grafo G'12 da aula (semi-euleriano, não hamiltoniano)
docs/                        relatórios (Partes 2 e 3, docx/pdf) e rubricas
```

## Como executar

Requer Python 3.10+. A aplicação e os testes usam apenas a biblioteca padrão.

```bash
python src/main.py               # aplicação (menu)
python testes/roda_testes.py     # executa os testes e grava testes/saidas/
python src/gera_grafo.py [k]     # regenera grafo.txt a partir de dados/estacoes_resumo.csv
python src/analise_preliminar.py # resultados parciais
```

Scripts opcionais (precisam de `pip install -r requirements.txt`):

```bash
python src/prepara_dados.py <pasta_csvs_cge_2024>   # recria dados/estacoes_resumo.csv
python src/figuras.py                               # recria as figuras
```

## Menu da aplicação

```
Parte 2 – manipulação do grafo
a) Ler dados do arquivo grafo.txt        f) Remover aresta
b) Gravar dados no arquivo grafo.txt     g) Mostrar conteúdo do arquivo
c) Inserir vértice                       h) Mostrar grafo (lista de adjacência)
d) Inserir aresta                        i) Conexidade do grafo e grafo reduzido
e) Remover vértice

Parte 3 – solução do problema
j) Regiões de chuva homogênea (árvore geradora mínima – Kruskal)
k) Rota mínima entre estações e estação central (Dijkstra)

Parte 3 – características do grafo
l) Graus dos vértices                    n) Verificar se o grafo é euleriano
m) Coloração sequencial                  o) Verificar se o grafo é hamiltoniano

p) Encerrar a aplicação
```

## Parte 3 – técnicas e resultados

**Solução do problema (técnicas da disciplina)**

| Opção | Técnica | Resultado na rede do CGE |
|---|---|---|
| j) | Grafo de diferenças (peso da aresta = \|chuva(v) − chuva(w)\|), AGM por **Kruskal** e retirada das k − 1 arestas mais pesadas da árvore | Com k = 4: um bloco principal de 26 estações (média 684 mm), uma região seca no leste (Mooca, Vila Formosa, Vila Prudente, São Mateus – média 499 mm) e duas estações **discrepantes** isoladas: Vila Maria/Guilherme (946 mm) e Santana de Parnaíba (734,8 mm) |
| k) | **Dijkstra** (caminho mínimo) e excentricidade de cada vértice | Rota Perus → Marsilac: 59,43 km em 6 trechos. Estação central (centro do grafo): **Capela do Socorro**, a no máximo 39,17 km de qualquer outra |

**Características do grafo**

| Opção | Técnica | Resultado |
|---|---|---|
| l) | Graus dos vértices | grau mín. 4, máx. 7, médio 5,25; soma dos graus = 168 = 2m; 16 vértices de grau ímpar |
| m) | Coloração sequencial (ordem natural e por grau) | 5 classes de cor → X(G) ≤ 5 |
| n) | Teorema dos vértices de grau ímpar | 16 vértices de grau ímpar → **não euleriano** |
| o) | Teoremas de Ore e Dirac + busca por tentativa e erro | Teoremas não satisfeitos, mas foi encontrado um ciclo → **hamiltoniano** (rota de 306,90 km passando uma vez por cada estação) |

![Regiões](figuras/regioes_agm.png)

## Relatório

- Parte 3 (final): [docs/Relatorio_Projeto_TG_Parte3_VINICIUSRODRIGUES.pdf](docs/Relatorio_Projeto_TG_Parte3_VINICIUSRODRIGUES.pdf)
- Parte 2: [docs/Relatorio_Projeto_TG_Parte2_VINICIUSRODRIGUES.pdf](docs/Relatorio_Projeto_TG_Parte2_VINICIUSRODRIGUES.pdf)

## Vídeo

Link do YouTube: *(a adicionar)*

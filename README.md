# Projeto de Teoria dos Grafos — 2026.1
**CESAR School**

Projeto desenvolvido em duas partes: a Parte 1 modela a rede de aeroportos brasileiros e a Parte 2 analisa o dataset Wikispeedia (navegação entre artigos da Wikipedia). Ambas implementam BFS, DFS, Dijkstra e Bellman-Ford do zero, sem bibliotecas de algoritmos de grafos.

---

## Estrutura do Repositório

```
projeto-grafos/
├── README.md                    # este arquivo
├── requirements.txt             # dependências da Parte 1
├── data/                        # dados da Parte 1
│   ├── aeroportos_data.csv
│   ├── adjacencias_aeroportos.csv
│   └── rotas.csv
├── out/                         # saídas geradas pela Parte 1
├── src/                         # código da Parte 1
│   ├── solve.py
│   ├── viz.py
│   ├── dashboard.py
│   ├── cli.py
│   └── graphs/
│       ├── graph.py
│       ├── io.py
│       └── algorithms.py
├── tests/                       # testes da Parte 1
│   ├── test_bfs.py
│   ├── test_dfs.py
│   ├── test_dijkstra.py
│   └── test_bellman_ford.py
└── PT2/                         # Parte 2 — Wikispeedia
    ├── README.md                # documentação completa da Parte 2
    ├── requirements.txt         # dependências da Parte 2
    ├── data/
    │   └── dataset_parte2/      # articles.tsv, links.tsv, categories.tsv
    ├── out/                     # saídas geradas pela Parte 2
    ├── src/
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── cli.py
    │   ├── graph.py
    │   ├── bfs_dfs.py
    │   ├── dijkstra.py
    │   ├── bellman_ford.py
    │   ├── loader_parte2.py
    │   ├── runner_parte2.py
    │   ├── metrics.py
    │   └── visualizations.py
    └── tests/
        └── test_algorithms.py
```

---

## Parte 1 — Rede de Aeroportos do Brasil

Análise estrutural da rede de aeroportos brasileiros. O grafo modela 20 aeroportos como nós e rotas aéreas como arestas não-direcionadas com pesos, permitindo calcular métricas de conectividade, caminhos mínimos, ego-networks e comparar o desempenho dos algoritmos.

### Instalação

Crie e ative um ambiente virtual na raiz do repositório:

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# ou: venv\Scripts\activate   # Windows
```

Instale as dependências:

```bash
pip3 install -r requirements.txt
```

### Como Executar

```bash
# Calcular todas as métricas e rotas
python3 src/solve.py

# Gerar todas as visualizações e o grafo interativo
python3 src/viz.py

# Gerar apenas o dashboard analítico (requer saídas do solve.py)
python3 src/dashboard.py

# Interface de linha de comando
python3 src/cli.py --help
python3 src/cli.py all              # executa tudo
python3 src/cli.py rota MAO GRU     # rota mínima entre dois aeroportos
python3 src/cli.py info GRU         # informações detalhadas de um aeroporto

# Testes
python3 -m pytest tests/
```

### Saídas Geradas (`out/`)

| Arquivo | Descrição |
|---|---|
| `grafo_interativo.html` | Grafo completo com busca, filtros por região, BFS interativo e Dijkstra no cliente |
| `arvore_percurso.html` | Grafo com as rotas obrigatórias destacadas |
| `dashboard.html` | Dashboard analítico com KPIs, gráficos e tabela filtrável |
| `global.json` | Ordem, tamanho e densidade do grafo completo |
| `regioes.json` | Métricas por região |
| `ego_aeroportos.csv` | Ego-network de cada aeroporto |
| `graus.csv` | Ranking de aeroportos por grau |
| `distancias_rotas.csv` | Caminhos mínimos (Dijkstra) para os pares em `rotas.csv` |
| `viz_*.png` | 10 gráficos estáticos de análise |

### Modelo de Pesos

| Tipo de Conexão | Peso |
|---|---|
| Hub → cidade da mesma região | 1.0 |
| Hub ↔ Hub (regiões diferentes) | 1.5 |
| Cidade → cidade mesma região (sem hub) | 1.5 |
| Hub → cidade fora da região | 2.0 |
| Cidade → cidade inter-regional (sem hub) | 3.0 |

**Hubs regionais:** REC (Nordeste), GRU (Sudeste), POA (Sul), BSB (Centro-Oeste), MAO (Norte)

### Resultados Principais

- **Aeroporto mais conectado:** GRU (grau 7)
- **Rota mais curta:** REC → POA (custo 1.5, conexão direta)
- **Rota mais longa:** BEL → CGH (custo 6.5, 5 escalas)
- **Região mais densa:** Centro-Oeste (densidade 1.0)
- **Algoritmo mais rápido:** BFS (~7,7 µs)

---

## Parte 2 — Wikispeedia: Rede de Navegação Wikipedia

Análise algorítmica do dataset Wikispeedia (Stanford SNAP): 4.604 artigos da Wikipedia como nós e 119.882 hiperlinks como arestas de um grafo **dirigido e ponderado** (peso = `1 / grau_de_saída`).

### Navegação e Instalação

> **Importante:** todos os comandos da Parte 2 devem ser executados dentro da pasta `PT2/`.

```bash
# Entrar na pasta da Parte 2
cd PT2

# Instalar dependências (fa2 e scipy são necessários para o layout ForceAtlas2)
pip install -r requirements.txt
```

### Como Executar

```bash
# Dentro de PT2/ — rodar todos os algoritmos e gerar todas as saídas
python -m src.cli --dataset ./data/dataset_parte2/ --alg ALL --out ./out/
```

> O processo leva ~40–60s na primeira execução (ForceAtlas2 com 500 iterações para o layout do grafo interativo). As saídas ficam em `PT2/out/`.

```bash
# Rodar os testes
python -m pytest tests/ -v
```

### Saídas Geradas (`PT2/out/`)

| Arquivo | Descrição |
|---|---|
| `grafo_interativo.html` | **Entrega principal** — dashboard interativo completo, abre direto no navegador |
| `parte2_report.json` | Resultados de todos os algoritmos, tempos e tabela de desempenho |
| `degree_distribution.png` | Distribuição de graus de saída |
| `in_out_degree_distribution.png` | Comparação de graus de entrada e saída em escala log |
| `degree_in_out_scatter.png` | Dispersão entrada × saída para identificar hubs |
| `weight_distribution.png` | Distribuição dos pesos `1/grau_saída` |
| `performance_bars.png` | Tempo médio por algoritmo |
| `comparison_lines.png` | Tempo por execução individual |
| `bfs_layers.png` | Nós descobertos por camada BFS |
| `dfs_edge_classes.png` | Classificação de arestas no DFS |
| `dijkstra_paths.png` | Distância ponderada versus saltos |
| `bellman_ford_scenarios.png` | Cenários Bellman-Ford com pesos negativos |
| `distance_heatmap.png` | Heatmap de distâncias Dijkstra entre pares |
| `parte2_avd_notes.md` | Notas analíticas para o relatório técnico |

### `grafo_interativo.html` — Funcionalidades

Arquivo HTML autocontido (sem servidor). Abre diretamente no navegador com todos os dados embutidos.

**Aba: Grafo Completo** — 4.604 artigos em Canvas com layout ForceAtlas2, coloridos por categoria. Clique simples expande os 30 vizinhos mais conectados; duplo clique expande todos. Filtro por categoria, busca com autocomplete e zoom com level-of-detail.

**Aba: Ego-Graph** — exploração progressiva com simulação de física D3. Filtro por categoria preservando o nó central.

**Aba: Caminho Mínimo** — Dijkstra rodando no browser. Resultado com distância ponderada, saltos e lista de artigos do caminho destacados com glow branco neon.

**Aba: Análises** — 8 visualizações interativas (cada uma abre em modal com gráfico + 3 seções de insight) e um Dashboard Analítico com KPIs globais e comparativo de desempenho.

### Algoritmos Implementados

| Algoritmo | Complexidade | Casos cobertos |
|---|---|---|
| BFS | O(V + E) | 3 fontes distintas, relato de camadas |
| DFS | O(V + E) | 3 fontes, detecção de ciclos, classificação de arestas |
| Dijkstra | O((V+E) log V) | 5 pares origem-destino |
| Bellman-Ford | O(V · E) | pesos normais, peso negativo sem ciclo, ciclo negativo detectado |

### Pesos Negativos — Justificativa

O grafo Wikispeedia tem pesos naturalmente positivos (`1/grau_saída`). Para atender o requisito do Bellman-Ford, dois cenários foram injetados artificialmente e documentados no `parte2_report.json` com o campo `"scenario"`.

---

## Algoritmos — Visão Geral (ambas as partes)

Todos os algoritmos foram implementados do zero, sem uso de networkx, igraph ou qualquer biblioteca de grafos. A implementação da Parte 1 está em `src/graphs/algorithms.py` e a da Parte 2 em `PT2/src/`.

---

## Declaração de Uso de IA

### Parte 1

Ferramentas de inteligência artificial foram utilizadas como recurso de apoio ao desenvolvimento. Durante a fase de modelagem e implementação, a IA foi consultada para discutir decisões de design dos algoritmos, revisar a lógica de BFS, DFS, Dijkstra e Bellman-Ford, e auxiliar na construção e validação dos testes unitários. Também foi utilizada para apoiar a definição das conexões entre nós, a calibração dos pesos e a justificativa das arestas do grafo de aeroportos.

No desenvolvimento do dashboard analítico (`src/dashboard.py` e `out/dashboard.html`), a IA foi utilizada de forma mais direta como agente de produção de código: auxiliou na geração da estrutura do arquivo, na escrita do CSS e do JavaScript, e na implementação do painel de filtros interativos. O uso foi supervisionado e iterativo — o código produzido foi revisado, ajustado e integrado manualmente ao projeto. A IA funcionou como uma ferramenta que acelerou a produção, mas as decisões de design, estrutura e funcionalidade foram tomadas pelo grupo.

### Parte 2

A IA foi utilizada como agente central de desenvolvimento do `grafo_interativo.html`, dado o nível de complexidade técnica imposto pelo volume do dataset — 4.604 nós e 119.882 arestas. Esse escopo tornou inviáveis as abordagens iniciais (pyvis, D3 com SVG, simulação no browser) e exigiu sucessivas mudanças de tecnologia e estratégia de renderização.

O principal pivô técnico foi a adoção de **Canvas + D3.js** em substituição ao SVG: com milhares de elementos, o SVG trava o browser por criar um nó do DOM por nó do grafo; o Canvas renderiza tudo como pixels sem overhead de DOM. A decisão foi tomada com base em análise das limitações de cada abordagem, conduzida em conjunto com a IA.

A escolha do algoritmo de layout **ForceAtlas2** — o mesmo utilizado pelo Gephi — também envolveu uso direto de IA: o algoritmo não era familiar ao grupo, e a IA auxiliou na compreensão do seu funcionamento (repulsão entre nós, atração por arestas, gravidade central), na configuração dos parâmetros (`scalingRatio`, `gravity`, `barnesHutTheta`) e na decisão de pré-calcular o layout em Python antes de gerar o HTML, em vez de rodar a simulação no browser.

Ao longo do desenvolvimento da visualização, a IA foi utilizada iterativamente para resolver desafios específicos de grafos densos: controle de sobreposição de nós, sistema de level-of-detail por zoom, hit-test com prioridade em nós destacados, reconstrução de arestas sem fantasmas no ego-graph e injeção de dados de grande volume dentro de f-strings Python sem erros de sintaxe. Todas as decisões de design, funcionalidade e estrutura do projeto foram tomadas pelo grupo, com a IA atuando como ferramenta de implementação e diagnóstico técnico.
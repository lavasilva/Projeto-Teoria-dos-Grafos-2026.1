# Projeto — Rede de Aeroportos do Brasil
**Teoria dos Grafos — 2026.1**

## Descrição

Análise estrutural e algorítmica da rede de aeroportos brasileiros com implementação própria de BFS, DFS, Dijkstra e Bellman-Ford. O projeto modela os aeroportos como nós de um grafo não-direcionado e as rotas como arestas com pesos, permitindo calcular métricas de conectividade e caminhos mínimos.

## Documento do Projeto:
https://docs.google.com/document/d/1EWGNU9YuuUsdmRpXTztDNzRiARYBJwFfk8IPl3aJzSE/edit?tab=t.0

## Requisitos

- Python 3.11+
- Dependências listadas em `requirements.txt`

```bash
pip3 install -r requirements.txt
```

---

## Estrutura de Pastas

```
projeto-grafos/
├── README.md
├── requirements.txt
├── data/
│   ├── aeroportos_data.csv          # dataset fornecido
│   ├── adjacencias_aeroportos.csv   # arestas construídas pelo grupo
│   └── rotas.csv                    # pares de aeroportos para cálculo de rotas
├── out/                             # saídas geradas (.json, .csv, .html, .png)
│   └── .gitkeep
├── src/
│   ├── solve.py                     # métricas globais, por região, ego-networks e rotas
│   ├── viz.py                       # visualizações analíticas
│   ├── cli.py                       # interface de linha de comando
│   └── graphs/
│       ├── graph.py                 # estrutura: lista de adjacência
│       ├── io.py                    # carregamento e validação dos CSVs
│       └── algorithms.py            # BFS, DFS, Dijkstra, Bellman-Ford
└── tests/
    ├── test_bfs.py
    ├── test_dfs.py
    ├── test_dijkstra.py
    └── test_bellman_ford.py
```

## Como Executar

### Calcular todas as métricas e rotas

```bash
python3 src/solve.py
```

Gera em `out/`:
- `global.json` — ordem, tamanho e densidade do grafo completo
- `regioes.json` — métricas por região (subgrafo induzido)
- `ego_aeroportos.csv` — ego-network de cada aeroporto
- `graus.csv` — ranking de aeroportos por grau
- `distancias_rotas.csv` — caminhos mínimos (Dijkstra) para os pares em `rotas.csv`

### Gerar visualizações

```bash
python3 src/viz.py
```

Gera em `out/`:
- `arvore_percurso.html` — grafo interativo com rotas destacadas
- `viz_graus_hist.png` — histograma de distribuição de graus
- `viz_ranking_barras.png` — ranking de aeroportos por conectividade
- `viz_regioes_barras.png` — comparação de métricas por região
- `viz_bfs_camadas.png` — camadas BFS a partir de GRU

### Rodar os testes

```bash
python3 -m pytest tests/
```

---

## Modelo de Pesos

As arestas seguem um modelo híbrido com penalidade por região e por ausência de hub:

| Tipo de Conexão | Peso |
|---|---|
| Hub → cidade da mesma região | 1.0 |
| Hub → Hub (regiões diferentes) | 1.5 |
| Cidade → cidade mesma região (sem hub) | 1.5 |
| Hub → cidade fora da região | 2.0 |
| Cidade → cidade inter-regional (sem hub) | 3.0 |

**Hubs regionais:** REC (Nordeste), GRU (Sudeste), POA (Sul), BSB (Centro-Oeste), MAO (Norte)

---

## Algoritmos Implementados

Todos os algoritmos foram implementados do zero em `src/graphs/algorithms.py`, sem uso de bibliotecas externas de grafos (networkx, igraph, graph-tool são proibidos).

- **BFS** — busca em largura, caminho mínimo em número de arestas
- **DFS** — busca em profundidade iterativa
- **Dijkstra** — caminho mínimo com pesos não-negativos (heap)
- **Bellman-Ford** — caminho mínimo com suporte a pesos negativos e detecção de ciclos negativos

---

## Resultados Principais

- **Aeroporto mais conectado:** GRU (grau 7)
- **Rota mais curta:** REC → POA (custo 1.5, conexão direta)
- **Rota mais longa:** BEL → CGH (custo 6.5, 5 escalas)
- **Região mais densa:** Centro-Oeste (densidade 1.0)

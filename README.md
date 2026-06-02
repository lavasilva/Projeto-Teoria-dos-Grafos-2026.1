# Projeto — Rede de Aeroportos do Brasil
**Teoria dos Grafos — 2026.1**

## Descrição

Análise estrutural e algorítmica da rede de aeroportos brasileiros com implementação própria de BFS, DFS, Dijkstra e Bellman-Ford. O projeto modela os aeroportos como nós de um grafo não-direcionado e as rotas como arestas com pesos, permitindo calcular métricas de conectividade e caminhos mínimos.

## Documento do Projeto:
https://docs.google.com/document/d/1EWGNU9YuuUsdmRpXTztDNzRiARYBJwFfk8IPl3aJzSE/edit?tab=t.0

## Instalação

- Requisitos: Python 3.11+
- Clone o repositório e, dentro da pasta do projeto, crie e ative um ambiente virtual antes de instalar as dependências:

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# ou: venv\Scripts\activate   # Windows
```

- em seguida, instale as dependências listadas em `requirements.txt`

```bash
pip3 install -r requirements.txt
```

- A partir daqui, sempre que abrir um novo terminal, rode source venv/bin/activate antes de executar qualquer comando do projeto.


---

## Estrutura de Pastas

```
projeto-grafos/
├── README.md
├── requirements.txt
├── data/
│   ├── aeroportos_data.csv          # lista de aeroportos (código IATA, cidade, região)
│   ├── adjacencias_aeroportos.csv   # arestas construídas pelo grupo (origem, destino, tipo_conexao, justificativa, peso)
│   └── rotas.csv                    # pares de aeroportos para cálculo de caminhos mínimos
├── out/                             # saídas geradas (.json, .csv, .html, .png)
│   └── .gitkeep
├── src/
│   ├── solve.py                     # métricas globais, por região, ego-networks e rotas
│   ├── viz.py                       # visualizações analíticas
    ├── dashboard.py                 # gera out/dashboard.html (dashboard interativo)
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

---

## Descrição dos Dados

**`data/aeroportos_data.csv`** — dataset fornecido pelo professor com 20 aeroportos brasileiros. Colunas: `iata`, `cidade`, `regiao`.

**`data/adjacencias_aeroportos.csv`** — arestas do grafo construídas pelo grupo. Colunas: `origem`, `destino`, `tipo_conexao`, `justificativa`, `peso`. Cada linha representa uma aresta não-direcionada (o sistema espelha automaticamente).

**`data/rotas.csv`** — 6 pares de aeroportos usados para calcular caminhos mínimos via Dijkstra. Colunas: `origem`, `destino`. Inclui o par obrigatório Manaus → São Paulo (MAO → GRU).

---

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
- `arvore_percurso.html` — grafo interativo com rotas obrigatórias destacadas
- `grafo_interativo.html` — grafo completo com tooltip, busca e destaques
- `dashboard.html` — dashboard analítico interativo (KPIs, gráficos, tabela filtrável)
- `viz_graus_hist.png` — histograma de distribuição de graus
- `viz_ranking_barras.png` — ranking de aeroportos por conectividade
- `viz_regioes_barras.png` — comparação de métricas por região
- `viz_bfs_camadas.png` — camadas BFS a partir de GRU
- `viz_densidade_ego.png` — densidade da ego-network por aeroporto
- `viz_custo_rotas.png` — custo das rotas calculadas
- `viz_pizza_regioes.png` — proporção de aeroportos por região
- `viz_hubs_vs_comuns.png` — comparação entre hubs e aeroportos comuns

### Gerar apenas o dashboard

O dashboard pode ser regenerado de forma independente sem rodar o `viz.py` completo. Exige que os arquivos `.csv` e `.json` de `out/` já existam (gerados por `solve.py`):

```bash
python3 src/dashboard.py
```

Abre `out/dashboard.html` no navegador para ver KPIs globais, ranking de aeroportos, comparação por região, rotas Dijkstra, ego-networks e tabela filtrável.

### Usar a interface de linha de comando (CLI)

```bash
# ver todos os comandos disponíveis
python3 src/cli.py --help

# calcular métricas e rotas
python3 src/cli.py solve

# gerar visualizações
python3 src/cli.py viz

# executar tudo de uma vez
python3 src/cli.py all

# calcular rota mínima entre dois aeroportos
python3 src/cli.py rota MAO GRU
python3 src/cli.py rota REC POA

# ver informações detalhadas de um aeroporto
python3 src/cli.py info GRU
python3 src/cli.py info MAO
```

### Rodar os testes

```bash
pip install pytest
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

**Fórmula:** `peso = base + penalidade_regiao + penalidade_hub`

**Hubs regionais:** REC (Nordeste), GRU (Sudeste), POA (Sul), BSB (Centro-Oeste), MAO (Norte)

Pesos negativos não são utilizados na Parte 1. O suporte a pesos negativos e detecção de ciclos negativos está implementado no Bellman-Ford e coberto nos testes.

---

## Algoritmos Implementados

Todos os algoritmos foram implementados do zero em `src/graphs/algorithms.py`, sem uso de bibliotecas externas de grafos (networkx, igraph, graph-tool são proibidos).

- **BFS** — busca em largura; retorna caminho mínimo em número de arestas
- **DFS** — busca em profundidade iterativa (pilha explícita)
- **Dijkstra** — caminho mínimo com pesos não-negativos via min-heap
- **Bellman-Ford** — caminho mínimo com suporte a pesos negativos e detecção de ciclos negativos

---

## Resultados Principais

- **Aeroporto mais conectado:** GRU (grau 7)
- **Rota mais curta:** REC → POA (custo 1.5, conexão direta)
- **Rota mais longa:** BEL → CGH (custo 6.5, 5 escalas)
- **Região mais densa:** Centro-Oeste (densidade 1.0)

---

## Declaração de IA

IA foi usada para o setup inicial do projeto (conexões entre nós, definição de centros e custos).

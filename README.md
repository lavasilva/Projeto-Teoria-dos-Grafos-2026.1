# Projeto — Rede de Aeroportos do Brasil
**Teoria dos Grafos — 2026.1**

## Descrição

Análise estrutural e algorítmica da rede de aeroportos brasileiros com implementação própria de BFS, DFS, Dijkstra e Bellman-Ford. O projeto modela os aeroportos como nós de um grafo não-direcionado e as rotas como arestas com pesos, permitindo calcular métricas de conectividade, caminhos mínimos, ego-networks e comparações de desempenho entre algoritmos.

## Documento do Projeto
https://docs.google.com/document/d/1EWGNU9YuuUsdmRpXTztDNzRiARYBJwFfk8IPl3aJzSE/edit?tab=t.0

## Instalação

- Requisitos: Python 3.11+
- Clone o repositório e, dentro da pasta do projeto, crie e ative um ambiente virtual antes de instalar as dependências:

```bash
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# ou: venv\Scripts\activate   # Windows
```

Em seguida, instale as dependências listadas em `requirements.txt`:

```bash
pip3 install -r requirements.txt
```

A partir daqui, sempre que abrir um novo terminal, rode `source venv/bin/activate` antes de executar qualquer comando do projeto.

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
│   ├── viz.py                       # visualizações analíticas e grafo interativo
│   ├── dashboard.py                 # gera out/dashboard.html (dashboard analítico com filtros)
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
- `grafo_interativo.html` — grafo completo com painel de controle, busca, filtros por região, camadas BFS e Dijkstra interativo no cliente
- `arvore_percurso.html` — grafo interativo com as rotas obrigatórias destacadas por cor
- `dashboard.html` — dashboard analítico com KPIs, gráficos, tabela filtrável e painel de filtros interativos
- `viz_graus_hist.png` — histograma de distribuição de graus
- `viz_ranking_barras.png` — ranking de aeroportos por conectividade
- `viz_regioes_barras.png` — comparação de métricas por região
- `viz_bfs_camadas.png` — camadas BFS a partir de GRU
- `viz_densidade_ego.png` — densidade da ego-network por aeroporto
- `viz_custo_rotas.png` — custo das rotas calculadas
- `viz_pizza_regioes.png` — proporção de aeroportos por região
- `viz_hubs_vs_comuns.png` — comparação entre hubs e aeroportos comuns
- `viz_comparacao_algoritmos.png` — comparação de tempo de execução (BFS, DFS, Dijkstra, Bellman-Ford)
- `viz_scatter_complexidade.png` — crescimento do tempo de execução por tamanho do grafo

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

- **BFS** — busca em largura; retorna caminho mínimo em número de arestas e computa camadas de distância a partir de um nó origem
- **DFS** — busca em profundidade iterativa com pilha explícita; utilizada também para detecção de ciclos no grafo
- **Dijkstra** — caminho mínimo com pesos não-negativos via min-heap; valida a ausência de pesos negativos antes de executar e retorna tanto o custo quanto o caminho completo
- **Bellman-Ford** — caminho mínimo com suporte a pesos negativos; detecta e sinaliza ciclos negativos; utilizado nos testes para verificar corretude do Dijkstra em casos-limite

---

## Visualizações Geradas (`viz.py`)

### Gráficos estáticos

| Arquivo | Descrição |
|---|---|
| `viz_graus_hist.png` | Histograma da distribuição de graus, colorido por região |
| `viz_ranking_barras.png` | Ranking dos 20 aeroportos por grau, hubs destacados em amarelo |
| `viz_regioes_barras.png` | Barras agrupadas comparando ordem, tamanho e densidade por região |
| `viz_bfs_camadas.png` | Camadas BFS a partir de GRU, cada camada em uma cor diferente |
| `viz_densidade_ego.png` | Densidade da ego-network de cada aeroporto, ordenada decrescentemente |
| `viz_custo_rotas.png` | Custo e número de escalas das 6 rotas Dijkstra calculadas |
| `viz_pizza_regioes.png` | Proporção de aeroportos por região geográfica |
| `viz_hubs_vs_comuns.png` | Comparação do grau médio entre hubs regionais e aeroportos comuns |
| `viz_comparacao_algoritmos.png` | Tempo de execução dos quatro algoritmos sobre o grafo completo |
| `viz_scatter_complexidade.png` | Crescimento do tempo de execução por tamanho de subgrafo (5 a 20 nós), com curvas separadas por algoritmo |

### Grafo interativo (`grafo_interativo.html`)

O arquivo `out/grafo_interativo.html` é a principal visualização interativa do projeto. Gerado por `viz_grafo_interativo()` em `viz.py`, renderiza o grafo completo usando a biblioteca **vis-network** com física habilitada e oferece um conjunto de ferramentas de exploração no cliente, sem dependência de servidor.

**Painel lateral esquerdo — controles principais:**

- **Busca por aeroporto:** campo de texto que aceita código IATA ou nome de cidade. Ao digitar, o nó correspondente é destacado no grafo e os demais são esmaecidos, facilitando a localização de aeroportos específicos.
- **Filtro por região:** botões coloridos gerados dinamicamente para cada região (Nordeste, Sudeste, Sul, Centro-Oeste, Norte). Ao clicar em uma região, apenas os aeroportos daquela região permanecem visíveis com suas cores originais; os demais são esmaecidos. Um painel de métricas do subgrafo regional (ordem, tamanho, densidade) é exibido abaixo dos botões. O botão "✕ Limpar filtro" restaura o estado original.
- **Camadas BFS:** slider que filtra o grafo por distância em arestas a partir de GRU (São Paulo/Guarulhos). Cada posição do slider mantém visíveis apenas os aeroportos até aquela camada de profundidade, permitindo explorar a expansão da rede a partir do maior hub. Um rótulo dinâmico indica a camada atual.
- **Resetar destaque:** botão que desfaz qualquer destaque ativo (busca, filtro regional, Dijkstra ou camadas BFS) e restaura o estado visual padrão do grafo.
- **Link para árvore de percurso:** atalho direto para `arvore_percurso.html`, que exibe as rotas obrigatórias destacadas.

**Painel Dijkstra interativo:**

Gaveta expansível no painel lateral que permite calcular o caminho mínimo entre qualquer par de aeroportos diretamente no navegador, sem recarregar a página. O algoritmo de Dijkstra é reimplementado em JavaScript no cliente, utilizando a lista de adjacência do grafo serializada pelo Python no momento da geração. Ao calcular uma rota:

- O custo total e o número de escalas são exibidos em destaque.
- O caminho é renderizado como uma sequência de chips com o código IATA de cada aeroporto.
- Os nós e arestas do caminho são destacados no grafo em roxo (`#a29bfe`), com os demais esmaecidos.

**Painel lateral direito — sidebar analítica:**

Exibe informações detalhadas sobre o nó selecionado ao clicar em qualquer aeroporto: código IATA, cidade, região, grau, métricas da ego-network (ordem, tamanho, densidade) e camada BFS em relação a GRU. Inclui também uma seção de insight contextual com observações pré-calculadas sobre a posição do aeroporto na rede.

**Legenda de regiões:** indica a cor correspondente a cada região geográfica, mantida fixa no painel lateral esquerdo.

**Física e layout:** o grafo usa simulação de física com estabilização automática (150 iterações), permitindo arrastar, soltar e reorganizar os nós livremente. O zoom é feito com scroll do mouse.

---

## Dashboard Analítico (`dashboard.html`)

O dashboard foi desenvolvido como uma **feature adicional** ao projeto, com o objetivo de reunir em uma única página interativa todos os dados e métricas calculados pelo `solve.py`, facilitando a leitura dos resultados e a extração de insights sem a necessidade de abrir múltiplos arquivos ou gráficos separados.

### Arquivo responsável

O dashboard é gerado pelo script `src/dashboard.py`, que pode ser executado de forma independente do `viz.py`. Ele lê os arquivos de saída do `solve.py` (`global.json`, `regioes.json`, `graus.csv`, `ego_aeroportos.csv`, `distancias_rotas.csv`) e produz `out/dashboard.html` como um arquivo HTML autossuficiente, sem dependências de servidor.

```bash
python3 src/dashboard.py
```

### O que o dashboard exibe

**KPIs globais:** oito métricas principais do grafo exibidas em cards no topo da página — número de aeroportos, número de conexões, densidade global, grau médio, maior hub, rota mais curta, rota mais longa e número de regiões cobertas.

**Insights destacados:** faixa com cinco observações analíticas pré-calculadas sobre o grafo, incluindo o hub dominante, a região mais densa, a rota direta mais barata, a rota mais cara e uma síntese sobre o papel dos hubs regionais.

**Ranking por grau:** gráfico de barras horizontal com todos os 20 aeroportos ordenados por grau, hubs destacados em amarelo e aeroportos comuns em azul.

**Distribuição por tipo de conexão:** gráfico de rosca separando conexões regionais e interregionais, com peso médio por tipo.

**Métricas por região:** lista com barra de proporção e os valores de ordem, tamanho e densidade para cada região; e gráfico de barras comparando a densidade regional.

**Caminhos mínimos (Dijkstra):** lista das 6 rotas calculadas com o caminho completo em chips e barra de custo proporcional; e gráfico de dispersão relacionando custo e número de escalas.

**Ego-networks:** heatmap em grade com todos os 20 aeroportos, onde a intensidade da cor reflete a densidade da ego-network; e gráfico de barras comparando o grau médio entre hubs e aeroportos comuns.

**Tabela completa de aeroportos:** tabela com todos os 20 aeroportos contendo IATA, cidade, região, grau, tipo (Hub/comum), densidade da ego-network e ordem da ego-network. Possui campo de busca por texto integrado ao painel de filtros.

### Painel de filtros interativos

O painel de filtros, adicionado sobre as seções do dashboard, permite restringir dinamicamente os dados exibidos no gráfico de ranking e na tabela sem recarregar a página:

- **Filtro por região:** botões coloridos por região; ao selecionar uma, apenas os aeroportos daquela região aparecem no gráfico e na tabela.
- **Filtro por tipo:** chips Hub / Comum / Todos para isolar hubs regionais ou aeroportos comuns.
- **Slider de grau mínimo:** filtra para exibir apenas aeroportos com grau igual ou superior ao valor selecionado (1 a 7).
- **Contador:** indica quantos aeroportos estão visíveis com os filtros ativos (ex.: "6 / 20 aeroportos").
- **Botão resetar:** desfaz todos os filtros ativos de uma vez e limpa o campo de busca.

---

## Resultados Principais

- **Aeroporto mais conectado:** GRU (grau 7)
- **Rota mais curta:** REC → POA (custo 1.5, conexão direta)
- **Rota mais longa:** BEL → CGH (custo 6.5, 5 escalas)
- **Região mais densa:** Centro-Oeste (densidade 1.0)
- **Hub com maior ego-network:** GRU (8 nós, 10 arestas, densidade 0.357)
- **Algoritmo mais rápido:** BFS (~7,7 µs), seguido de DFS, Dijkstra e Bellman-Ford
- **Complexidade verificada:** crescimento de tempo consistente com O(V+E) para BFS/DFS e O((V+E) log V) para Dijkstra

---

## Declaração de IA

Ferramentas de inteligência artificial foram utilizadas ao longo de todo o projeto como recurso de apoio ao desenvolvimento. Durante a fase de modelagem e implementação, a IA foi consultada para tirar dúvidas sobre conceitos de teoria dos grafos, discutir decisões de design dos algoritmos, revisar a lógica de implementação de BFS, DFS, Dijkstra e Bellman-Ford, e auxiliar na construção e validação dos testes unitários. Também foi utilizada para apoiar a definição das conexões entre nós, a calibração dos pesos e a justificativa das arestas do grafo de aeroportos.

No desenvolvimento do dashboard analítico (`src/dashboard.py` e `out/dashboard.html`), a IA foi utilizada de forma mais direta como agente de produção de código: ela auxiliou na geração da estrutura do arquivo, na escrita do CSS e do JavaScript, e na implementação do painel de filtros interativos. O uso foi supervisionado e iterativo — o código produzido foi revisado, ajustado e integrado manualmente ao projeto, não sendo adotado de forma automática ou integral. A IA funcionou como uma ferramenta que acelerou a produção, mas as decisões de design, estrutura e funcionalidade foram tomadas pelo grupo.
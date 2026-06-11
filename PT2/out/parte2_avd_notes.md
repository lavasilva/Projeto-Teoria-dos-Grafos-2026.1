# Notas Analiticas AVD - Parte 2

## Contexto
O dataset Wikispeedia foi modelado como grafo dirigido e ponderado: cada artigo e um no, cada hiperlink e uma aresta, e o peso segue a regra `1 / grau_de_saida`.

## Leitura do Dataset
- Nos: 4604
- Arestas: 119882
- Grau medio de saida: 26.04
- Grau maximo de saida: 294
- Grau mediano de saida: 19

## Insights Visuais
- A distribuicao de graus tem cauda longa: poucos artigos funcionam como hubs, enquanto a maioria concentra poucos links de saida.
- A comparacao entre grau de entrada e saida ajuda a separar artigos que apontam para muitos temas daqueles que recebem muitas referencias.
- O heatmap de Dijkstra evidencia quais pares sao proximos no modelo ponderado e evita confundir distancia infinita com distancia zero.
- Os graficos de desempenho usam cores consistentes por algoritmo para reduzir carga cognitiva e melhorar comparabilidade.

## Comparacao dos Algoritmos
- BFS e adequado quando o objetivo e minimizar numero de saltos, ignorando pesos.
- DFS e adequado para explorar profundidade, ciclos e classificacao de arestas.
- Dijkstra e adequado para pesos nao negativos e caminhos de menor custo no modelo escolhido.
- Bellman-Ford e adequado quando ha pesos negativos, mas seu custo O(V*E) limita o uso no grafo completo.

## Limitacoes AVD
- O grafo completo com 119.882 arestas sofre com sobreposicao visual; por isso filtros, amostragem e transparencia sao essenciais.
- O peso `1 / grau_de_saida` favorece links de artigos especializados e pode reduzir a importancia visual de hubs generalistas.
- Comparar Bellman-Ford com os outros algoritmos exige cuidado, pois ele foi executado em subgrafo controlado para manter viabilidade.

## Arquivos Visuais Gerados
- `degree_distribution.png`
- `in_out_degree_distribution.png`
- `degree_in_out_scatter.png`
- `weight_distribution.png`
- `performance_bars.png`
- `comparison_lines.png`
- `bfs_layers.png`
- `dfs_edge_classes.png`
- `dijkstra_paths.png`
- `bellman_ford_scenarios.png`
- `distance_heatmap.png`
- `grafo_interativo.html`

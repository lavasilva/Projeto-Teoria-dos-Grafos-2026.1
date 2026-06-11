from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "dataset_parte2"
OUT_DIR  = ROOT / "out"

CAT_COLORS = {
    "Science":                 "#34d399",
    "Geography":               "#0ea5e9",
    "People":                  "#c084fc",
    "History":                 "#fde047",
    "Everyday_life":           "#fb923c",
    "Design_and_Technology":   "#4ade80",
    "Countries":               "#bae6fd",
    "Citizenship":             "#e879f9",
    "Language_and_literature": "#f472b6",
    "Religion":                "#fb7c3c",
    "Music":                   "#a78bfa",
    "Business_Studies":        "#fbbf24",
    "IT":                      "#22d3ee",
    "Mathematics":             "#86efac",
    "Art":                     "#f87171",
    "other":                   "#94a3b8",
}


def _label(raw: str) -> str:
    """Decodifica nome de artigo URL-encoded para exibição."""
    return unquote(raw).replace("_", " ")


def _read_articles(data_dir: Path) -> set[str]:
    arts: set[str] = set()
    p = data_dir / "articles.tsv"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                arts.add(line)
    return arts


def _read_categories(data_dir: Path, arts: set[str]) -> dict[str, str]:
    """Categoria de topo (2º segmento) de cada artigo, ex.: Science, Geography."""
    cat: dict[str, str] = {}
    p = data_dir / "categories.tsv"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 2:
                continue
            article, cat_path = parts
            segs = cat_path.split(".")
            top = segs[1] if len(segs) > 1 else segs[0]
            if article not in cat and top in CAT_COLORS:
                cat[article] = top
    for a in arts:
        cat.setdefault(a, "other")
    return cat


def _read_degrees(data_dir: Path, arts: set[str]) -> tuple[dict, dict]:
    out_deg: dict[str, int] = defaultdict(int)
    in_deg: dict[str, int] = defaultdict(int)
    p = data_dir / "links.tsv"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("\t")
                if len(parts) == 2 and parts[0] in arts and parts[1] in arts:
                    out_deg[parts[0]] += 1
                    in_deg[parts[1]] += 1
    return out_deg, in_deg


def load_data(data_dir: Path, out_dir: Path) -> dict:
    with open(out_dir / "parte2_report.json", encoding="utf-8") as f:
        report = json.load(f)

    arts = _read_articles(data_dir)
    cat = _read_categories(data_dir, arts)
    out_deg, in_deg = _read_degrees(data_dir, arts)

    cat_counts: dict[str, int] = defaultdict(int)
    for a in arts:
        cat_counts[cat[a]] += 1

    def row(a: str) -> dict:
        o, i = out_deg.get(a, 0), in_deg.get(a, 0)
        return {
            "raw": a,
            "label": _label(a),
            "out": o,
            "in": i,
            "cat": cat.get(a, "other"),
            "tipo": "hub" if o >= i else "autoridade",
        }


    top_out_sel = sorted(arts, key=lambda a: -out_deg.get(a, 0))[:40]
    top_in_sel  = sorted(arts, key=lambda a: -in_deg.get(a, 0))[:40]
    per_cat: dict[str, str] = {}
    for a in arts:
        c = cat[a]
        if c == "other":
            continue
        if c not in per_cat or (out_deg.get(a, 0) + in_deg.get(a, 0)) > (
            out_deg.get(per_cat[c], 0) + in_deg.get(per_cat[c], 0)
        ):
            per_cat[c] = a
    selection = set(top_out_sel) | set(top_in_sel) | set(per_cat.values())
    articles = sorted((row(a) for a in selection), key=lambda r: -r["out"])

    top_out = [row(a) for a in sorted(arts, key=lambda a: -out_deg.get(a, 0))[:15]]
    top_in  = [row(a) for a in sorted(arts, key=lambda a: -in_deg.get(a, 0))[:15]]

    return dict(
        report=report,
        articles=articles,
        cat_counts=dict(sorted(cat_counts.items(), key=lambda kv: -kv[1])),
        top_out=top_out,
        top_in=top_in,
    )


def _js(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def build_dashboard(data: dict, grafo_path: str = "grafo_interativo.html") -> str:
    report   = data["report"]
    articles = data["articles"]
    cat_counts = data["cat_counts"]
    top_out  = data["top_out"]
    top_in   = data["top_in"]

    g = report["graph_description"]
    n = g["num_nodes"]
    m = g["num_edges"]
    deg = g["degree_stats"]
    densidade = m / (n * (n - 1)) if n > 1 else 0  

    dijkstra = [
        {
            "source": d["source"], "target": d["target"],
            "distance": d["distance"], "path_length": d["path_length"],
            "path": d.get("path", []),
        }
        for d in report.get("dijkstra", [])
    ]
    bfs = [
        {"source": b["source"], "layer_sizes": b["layer_sizes"],
         "visited_count": b["visited_count"], "num_layers": b["num_layers"]}
        for b in report.get("bfs", [])
    ]
    dfs = [
        {"source": d["source"], "edge_class_counts": d["edge_class_counts"]}
        for d in report.get("dfs", [])
    ]
    perf = report.get("performance_table", [])
    n_categorias = sum(1 for k in cat_counts if k != "other")

    js_data = (
        "const GLOBAL = "    + _js({
            "num_nodes": n, "num_edges": m, "densidade": densidade,
            "avg": deg.get("avg"), "median": deg.get("median"),
            "max": deg.get("max"), "n_categorias": n_categorias,
        }) + ";\n"
        "const ARTICLES = "  + _js(articles) + ";\n"
        "const CAT_COUNTS = " + _js(cat_counts) + ";\n"
        "const CAT_COLORS = " + _js(CAT_COLORS) + ";\n"
        "const TOP_OUT = "   + _js(top_out) + ";\n"
        "const TOP_IN = "    + _js(top_in) + ";\n"
        "const DIJKSTRA = "  + _js(dijkstra) + ";\n"
        "const BFS = "       + _js(bfs) + ";\n"
        "const DFS = "       + _js(dfs) + ";\n"
        "const PERF = "      + _js(perf) + ";\n"
        "const GRAFO_URL = " + _js(grafo_path) + ";\n"
    )

    return _TEMPLATE.replace("/*__DATA__*/", js_data).replace("__GRAFO_URL__", grafo_path)


# ────────────────────────────────────────────────────────────────────────────
# DECLARAÇÃO DE IA: Template HTML/CSS/JS
# ────────────────────────────────────────────────────────────────────────────
_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard — Wikispeedia · Rede de Artigos</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:#08111f; --surface:#0a1628; --card:#0e1b30; --border:#162035;
  --accent:#2dd4bf; --accent2:#38bdf8; --accent3:#c084fc;
  --text:#e2e8f0; --muted:#3d5570; --green:#22c55e; --amber:#fbbf24; --red:#f87171;
  --font-head:'Syne',sans-serif; --font-mono:'IBM Plex Mono',monospace;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:var(--font-mono);font-size:13px;min-height:100vh;}

header{display:flex;align-items:center;justify-content:space-between;padding:18px 32px 14px;
  border-bottom:1px solid var(--border);background:var(--surface);position:sticky;top:0;z-index:100;}
.header-left h1{font-family:var(--font-head);font-weight:800;font-size:20px;letter-spacing:-.5px;color:var(--accent);}
.header-left p{font-size:11px;color:var(--muted);margin-top:2px;}
.header-btn{display:inline-flex;align-items:center;gap:8px;padding:9px 18px;background:var(--accent);
  color:#04201c;font-family:var(--font-head);font-weight:600;font-size:13px;border-radius:6px;
  text-decoration:none;transition:opacity .15s,transform .15s;}
.header-btn:hover{opacity:.88;transform:translateY(-1px);}

main{padding:28px 32px;max-width:1440px;margin:0 auto;}

.kpi-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px;margin-bottom:28px;}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px 18px;position:relative;overflow:hidden;}
.kpi::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:var(--accent);}
.kpi-label{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:6px;}
.kpi-value{font-family:var(--font-head);font-size:26px;font-weight:800;color:var(--accent);line-height:1;}
.kpi-sub{font-size:10px;color:var(--muted);margin-top:4px;}

.section-title{font-family:var(--font-head);font-weight:600;font-size:12px;text-transform:uppercase;
  letter-spacing:2px;color:var(--muted);margin:0 0 14px;padding-bottom:6px;border-bottom:1px solid var(--border);}

.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:22px;}
.grid-1-2{display:grid;grid-template-columns:1fr 2fr;gap:18px;margin-bottom:22px;}
.grid-2-1{display:grid;grid-template-columns:2fr 1fr;gap:18px;margin-bottom:22px;}
@media(max-width:900px){.grid-2,.grid-1-2,.grid-2-1{grid-template-columns:1fr;}}

.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px 20px;}
.card-title{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--accent2);margin-bottom:14px;font-weight:600;}
.chart-wrap{position:relative;height:240px;}
.chart-wrap-tall{position:relative;height:340px;}

.data-table{width:100%;border-collapse:collapse;font-size:12px;}
.data-table thead th{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);
  padding:6px 10px;text-align:left;border-bottom:1px solid var(--border);font-weight:600;}
.data-table tbody tr{border-bottom:1px solid var(--border);transition:background .12s;}
.data-table tbody tr:hover{background:rgba(255,255,255,.03);}
.data-table tbody td{padding:7px 10px;}
.badge{display:inline-block;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:600;}
.hub-badge{background:rgba(45,212,191,.16);color:var(--accent);border:1px solid rgba(45,212,191,.3);}
.auth-badge{background:rgba(56,189,248,.14);color:var(--accent2);border:1px solid rgba(56,189,248,.28);}

/* filtros */
.filter-bar{display:flex;flex-wrap:wrap;align-items:center;gap:20px;background:var(--surface);
  border:1px solid var(--border);border-radius:10px;padding:14px 20px;margin-bottom:22px;}
.filter-group{display:flex;flex-direction:column;gap:6px;}
.filter-label{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:var(--muted);}
.filter-chips{display:flex;flex-wrap:wrap;gap:5px;max-width:620px;}
.chip{padding:4px 10px;border-radius:20px;font-size:10px;font-family:var(--font-head);font-weight:600;
  border:1px solid var(--border);background:var(--card);color:var(--muted);cursor:pointer;transition:all .15s;user-select:none;}
.chip:hover{border-color:var(--accent);color:var(--text);}
.chip.active{background:var(--accent);color:#04201c;border-color:var(--accent);}
.chip.hub-chip.active{background:var(--accent);color:#04201c;border-color:var(--accent);}
.chip.auth-chip.active{background:var(--accent2);color:#04201c;border-color:var(--accent2);}
.filter-divider{width:1px;height:36px;background:var(--border);}
.slider-wrap{display:flex;align-items:center;gap:8px;}
.slider-wrap input[type=range]{-webkit-appearance:none;appearance:none;width:120px;height:4px;
  background:var(--border);border-radius:2px;outline:none;cursor:pointer;}
.slider-wrap input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;
  border-radius:50%;background:var(--accent);cursor:pointer;}
.slider-val{font-family:var(--font-head);font-weight:700;font-size:13px;color:var(--accent);min-width:26px;}
.filter-reset{margin-left:auto;padding:5px 14px;border-radius:6px;border:1px solid var(--border);
  background:transparent;color:var(--muted);font-family:var(--font-mono);font-size:10px;cursor:pointer;transition:all .15s;}
.filter-reset:hover{border-color:var(--accent);color:var(--accent);}
.filter-count{font-size:10px;color:var(--muted);white-space:nowrap;}
.filter-count span{color:var(--accent);font-weight:700;}

/* listas (categorias, top, rotas) */
.reg-list{display:flex;flex-direction:column;gap:9px;}
.reg-row{display:grid;grid-template-columns:150px 1fr 50px 56px;align-items:center;gap:8px;font-size:11px;}
.reg-bar-bg{height:8px;background:var(--border);border-radius:4px;overflow:hidden;}
.reg-bar-fill{height:100%;border-radius:4px;transition:width .6s cubic-bezier(.22,1,.36,1);}
.reg-name{font-weight:600;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.reg-val{text-align:right;color:var(--muted);}

.tworow{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
@media(max-width:600px){.tworow{grid-template-columns:1fr;}}
.mini-row{display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid var(--border);font-size:11px;}
.mini-row:last-child{border-bottom:none;}
.mini-rank{color:var(--muted);width:18px;text-align:right;}
.mini-name{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.mini-val{color:var(--accent);font-weight:700;}

.rota-row{display:grid;grid-template-columns:1fr 70px;gap:10px;align-items:center;padding:9px 0;
  border-bottom:1px solid var(--border);font-size:11px;}
.rota-row:last-child{border-bottom:none;}
.rota-path{display:flex;flex-wrap:wrap;gap:4px;align-items:center;}
.rota-chip{padding:2px 7px;background:rgba(192,132,252,.15);border:1px solid rgba(192,132,252,.25);
  border-radius:4px;font-size:10px;color:var(--accent3);font-weight:600;}
.rota-arrow{color:var(--muted);font-size:10px;}
.custo-bar-bg{height:6px;background:var(--border);border-radius:3px;overflow:hidden;}
.custo-bar-fill{height:100%;background:linear-gradient(90deg,var(--accent2),var(--accent3));border-radius:3px;}

.insight-strip{background:linear-gradient(135deg,rgba(45,212,191,.07),rgba(56,189,248,.05));
  border:1px solid rgba(45,212,191,.2);border-radius:10px;padding:14px 20px;display:flex;flex-wrap:wrap;gap:24px;margin-bottom:22px;}
.insight-item{display:flex;align-items:flex-start;gap:10px;flex:1;min-width:240px;}
.insight-text{font-size:11px;line-height:1.6;}
.insight-text strong{color:var(--accent);display:block;font-size:11px;margin-bottom:2px;}

.note{font-size:10px;color:var(--muted);margin-top:10px;line-height:1.6;}
footer{text-align:center;padding:24px;font-size:10px;color:var(--muted);border-top:1px solid var(--border);margin-top:32px;}
</style>
</head>
<body>

<header>
  <div class="header-left">
    <h1>🌐 Wikispeedia — Rede de Artigos</h1>
    <p>Dashboard Analítico — Teoria dos Grafos 2026.1 · Parte 2</p>
  </div>
  <a class="header-btn" href="__GRAFO_URL__">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"/></svg>
    Ver Grafo Interativo
  </a>
</header>

<main>
  <div class="kpi-row" id="kpi-row"></div>
  <div class="insight-strip" id="insight-strip"></div>

  <!-- Filtros -->
  <div class="filter-bar">
    <div class="filter-group">
      <span class="filter-label">Categoria</span>
      <div class="filter-chips" id="filter-cats">
        <span class="chip active" data-cat="all">Todas</span>
      </div>
    </div>
    <div class="filter-divider"></div>
    <div class="filter-group">
      <span class="filter-label">Tipo</span>
      <div class="filter-chips">
        <span class="chip active" id="chip-todos" data-tipo="all">Todos</span>
        <span class="chip hub-chip" id="chip-hub" data-tipo="hub">Hub</span>
        <span class="chip auth-chip" id="chip-auth" data-tipo="autoridade">Autoridade</span>
      </div>
    </div>
    <div class="filter-divider"></div>
    <div class="filter-group">
      <span class="filter-label">Grau de saída mínimo</span>
      <div class="slider-wrap">
        <input type="range" id="slider-grau" min="0" max="294" value="0" step="5">
        <span class="slider-val" id="slider-grau-val">0</span>
      </div>
    </div>
    <button class="filter-reset" id="btn-reset-filters">↺ Resetar</button>
    <span class="filter-count" id="filter-count"><span id="fc-num">0</span> artigos no recorte</span>
  </div>

  <!-- Conectividade e Hierarquia -->
  <p class="section-title">Conectividade e Hierarquia</p>
  <div class="grid-2-1">
    <div class="card">
      <div class="card-title">Ranking de Artigos por Grau de Saída</div>
      <div class="chart-wrap-tall"><canvas id="chart-graus"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Hubs vs Autoridades</div>
      <div class="tworow">
        <div>
          <div style="font-size:10px;color:var(--accent);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">↗ Conectores (saída)</div>
          <div id="top-out-list"></div>
        </div>
        <div>
          <div style="font-size:10px;color:var(--accent2);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">↘ Autoridades (entrada)</div>
          <div id="top-in-list"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Análise por Categoria -->
  <p class="section-title">Análise por Categoria</p>
  <div class="grid-1-2">
    <div class="card">
      <div class="card-title">Artigos por Categoria</div>
      <div id="cat-list" class="reg-list"></div>
    </div>
    <div class="card">
      <div class="card-title">Distribuição por Categoria</div>
      <div class="chart-wrap-tall"><canvas id="chart-cat"></canvas></div>
    </div>
  </div>

  <!-- Caminhos Mínimos -->
  <p class="section-title">Caminhos Mínimos (Dijkstra)</p>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Rotas Calculadas</div>
      <div id="rota-list"></div>
      <div class="note">Peso da aresta = 1 / grau de saída da origem. Passar por hubs (grau alto) barateia cada salto.</div>
    </div>
    <div class="card">
      <div class="card-title">Custo Ponderado vs Saltos</div>
      <div class="chart-wrap"><canvas id="chart-rotas"></canvas></div>
    </div>
  </div>

  <!-- Busca em Grafo -->
  <p class="section-title">Busca em Grafo (BFS &amp; DFS)</p>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">BFS — Nós Descobertos por Camada</div>
      <div class="chart-wrap"><canvas id="chart-bfs"></canvas></div>
      <div class="note">A maioria dos 4.604 nós é alcançada já na 2ª–3ª camada: a rede tem diâmetro pequeno (≈ seis graus de separação).</div>
    </div>
    <div class="card">
      <div class="card-title">DFS — Classificação de Arestas</div>
      <div class="chart-wrap"><canvas id="chart-dfs"></canvas></div>
      <div class="note">As ~65.000 arestas de retorno (back) confirmam que o grafo é fortemente cíclico.</div>
    </div>
  </div>

  <!-- Desempenho -->
  <p class="section-title">Desempenho dos Algoritmos</p>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Tempo Médio por Algoritmo (escala log)</div>
      <div class="chart-wrap"><canvas id="chart-perf-time"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Memória Média por Algoritmo</div>
      <div class="chart-wrap"><canvas id="chart-perf-mem"></canvas></div>
      <div class="note">* Bellman-Ford rodou em subgrafo de 200 nós: O(V·E) é inviável no grafo completo (~550M operações).</div>
    </div>
  </div>

  <!-- Tabela -->
  <p class="section-title">Tabela de Artigos (hubs &amp; autoridades)</p>
  <div class="card" style="margin-bottom:22px;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
      <span class="card-title" style="margin:0;">Artigos em destaque</span>
      <input id="search-table" placeholder="Filtrar por nome ou categoria..."
        style="background:var(--surface);border:1px solid var(--border);border-radius:6px;
               padding:5px 10px;color:var(--text);font-family:var(--font-mono);font-size:11px;width:240px;">
    </div>
    <table class="data-table" id="article-table">
      <thead><tr>
        <th>Artigo</th><th>Categoria</th><th>Grau Saída</th><th>Grau Entrada</th><th>Tipo</th><th>Razão E/S</th>
      </tr></thead>
      <tbody id="article-tbody"></tbody>
    </table>
  </div>
</main>

<footer>
  Projeto Teoria dos Grafos 2026.1 · CESAR School · Dataset: Wikispeedia (Stanford SNAP) — articles.tsv, links.tsv, categories.tsv
</footer>

<script>
/*__DATA__*/

Chart.defaults.color = '#3d5570';
Chart.defaults.borderColor = '#162035';
Chart.defaults.font.family = "'IBM Plex Mono', monospace";
Chart.defaults.font.size = 11;

const ALG_COLORS = { BFS:'#22c55e', DFS:'#fbbf24', Dijkstra:'#38bdf8', 'Bellman-Ford':'#f87171' };
const SRC_COLORS = ['#2dd4bf','#38bdf8','#c084fc'];
const EDGE_COLORS = { tree:'#22c55e', back:'#f87171', forward:'#fbbf24', cross:'#38bdf8' };

function catColor(c){ return CAT_COLORS[c] || '#94a3b8'; }
function fmt(n){ return n.toLocaleString('pt-BR'); }

/* ── KPIs ── */
function buildKPIs(){
  const hubOut = TOP_OUT[0];
  const authIn = TOP_IN[0];
  const shortest = [...DIJKSTRA].sort((a,b)=>a.distance-b.distance)[0];
  const kpis = [
    {label:'Artigos', value:fmt(GLOBAL.num_nodes), sub:'nós do grafo dirigido'},
    {label:'Links', value:fmt(GLOBAL.num_edges), sub:'arestas direcionadas'},
    {label:'Densidade Global', value:(GLOBAL.densidade*100).toFixed(2)+'%', sub:'do grafo dirigido completo'},
    {label:'Grau Médio', value:GLOBAL.avg.toFixed(2), sub:'links de saída por artigo'},
    {label:'Maior Hub', value:hubOut.label, sub:`grau de saída ${hubOut.out}`},
    {label:'Maior Autoridade', value:authIn.label, sub:`grau de entrada ${fmt(authIn.in)}`},
    {label:'Caminho Mais Curto', value:shortest.distance.toFixed(4), sub:`${shortest.source.replace(/_/g,' ')} → ${shortest.target.replace(/_/g,' ')}`},
    {label:'Categorias', value:GLOBAL.n_categorias, sub:'temas cobertos'},
  ];
  const row = document.getElementById('kpi-row');
  kpis.forEach(k=>{
    row.innerHTML += `<div class="kpi"><div class="kpi-label">${k.label}</div>
      <div class="kpi-value" style="${k.value.length>10?'font-size:16px;':''}">${k.value}</div>
      <div class="kpi-sub">${k.sub}</div></div>`;
  });
}

function buildInsights(){
  const hub = TOP_OUT[0];
  const topCats = Object.entries(CAT_COUNTS).filter(([k])=>k!=='other').sort((a,b)=>b[1]-a[1]);
  const c1=topCats[0], c2=topCats[1];
  const pct2 = ((c1[1]+c2[1])/GLOBAL.num_nodes*100).toFixed(0);
  const back = DFS[0].edge_class_counts.back;
  const items = [
    {title:'Hub dominante', text:`${hub.label} lidera com grau de saída ${hub.out} — ${(hub.out/GLOBAL.avg).toFixed(0)}× a média (${GLOBAL.avg.toFixed(1)}). Artigos geopolíticos dominam o topo.`},
    {title:'Cauda longa (scale-free)', text:`A mediana de grau é ${GLOBAL.median}, mas o máximo chega a ${GLOBAL.max}. Padrão clássico de redes de conhecimento: poucos hubs, muitos nós comuns.`},
    {title:'Categorias dominantes', text:`${c1[0].replace(/_/g,' ')} (${fmt(c1[1])}) e ${c2[0].replace(/_/g,' ')} (${fmt(c2[1])}) somam ${pct2}% de todos os artigos.`},
    {title:'Passar por hubs barateia', text:`No modelo 1/grau, caminhos que cruzam hubs têm peso menor por aresta — o custo mínimo nem sempre é o de menos saltos.`},
    {title:'Rede fortemente cíclica', text:`O DFS classifica ~${fmt(back)} arestas como "back": quase qualquer sequência de cliques entre artigos fecha um ciclo.`},
  ];
  const strip = document.getElementById('insight-strip');
  items.forEach(i=>{
    strip.innerHTML += `<div class="insight-item"><div class="insight-text"><strong>${i.title}</strong>${i.text}</div></div>`;
  });
}

/* ── Estado de filtro ── */
const filterState = { cat:'all', tipo:'all', grauMin:0 };

function filteredArticles(){
  return ARTICLES.filter(a=>{
    if(filterState.cat!=='all' && a.cat!==filterState.cat) return false;
    if(filterState.tipo!=='all' && a.tipo!==filterState.tipo) return false;
    if(a.out < filterState.grauMin) return false;
    return true;
  });
}

let grausChart=null;
function buildGrausChart(){
  const rows = filteredArticles().slice().sort((a,b)=>b.out-a.out).slice(0,18);
  const labels = rows.map(r=>r.label);
  const values = rows.map(r=>r.out);
  const colors = rows.map(r=>catColor(r.cat));
  if(grausChart){
    grausChart.data.labels=labels;
    grausChart.data.datasets[0].data=values;
    grausChart.data.datasets[0].backgroundColor=colors;
    grausChart._rows=rows;
    grausChart.update();
    return;
  }
  const ctx=document.getElementById('chart-graus');
  grausChart=new Chart(ctx,{
    type:'bar',
    data:{labels,datasets:[{label:'Grau de saída',data:values,backgroundColor:colors,borderRadius:4,borderSkipped:false}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>{
        const r=grausChart._rows[ctx.dataIndex];
        return ` saída ${r.out} · entrada ${r.in} · ${r.cat.replace(/_/g,' ')} [${r.tipo}]`;
      }}}},
      scales:{x:{grid:{color:'#162035'}},y:{grid:{display:false}}}}
  });
  grausChart._rows=rows;
}

function buildTopLists(){
  const out=document.getElementById('top-out-list');
  TOP_OUT.slice(0,10).forEach((r,i)=>{
    out.innerHTML += `<div class="mini-row"><span class="mini-rank">${i+1}</span>
      <span class="mini-name" title="${r.label} · ${r.cat.replace(/_/g,' ')}" style="color:${catColor(r.cat)}">${r.label}</span>
      <span class="mini-val">${r.out}</span></div>`;
  });
  const inn=document.getElementById('top-in-list');
  TOP_IN.slice(0,10).forEach((r,i)=>{
    inn.innerHTML += `<div class="mini-row"><span class="mini-rank">${i+1}</span>
      <span class="mini-name" title="${r.label} · ${r.cat.replace(/_/g,' ')}" style="color:${catColor(r.cat)}">${r.label}</span>
      <span class="mini-val" style="color:var(--accent2)">${fmt(r.in)}</span></div>`;
  });
}

function buildCategorias(){
  const entries=Object.entries(CAT_COUNTS).filter(([k])=>k!=='other').sort((a,b)=>b[1]-a[1]);
  const maxC=Math.max(...entries.map(e=>e[1]));
  const list=document.getElementById('cat-list');
  entries.forEach(([cat,cnt])=>{
    const cor=catColor(cat);
    const pct=(cnt/maxC*100).toFixed(0);
    const share=(cnt/GLOBAL.num_nodes*100).toFixed(1);
    list.innerHTML += `<div class="reg-row">
      <span class="reg-name" style="color:${cor}" title="${cat.replace(/_/g,' ')}">${cat.replace(/_/g,' ')}</span>
      <div class="reg-bar-bg"><div class="reg-bar-fill" style="width:${pct}%;background:${cor};"></div></div>
      <span class="reg-val">${fmt(cnt)}</span>
      <span class="reg-val" style="color:${cor}">${share}%</span>
    </div>`;
  });

  new Chart(document.getElementById('chart-cat'),{
    type:'bar',
    data:{labels:entries.map(e=>e[0].replace(/_/g,' ')),
      datasets:[{label:'Artigos',data:entries.map(e=>e[1]),
        backgroundColor:entries.map(e=>catColor(e[0])),borderRadius:5,borderSkipped:false}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>{
        const share=(ctx.parsed.x/GLOBAL.num_nodes*100).toFixed(1);
        return ` ${fmt(ctx.parsed.x)} artigos (${share}%)`;
      }}}},
      scales:{x:{grid:{color:'#162035'}},y:{grid:{display:false}}}}
  });
}

function buildRotas(){
  const maxD=Math.max(...DIJKSTRA.map(d=>d.distance));
  const list=document.getElementById('rota-list');
  DIJKSTRA.forEach(d=>{
    const chips=(d.path||[]).map((c,i,arr)=>i<arr.length-1
      ? `<span class="rota-chip">${c.replace(/_/g,' ')}</span><span class="rota-arrow">→</span>`
      : `<span class="rota-chip">${c.replace(/_/g,' ')}</span>`).join('');
    const pct=(d.distance/maxD*100).toFixed(0);
    list.innerHTML += `<div class="rota-row">
      <div class="rota-path">${chips}</div>
      <div><div style="font-size:10px;color:var(--accent);text-align:right;margin-bottom:2px;">${d.distance.toFixed(4)}</div>
      <div class="custo-bar-bg"><div class="custo-bar-fill" style="width:${pct}%;"></div></div></div>
    </div>`;
  });

  const pts=DIJKSTRA.map(d=>({x:d.path_length-1,y:d.distance,label:`${d.source.replace(/_/g,' ')}→${d.target.replace(/_/g,' ')}`}));
  new Chart(document.getElementById('chart-rotas'),{
    type:'scatter',
    data:{datasets:[{label:'Rotas',data:pts,backgroundColor:'#c084fc',pointRadius:9,pointHoverRadius:12}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>`${ctx.raw.label}: custo ${ctx.raw.y.toFixed(4)}, ${ctx.raw.x} salto(s)`}}},
      scales:{x:{title:{display:true,text:'Saltos',color:'#3d5570'},grid:{color:'#162035'},ticks:{stepSize:1}},
        y:{title:{display:true,text:'Custo ponderado',color:'#3d5570'},grid:{color:'#162035'}}}}
  });
}

function buildBFS(){
  const maxLayer=Math.max(...BFS.map(b=>Math.max(...Object.keys(b.layer_sizes).map(Number))));
  const labels=Array.from({length:maxLayer+1},(_,i)=>'Camada '+i);
  const datasets=BFS.map((b,i)=>({
    label:b.source.replace(/_/g,' '),
    data:labels.map((_,k)=>b.layer_sizes[k]||0),
    backgroundColor:SRC_COLORS[i%SRC_COLORS.length],borderRadius:3,borderSkipped:false,
  }));
  new Chart(document.getElementById('chart-bfs'),{
    type:'bar',data:{labels,datasets},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:'top',labels:{boxWidth:10,padding:8,font:{size:10}}},
        tooltip:{callbacks:{label:ctx=>` ${ctx.dataset.label}: ${fmt(ctx.parsed.y)} nós`}}},
      scales:{x:{grid:{display:false}},y:{grid:{color:'#162035'},title:{display:true,text:'nós descobertos',color:'#3d5570'}}}}
  });
}

function buildDFS(){
  const classes=['tree','back','forward','cross'];
  const datasets=classes.map(cl=>({
    label:cl,
    data:DFS.map(d=>d.edge_class_counts[cl]||0),
    backgroundColor:EDGE_COLORS[cl],borderRadius:3,borderSkipped:false,
  }));
  new Chart(document.getElementById('chart-dfs'),{
    type:'bar',
    data:{labels:DFS.map(d=>d.source.replace(/_/g,' ')),datasets},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:'top',labels:{boxWidth:10,padding:8,font:{size:10}}},
        tooltip:{callbacks:{label:ctx=>` ${ctx.dataset.label}: ${fmt(ctx.parsed.x)} arestas`}}},
      scales:{x:{stacked:true,grid:{color:'#162035'}},y:{stacked:true,grid:{display:false}}}}
  });
}

function perfByAlg(){
  const map={};
  PERF.forEach(p=>{
    if(!map[p.algorithm]) map[p.algorithm]={t:[],m:[]};
    map[p.algorithm].t.push(p.time_s);
    map[p.algorithm].m.push(p.mem_kb);
  });
  const algs=Object.keys(map);
  return algs.map(a=>({
    alg:a,
    time:map[a].t.reduce((s,v)=>s+v,0)/map[a].t.length,
    mem:(map[a].m.reduce((s,v)=>s+v,0)/map[a].m.length)/1024,
  }));
}

function buildPerf(){
  const data=perfByAlg();
  const cpx={BFS:'O(V+E)',DFS:'O(V+E)',Dijkstra:'O((V+E)·logV)','Bellman-Ford':'O(V·E)'};
  new Chart(document.getElementById('chart-perf-time'),{
    type:'bar',
    data:{labels:data.map(d=>d.alg),datasets:[{label:'Tempo (s)',data:data.map(d=>d.time),
      backgroundColor:data.map(d=>ALG_COLORS[d.alg]||'#94a3b8'),borderRadius:5,borderSkipped:false}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>` ${ctx.parsed.y.toFixed(4)} s  ·  ${cpx[ctx.label]||''}`}}},
      scales:{y:{type:'logarithmic',grid:{color:'#162035'},title:{display:true,text:'segundos (log)',color:'#3d5570'}},
        x:{grid:{display:false}}}}
  });
  new Chart(document.getElementById('chart-perf-mem'),{
    type:'bar',
    data:{labels:data.map(d=>d.alg),datasets:[{label:'Memória (MB)',data:data.map(d=>d.mem),
      backgroundColor:data.map(d=>ALG_COLORS[d.alg]||'#94a3b8'),borderRadius:5,borderSkipped:false}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>` ${ctx.parsed.y.toFixed(2)} MB`}}},
      scales:{y:{grid:{color:'#162035'},title:{display:true,text:'MB',color:'#3d5570'},beginAtZero:true},
        x:{grid:{display:false}}}}
  });
}

function rebuildTable(textFilter){
  const rows=filteredArticles().slice().sort((a,b)=>b.out-a.out);
  const tbody=document.getElementById('article-tbody');
  tbody.innerHTML='';
  rows.filter(r=>!textFilter||r.label.toLowerCase().includes(textFilter)||r.cat.toLowerCase().includes(textFilter))
    .forEach(r=>{
      const cor=catColor(r.cat);
      const ratio=r.out>0?(r.in/r.out):0;
      tbody.innerHTML += `<tr>
        <td><b style="color:var(--accent2);">${r.label}</b></td>
        <td><span style="color:${cor};font-weight:600;">${r.cat.replace(/_/g,' ')}</span></td>
        <td style="color:var(--accent);">${r.out}</td>
        <td style="color:var(--accent2);">${fmt(r.in)}</td>
        <td>${r.tipo==='hub'?'<span class="badge hub-badge">Hub</span>':'<span class="badge auth-badge">Autoridade</span>'}</td>
        <td style="color:var(--muted);">${ratio.toFixed(2)}×</td>
      </tr>`;
    });
}

function applyFilters(){
  document.getElementById('fc-num').textContent=filteredArticles().length;
  buildGrausChart();
  rebuildTable(document.getElementById('search-table').value.toLowerCase().trim());
}

function initFilterUI(){
  const wrap=document.getElementById('filter-cats');
  Object.keys(CAT_COUNTS).filter(c=>c!=='other').forEach(cat=>{
    const chip=document.createElement('span');
    chip.className='chip';chip.dataset.cat=cat;chip.textContent=cat.replace(/_/g,' ');
    chip.style.borderColor=catColor(cat);
    chip.addEventListener('click',()=>{
      filterState.cat=cat;
      wrap.querySelectorAll('.chip').forEach(c=>{c.classList.remove('active');c.style.background='';c.style.color='';});
      chip.classList.add('active');chip.style.background=catColor(cat);chip.style.color='#04201c';
      applyFilters();
    });
    wrap.appendChild(chip);
  });
  wrap.querySelector('[data-cat="all"]').addEventListener('click',()=>{
    filterState.cat='all';
    wrap.querySelectorAll('.chip').forEach(c=>{c.classList.remove('active');c.style.background='';c.style.color='';});
    wrap.querySelector('[data-cat="all"]').classList.add('active');
    applyFilters();
  });

  ['chip-todos','chip-hub','chip-auth'].forEach(id=>{
    document.getElementById(id).addEventListener('click',()=>{
      filterState.tipo={'chip-todos':'all','chip-hub':'hub','chip-auth':'autoridade'}[id];
      ['chip-todos','chip-hub','chip-auth'].forEach(c=>document.getElementById(c).classList.remove('active'));
      document.getElementById(id).classList.add('active');
      applyFilters();
    });
  });

  const slider=document.getElementById('slider-grau');
  const sliderVal=document.getElementById('slider-grau-val');
  slider.max=GLOBAL.max;
  slider.addEventListener('input',()=>{
    filterState.grauMin=parseInt(slider.value);
    sliderVal.textContent=slider.value;
    applyFilters();
  });

  document.getElementById('btn-reset-filters').addEventListener('click',()=>{
    filterState.cat='all';filterState.tipo='all';filterState.grauMin=0;
    slider.value=0;sliderVal.textContent='0';
    wrap.querySelectorAll('.chip').forEach(c=>{c.classList.remove('active');c.style.background='';c.style.color='';});
    wrap.querySelector('[data-cat="all"]').classList.add('active');
    ['chip-todos','chip-hub','chip-auth'].forEach(c=>document.getElementById(c).classList.remove('active'));
    document.getElementById('chip-todos').classList.add('active');
    document.getElementById('search-table').value='';
    applyFilters();
  });

  document.getElementById('search-table').addEventListener('input',e=>{
    rebuildTable(e.target.value.toLowerCase().trim());
  });
}

buildKPIs();
buildInsights();
buildGrausChart();
buildTopLists();
buildCategorias();
buildRotas();
buildBFS();
buildDFS();
buildPerf();
rebuildTable('');
initFilterUI();
document.getElementById('fc-num').textContent=ARTICLES.length;
</script>
</body>
</html>
"""


def generate_dashboard(
    data_dir: Path = DATA_DIR,
    out_dir: Path = OUT_DIR,
    grafo_path: str = "grafo_interativo.html",
) -> Path:
    data = load_data(data_dir, out_dir)
    html = build_dashboard(data, grafo_path=grafo_path)
    out_path = out_dir / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


if __name__ == "__main__":
    out_dir  = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT_DIR
    data_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DATA_DIR
    path = generate_dashboard(data_dir=data_dir, out_dir=out_dir)
    print(f"Dashboard gerado: {path}")

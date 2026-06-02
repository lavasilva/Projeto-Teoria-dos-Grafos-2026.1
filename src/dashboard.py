from __future__ import annotations
import json
import csv
import sys
from pathlib import Path

ROOT     = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
OUT_DIR  = ROOT / "out"

REGIAO_CORES = {
    "Nordeste":     "#e67e22",
    "Sudeste":      "#1a6fa8",
    "Sul":          "#27ae60",
    "Centro-Oeste": "#8e44ad",
    "Norte":        "#c0392b",
}

HUBS = {"REC", "GRU", "POA", "BSB", "MAO"}


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_data(data_dir: Path, out_dir: Path) -> dict:
    aeroportos   = _read_csv(data_dir / "aeroportos_data.csv")
    adjacencias  = _read_csv(data_dir / "adjacencias_aeroportos.csv")
    rotas_in     = _read_csv(data_dir / "rotas.csv")
    graus        = _read_csv(out_dir  / "graus.csv")
    ego          = _read_csv(out_dir  / "ego_aeroportos.csv")
    distancias   = _read_csv(out_dir  / "distancias_rotas.csv")

    with open(out_dir / "global.json", encoding="utf-8") as f:
        global_m = json.load(f)
    with open(out_dir / "regioes.json", encoding="utf-8") as f:
        regioes = json.load(f)

    return dict(
        aeroportos=aeroportos,
        adjacencias=adjacencias,
        rotas_in=rotas_in,
        graus=graus,
        ego=ego,
        distancias=distancias,
        global_m=global_m,
        regioes=regioes,
    )



def _js(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)



def build_dashboard(data: dict, grafo_path: str = "grafo_interativo.html") -> str:
    aeroportos  = data["aeroportos"]
    adjacencias = data["adjacencias"]
    graus       = data["graus"]
    ego         = data["ego"]
    distancias  = data["distancias"]
    global_m    = data["global_m"]
    regioes     = data["regioes"]

    graus_sorted     = sorted(graus,      key=lambda r: int(r["grau"]),           reverse=True)
    ego_sorted       = sorted(ego,        key=lambda r: float(r["grau"]),         reverse=True)
    dist_sorted      = sorted(distancias, key=lambda r: float(r["custo"]),        reverse=True)
    regioes_sorted   = sorted(regioes,    key=lambda r: r["ordem"],               reverse=True)

    iata_to_info = {a["iata"]: a for a in aeroportos}
    iata_to_grau = {r["aeroporto"]: int(r["grau"]) for r in graus}
    iata_to_ego  = {r["aeroporto"]: r for r in ego}

    tipo_count: dict[str, int] = {}
    peso_vals: list[float] = []
    for row in adjacencias:
        t = row["tipo_conexao"]
        tipo_count[t] = tipo_count.get(t, 0) + 1
        peso_vals.append(float(row["peso"]))

    grau_vals = [int(r["grau"]) for r in graus]
    grau_medio = sum(grau_vals) / len(grau_vals) if grau_vals else 0

    tipo_peso_sum: dict[str, float] = {}
    tipo_peso_cnt: dict[str, int]   = {}
    for row in adjacencias:
        t = row["tipo_conexao"]
        p = float(row["peso"])
        tipo_peso_sum[t] = tipo_peso_sum.get(t, 0) + p
        tipo_peso_cnt[t] = tipo_peso_cnt.get(t, 0) + 1
    tipo_peso_avg = {t: tipo_peso_sum[t] / tipo_peso_cnt[t] for t in tipo_peso_sum}

    hubs_grau   = [{"iata": r["aeroporto"], "grau": int(r["grau"])} for r in graus if r["aeroporto"] in HUBS]
    others_grau = [{"iata": r["aeroporto"], "grau": int(r["grau"])} for r in graus if r["aeroporto"] not in HUBS]

    js_data = f"""
const GLOBAL      = {_js(global_m)};
const REGIOES     = {_js(regioes_sorted)};
const GRAUS       = {_js(graus_sorted)};
const EGO         = {_js(ego_sorted)};
const DISTANCIAS  = {_js(dist_sorted)};
const TIPO_COUNT  = {_js(tipo_count)};
const TIPO_PESO   = {_js(tipo_peso_avg)};
const REGIAO_CORES= {_js(REGIAO_CORES)};
const IATA_INFO   = {_js(iata_to_info)};
const HUBS_SET    = {_js(list(HUBS))};
const GRAU_MEDIO  = {grau_medio:.4f};
const HUBS_GRAU   = {_js(hubs_grau)};
const OTHERS_GRAU = {_js(others_grau)};
const ADJACENCIAS = {_js(adjacencias)};
const GRAFO_URL   = {_js(grafo_path)};
"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard — Rede de Aeroportos do Brasil</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg:      #0d0e14;
  --surface: #13141d;
  --card:    #191a26;
  --border:  #252636;
  --accent:  #f1c40f;
  --accent2: #7ec8e3;
  --accent3: #a29bfe;
  --text:    #e2e8f0;
  --muted:   #64748b;
  --font-head: 'Syne', sans-serif;
  --font-mono: 'IBM Plex Mono', monospace;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-mono);
  font-size: 13px;
  min-height: 100vh;
}}

/* ── TOPO ── */
header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 32px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  position: sticky;
  top: 0;
  z-index: 100;
}}
.header-left h1 {{
  font-family: var(--font-head);
  font-weight: 800;
  font-size: 20px;
  letter-spacing: -0.5px;
  color: var(--accent);
}}
.header-left p {{
  font-size: 11px;
  color: var(--muted);
  margin-top: 2px;
}}
.header-btn {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px;
  background: var(--accent);
  color: #000;
  font-family: var(--font-head);
  font-weight: 600;
  font-size: 13px;
  border-radius: 6px;
  text-decoration: none;
  transition: opacity .15s, transform .15s;
}}
.header-btn:hover {{ opacity: .88; transform: translateY(-1px); }}
.header-btn svg {{ flex-shrink: 0; }}

/* ── LAYOUT ── */
main {{
  padding: 28px 32px;
  max-width: 1440px;
  margin: 0 auto;
}}

/* ── KPIs ── */
.kpi-row {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 28px;
}}
.kpi {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 18px;
  position: relative;
  overflow: hidden;
}}
.kpi::before {{
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
  background: var(--accent);
}}
.kpi-label {{
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--muted);
  margin-bottom: 6px;
}}
.kpi-value {{
  font-family: var(--font-head);
  font-size: 28px;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
}}
.kpi-sub {{
  font-size: 10px;
  color: var(--muted);
  margin-top: 4px;
}}

/* ── SEÇÕES ── */
.section-title {{
  font-family: var(--font-head);
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--muted);
  margin: 0 0 14px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}}

/* ── GRID DE CARDS ── */
.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 22px; }}
.grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; margin-bottom: 22px; }}
.grid-1-2 {{ display: grid; grid-template-columns: 1fr 2fr; gap: 18px; margin-bottom: 22px; }}
.grid-2-1 {{ display: grid; grid-template-columns: 2fr 1fr; gap: 18px; margin-bottom: 22px; }}
@media (max-width: 900px) {{
  .grid-2, .grid-3, .grid-1-2, .grid-2-1 {{ grid-template-columns: 1fr; }}
}}

.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px 20px;
}}
.card-title {{
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--accent2);
  margin-bottom: 14px;
  font-weight: 600;
}}

/* ── CHART CONTAINERS ── */
.chart-wrap {{ position: relative; height: 220px; }}
.chart-wrap-tall {{ position: relative; height: 300px; }}

/* ── TABELA ── */
.data-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}}
.data-table thead th {{
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--muted);
  padding: 6px 10px;
  text-align: left;
  border-bottom: 1px solid var(--border);
  font-weight: 600;
}}
.data-table tbody tr {{ border-bottom: 1px solid var(--border); transition: background .12s; }}
.data-table tbody tr:hover {{ background: rgba(255,255,255,.03); }}
.data-table tbody td {{ padding: 7px 10px; }}
.badge {{
  display: inline-block;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}}
.hub-badge {{ background: rgba(241,196,15,.18); color: var(--accent); border: 1px solid rgba(241,196,15,.3); }}
.rota-badge {{ background: rgba(126,200,227,.12); color: var(--accent2); border: 1px solid rgba(126,200,227,.25); }}

/* ── SCATTER TOOLTIP ── */
#scatter-tip {{
  position: fixed;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 8px 12px;
  font-size: 11px;
  pointer-events: none;
  opacity: 0;
  transition: opacity .12s;
  z-index: 999;
  max-width: 180px;
  line-height: 1.6;
}}

/* ── EGO HEATMAP ── */
.ego-grid {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}}
.ego-cell {{
  border-radius: 7px;
  padding: 8px 6px;
  text-align: center;
  cursor: default;
  border: 1px solid transparent;
  transition: transform .15s, border-color .15s;
}}
.ego-cell:hover {{ transform: scale(1.05); border-color: var(--accent); }}
.ego-cell .ec-iata {{ font-weight: 600; font-size: 12px; color: #fff; }}
.ego-cell .ec-dens {{ font-size: 10px; color: rgba(255,255,255,.7); margin-top: 2px; }}

/* ── REGION BADGES ── */
.reg-list {{
  display: flex;
  flex-direction: column;
  gap: 10px;
}}
.reg-row {{
  display: grid;
  grid-template-columns: 100px 1fr 60px 60px 70px;
  align-items: center;
  gap: 8px;
  font-size: 11px;
}}
.reg-bar-bg {{
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}}
.reg-bar-fill {{
  height: 100%;
  border-radius: 4px;
  transition: width .6s cubic-bezier(.22,1,.36,1);
}}
.reg-name {{ font-weight: 600; font-size: 11px; }}
.reg-val {{ text-align: right; color: var(--muted); }}

/* ── ROTA TABLE ── */
.rota-row {{
  display: grid;
  grid-template-columns: 90px 90px 1fr 70px;
  gap: 8px;
  align-items: center;
  padding: 9px 0;
  border-bottom: 1px solid var(--border);
  font-size: 11px;
}}
.rota-row:last-child {{ border-bottom: none; }}
.rota-path {{
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}}
.rota-chip {{
  padding: 2px 7px;
  background: rgba(162,155,254,.15);
  border: 1px solid rgba(162,155,254,.25);
  border-radius: 4px;
  font-size: 10px;
  color: var(--accent3);
  font-weight: 600;
}}
.rota-arrow {{ color: var(--muted); font-size: 10px; }}
.custo-bar-bg {{
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}}
.custo-bar-fill {{
  height: 100%;
  background: linear-gradient(90deg, var(--accent2), var(--accent3));
  border-radius: 3px;
}}

/* ── TIPO CONEXÃO ── */
.tipo-row {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
  font-size: 11px;
}}
.tipo-row:last-child {{ border-bottom: none; }}
.tipo-dot {{ width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }}
.tipo-name {{ flex: 1; }}
.tipo-count {{ color: var(--accent); font-weight: 600; width: 28px; text-align: right; }}
.tipo-peso {{ color: var(--muted); width: 60px; text-align: right; }}

/* ── INSIGHT STRIP ── */
.insight-strip {{
  background: linear-gradient(135deg, rgba(241,196,15,.07), rgba(126,200,227,.05));
  border: 1px solid rgba(241,196,15,.2);
  border-radius: 10px;
  padding: 14px 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 22px;
}}
.insight-item {{ display: flex; align-items: flex-start; gap: 10px; }}
.insight-icon {{ font-size: 20px; flex-shrink: 0; line-height: 1; }}
.insight-text {{ font-size: 11px; line-height: 1.6; }}
.insight-text strong {{ color: var(--accent); display: block; font-size: 11px; margin-bottom: 2px; }}

/* ── FOOTER ── */
footer {{
  text-align: center;
  padding: 24px;
  font-size: 10px;
  color: var(--muted);
  border-top: 1px solid var(--border);
  margin-top: 32px;
}}
</style>
</head>
<body>

<header>
  <div class="header-left">
    <h1>✈ Rede de Aeroportos do Brasil</h1>
    <p>Dashboard Analítico — Teoria dos Grafos 2026.1</p>
  </div>
  <a class="header-btn" href="grafo_interativo.html">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"/><line x1="14.83" y1="9.17" x2="18.36" y2="5.64"/><line x1="4.93" y1="19.07" x2="9.17" y2="14.83"/></svg>
    Ver Grafo Interativo
  </a>
</header>

<div id="scatter-tip"></div>

<main>

  <!-- KPIs -->
  <div class="kpi-row" id="kpi-row"></div>

  <!-- Insights destacados -->
  <div class="insight-strip" id="insight-strip"></div>

  <!-- Seção 1: Distribuição e ranking -->
  <p class="section-title">Conectividade e Hierarquia</p>
  <div class="grid-2-1">
    <div class="card">
      <div class="card-title">Ranking de Aeroportos por Grau</div>
      <div class="chart-wrap-tall"><canvas id="chart-graus"></canvas></div>
    </div>
    <div class="card">
      <div class="card-title">Distribuição por Tipo de Conexão</div>
      <div class="chart-wrap" style="height:140px;"><canvas id="chart-tipo-donut"></canvas></div>
      <div style="margin-top:14px;" id="tipo-list"></div>
    </div>
  </div>

  <!-- Seção 2: Regiões -->
  <p class="section-title">Análise Regional</p>
  <div class="grid-1-2">
    <div class="card">
      <div class="card-title">Métricas por Região</div>
      <div id="reg-list" class="reg-list"></div>
    </div>
    <div class="card">
      <div class="card-title">Densidade por Região</div>
      <div class="chart-wrap"><canvas id="chart-regioes"></canvas></div>
    </div>
  </div>

  <!-- Seção 3: Caminhos mínimos -->
  <p class="section-title">Caminhos Mínimos (Dijkstra)</p>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Rotas Calculadas</div>
      <div id="rota-list"></div>
    </div>
    <div class="card">
      <div class="card-title">Custo vs Escalas</div>
      <div class="chart-wrap"><canvas id="chart-rotas"></canvas></div>
    </div>
  </div>

  <!-- Seção 4: Ego-networks -->
  <p class="section-title">Ego-Networks</p>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">Densidade da Ego-Network (heatmap)</div>
      <div id="ego-grid" class="ego-grid"></div>
    </div>
    <div class="card">
      <div class="card-title">Hubs vs Aeroportos Comuns — Grau Médio</div>
      <div class="chart-wrap"><canvas id="chart-hubs"></canvas></div>
    </div>
  </div>

  <!-- Tabela completa -->
  <p class="section-title">Tabela Completa de Aeroportos</p>
  <div class="card" style="margin-bottom:22px;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
      <span class="card-title" style="margin:0;">Todos os Aeroportos</span>
      <input id="search-table" placeholder="Filtrar por IATA ou cidade..."
        style="background:var(--surface);border:1px solid var(--border);border-radius:6px;
               padding:5px 10px;color:var(--text);font-family:var(--font-mono);font-size:11px;width:220px;">
    </div>
    <table class="data-table" id="airport-table">
      <thead>
        <tr>
          <th>IATA</th><th>Cidade</th><th>Região</th><th>Grau</th>
          <th>Tipo</th><th>Ego-Dens.</th><th>Ord. Ego</th>
        </tr>
      </thead>
      <tbody id="airport-tbody"></tbody>
    </table>
  </div>

</main>

<footer>
  Projeto Teoria dos Grafos 2026.1 · CESAR School · Dados: aeroportos_data.csv, adjacencias_aeroportos.csv, rotas.csv
</footer>

<script>
{js_data}

Chart.defaults.color = '#64748b';
Chart.defaults.borderColor = '#252636';
Chart.defaults.font.family = "'IBM Plex Mono', monospace";
Chart.defaults.font.size   = 11;

const TIPO_COLORS = {{
  regional:      '#27ae60',
  interregional: '#e67e22',
}};

function regiaoColor(nome) {{
  return REGIAO_CORES[nome] || '#7ec8e3';
}}

function buildKPIs() {{
  const maxGrau = GRAUS[0];
  const minRota = DISTANCIAS[DISTANCIAS.length-1];
  const maxRota = DISTANCIAS[0];

  const kpis = [
    {{ label:'Aeroportos',      value: GLOBAL.ordem,                          sub:'nós do grafo' }},
    {{ label:'Conexões',        value: GLOBAL.tamanho,                        sub:'arestas (não-dir.)' }},
    {{ label:'Densidade Global',value: (GLOBAL.densidade*100).toFixed(1)+'%', sub:'do grafo completo' }},
    {{ label:'Grau Médio',      value: GRAU_MEDIO.toFixed(2),                 sub:'conexões por aeroporto' }},
    {{ label:'Maior Hub',       value: maxGrau.aeroporto,                     sub:`grau ${{maxGrau.grau}}` }},
    {{ label:'Rota Mais Curta', value: minRota.custo,                         sub:`${{minRota.origem}} → ${{minRota.destino}}` }},
    {{ label:'Rota Mais Longa', value: maxRota.custo,                         sub:`${{maxRota.origem}} → ${{maxRota.destino}}` }},
    {{ label:'Regiões',         value: REGIOES.length,                        sub:'cobertas' }},
  ];

  const row = document.getElementById('kpi-row');
  kpis.forEach(k => {{
    row.innerHTML += `<div class="kpi">
      <div class="kpi-label">${{k.label}}</div>
      <div class="kpi-value">${{k.value}}</div>
      <div class="kpi-sub">${{k.sub}}</div>
    </div>`;
  }});
}}

function buildInsights() {{
  const densMax = [...REGIOES].sort((a,b)=>b.densidade-a.densidade)[0];
  const hubsText = HUBS_SET.join(', ');
  const belCgh = DISTANCIAS.find(d => d.origem==='BEL' && d.destino==='CGH') || DISTANCIAS[0];

  const items = [
    {{ icon:'🏆', title:'Hub dominante', text:`GRU lidera com grau ${{GRAUS[0].grau}}, conectando ${{GRAUS[0].grau}} aeroportos diretamente — mais que qualquer outro nó da rede.` }},
    {{ icon:'🗺️', title:`Região mais densa`, text:`${{densMax.regiao}} tem densidade ${{densMax.densidade.toFixed(2)}} — todos os seus aeroportos são mutuamente alcançáveis com poucas arestas.` }},
    {{ icon:'✂️', title:'Rota direta mais barata', text:`REC → POA tem custo 1.5, pois os dois hubs regionais estão conectados diretamente (Hub↔Hub inter-regional).` }},
    {{ icon:'🔗', title:'Rota mais cara', text:`${{belCgh.origem}} → ${{belCgh.destino}} custa ${{belCgh.custo}} passando por ${{belCgh.caminho.split(' -> ').length-2}} escalas: ${{belCgh.caminho}}.` }},
    {{ icon:'⭐', title:'Hubs regionais', text:`Os 5 hubs (${{hubsText}}) concentram a maioria das conexões inter-regionais e reduzem o custo médio das rotas.` }},
  ];

  const strip = document.getElementById('insight-strip');
  items.forEach(i => {{
    strip.innerHTML += `<div class="insight-item">
      <div class="insight-icon">${{i.icon}}</div>
      <div class="insight-text"><strong>${{i.title}}</strong>${{i.text}}</div>
    </div>`;
  }});
}}

function buildGrausChart() {{
  const labels = GRAUS.map(r => r.aeroporto);
  const values = GRAUS.map(r => parseInt(r.grau));
  const colors = GRAUS.map(r => HUBS_SET.includes(r.aeroporto) ? '#f1c40f' : '#7ec8e3');

  new Chart(document.getElementById('chart-graus'), {{
    type: 'bar',
    data: {{
      labels,
      datasets: [{{
        label: 'Grau',
        data: values,
        backgroundColor: colors,
        borderRadius: 4,
        borderSkipped: false,
      }}]
    }},
    options: {{
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            label: ctx => {{
              const iata = labels[ctx.dataIndex];
              const info = IATA_INFO[iata];
              const hub = HUBS_SET.includes(iata) ? ' [HUB]' : '';
              return ` Grau ${{ctx.parsed.x}} — ${{info ? info.cidade : ''}}${{hub}}`;
            }}
          }}
        }}
      }},
      scales: {{
        x: {{ grid: {{ color:'#252636' }}, ticks: {{ stepSize:1 }} }},
        y: {{ grid: {{ display: false }} }},
      }}
    }}
  }});
}}

function buildTipoDonut() {{
  const labels = Object.keys(TIPO_COUNT);
  const values = Object.values(TIPO_COUNT);
  const colors = labels.map(l => TIPO_COLORS[l] || '#a29bfe');

  new Chart(document.getElementById('chart-tipo-donut'), {{
    type: 'doughnut',
    data: {{
      labels,
      datasets: [{{ data: values, backgroundColor: colors, borderWidth: 0, hoverOffset: 6 }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ position: 'right', labels: {{ boxWidth:10, padding:10, font:{{ size:10 }} }} }}
      }},
      cutout: '62%',
    }}
  }});

  // lista tipo
  const list = document.getElementById('tipo-list');
  labels.forEach((l,i) => {{
    const avg = TIPO_PESO[l] !== undefined ? TIPO_PESO[l].toFixed(2) : '-';
    list.innerHTML += `<div class="tipo-row">
      <span class="tipo-dot" style="background:${{colors[i]}};"></span>
      <span class="tipo-name">${{l}}</span>
      <span class="tipo-count">${{values[i]}}</span>
      <span class="tipo-peso">ø ${{avg}}</span>
    </div>`;
  }});
}}

function buildRegioes() {{
  const maxOrdem = Math.max(...REGIOES.map(r=>r.ordem));

  const list = document.getElementById('reg-list');
  REGIOES.forEach(r => {{
    const cor = regiaoColor(r.regiao);
    const pct = (r.ordem / maxOrdem * 100).toFixed(0);
    list.innerHTML += `<div class="reg-row">
      <span class="reg-name" style="color:${{cor}}">${{r.regiao}}</span>
      <div class="reg-bar-bg"><div class="reg-bar-fill" style="width:${{pct}}%;background:${{cor}};"></div></div>
      <span class="reg-val">${{r.ordem}} nós</span>
      <span class="reg-val">${{r.tamanho}} ar.</span>
      <span class="reg-val" style="color:${{cor}}">${{r.densidade.toFixed(2)}}</span>
    </div>`;
  }});

  new Chart(document.getElementById('chart-regioes'), {{
    type: 'bar',
    data: {{
      labels: REGIOES.map(r=>r.regiao),
      datasets: [
        {{
          label: 'Densidade',
          data: REGIOES.map(r=>r.densidade),
          backgroundColor: REGIOES.map(r=>regiaoColor(r.regiao)),
          borderRadius: 5,
          borderSkipped: false,
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display:false }} }},
      scales: {{
        y: {{ min:0, max:1.1, grid:{{ color:'#252636' }}, ticks:{{ callback: v => v.toFixed(1) }} }},
        x: {{ grid:{{ display:false }} }}
      }}
    }}
  }});
}}

function buildRotas() {{
  const maxCusto = Math.max(...DISTANCIAS.map(d=>parseFloat(d.custo)));
  const list = document.getElementById('rota-list');

  DISTANCIAS.forEach(d => {{
    const chips = d.caminho.split(' -> ')
      .map((c,i,arr) => i<arr.length-1
        ? `<span class="rota-chip">${{c}}</span><span class="rota-arrow">→</span>`
        : `<span class="rota-chip">${{c}}</span>`)
      .join('');
    const pct = (parseFloat(d.custo)/maxCusto*100).toFixed(0);
    list.innerHTML += `<div class="rota-row">
      <span class="badge rota-badge">${{d.origem}}</span>
      <span class="badge rota-badge">${{d.destino}}</span>
      <div class="rota-path">${{chips}}</div>
      <div>
        <div style="font-size:10px;color:var(--accent);text-align:right;margin-bottom:2px;">⚖ ${{d.custo}}</div>
        <div class="custo-bar-bg"><div class="custo-bar-fill" style="width:${{pct}}%;"></div></div>
      </div>
    </div>`;
  }});

  // Scatter: custo vs escalas
  const pts = DISTANCIAS.map(d => {{
    const steps = d.caminho.split(' -> ').length - 2;
    return {{ x: steps, y: parseFloat(d.custo), label: `${{d.origem}}→${{d.destino}}` }};
  }});

  new Chart(document.getElementById('chart-rotas'), {{
    type: 'scatter',
    data: {{
      datasets: [{{
        label: 'Rotas',
        data: pts.map(p => ({{ x:p.x, y:p.y, label:p.label }})),
        backgroundColor: '#a29bfe',
        pointRadius: 8,
        pointHoverRadius: 11,
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{
        legend: {{ display:false }},
        tooltip: {{ callbacks: {{ label: ctx => `${{ctx.raw.label}}: custo ${{ctx.raw.y}}, ${{ctx.raw.x}} escala(s)` }} }}
      }},
      scales: {{
        x: {{ title:{{ display:true, text:'Escalas', color:'#64748b' }}, grid:{{ color:'#252636' }}, ticks:{{stepSize:1}} }},
        y: {{ title:{{ display:true, text:'Custo', color:'#64748b' }}, grid:{{ color:'#252636' }} }},
      }}
    }}
  }});
}}

function buildEgo() {{
  const grid = document.getElementById('ego-grid');
  const maxDens = Math.max(...EGO.map(e=>parseFloat(e.densidade_ego)));

  EGO.forEach(e => {{
    const dens = parseFloat(e.densidade_ego);
    const reg  = e.regiao;
    const cor  = regiaoColor(reg);
    const alpha = 0.15 + dens * 0.65;
    const bg = cor + Math.round(alpha*255).toString(16).padStart(2,'0');
    grid.innerHTML += `<div class="ego-cell" style="background:${{bg}};" title="${{e.cidade}} (${{reg}}) — dens ${{dens.toFixed(2)}}">
      <div class="ec-iata">${{e.aeroporto}}</div>
      <div class="ec-dens">${{dens.toFixed(2)}}</div>
    </div>`;
  }});
}}

function buildHubsChart() {{
  const hubGraus   = HUBS_GRAU.map(h=>h.grau);
  const otherGraus = OTHERS_GRAU.map(h=>h.grau);
  const avgHub   = hubGraus.reduce((a,b)=>a+b,0) / hubGraus.length;
  const avgOther = otherGraus.reduce((a,b)=>a+b,0) / otherGraus.length;

  new Chart(document.getElementById('chart-hubs'), {{
    type: 'bar',
    data: {{
      labels: ['Hubs Regionais', 'Aeroportos Comuns'],
      datasets: [
        {{
          label: 'Grau Médio',
          data: [avgHub.toFixed(2), avgOther.toFixed(2)],
          backgroundColor: ['#f1c40f', '#7ec8e3'],
          borderRadius: 6,
          borderSkipped: false,
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend:{{ display:false }} }},
      scales: {{
        y: {{ grid:{{ color:'#252636' }}, beginAtZero:true }},
        x: {{ grid:{{ display:false }} }}
      }}
    }}
  }});
}}
function buildTable() {{
  const tbody = document.getElementById('airport-tbody');
  const rows  = [];

  Object.keys(IATA_INFO).forEach(iata => {{
    const info = IATA_INFO[iata];
    const e    = EGO.find(r => r.aeroporto === iata) || {{}};
    const hub  = HUBS_SET.includes(iata);
    rows.push({{ iata, info, e, hub }});
  }});

  rows.sort((a,b) => (parseInt(b.e.grau)||0) - (parseInt(a.e.grau)||0));

  function render(filter) {{
    tbody.innerHTML = '';
    rows.filter(r =>
      !filter ||
      r.iata.toLowerCase().includes(filter) ||
      r.info.cidade.toLowerCase().includes(filter)
    ).forEach(r => {{
      const cor = regiaoColor(r.info.regiao);
      tbody.innerHTML += `<tr>
        <td><b style="color:var(--accent2);">${{r.iata}}</b></td>
        <td>${{r.info.cidade}}</td>
        <td><span style="color:${{cor}};font-weight:600;">${{r.info.regiao}}</span></td>
        <td style="color:var(--accent);">${{r.e.grau || '-'}}</td>
        <td>${{r.hub ? '<span class="badge hub-badge">Hub</span>' : '<span style="color:var(--muted);">comum</span>'}}</td>
        <td>${{r.e.densidade_ego ? parseFloat(r.e.densidade_ego).toFixed(3) : '-'}}</td>
        <td>${{r.e.ordem_ego || '-'}}</td>
      </tr>`;
    }});
  }}

  render('');

  document.getElementById('search-table').addEventListener('input', e => {{
    render(e.target.value.toLowerCase().trim());
  }});
}}

buildKPIs();
buildInsights();
buildGrausChart();
buildTipoDonut();
buildRegioes();
buildRotas();
buildEgo();
buildHubsChart();
buildTable();
</script>
</body>
</html>
"""
    return html


def generate_dashboard(
    data_dir: Path = DATA_DIR,
    out_dir:  Path = OUT_DIR,
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

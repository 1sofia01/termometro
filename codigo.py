import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
import os

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Termômetro de Saúde Pública na Mídia",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilo CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0f1117; color: #e8eaf6; }
    [data-testid="stSidebar"] { background-color: #161b2e; border-right: 1px solid #1e2a4a; }
    .block-container { padding-top: 2rem; }

    .metric-card {
        background: linear-gradient(135deg, #1a2340 0%, #1e2d52 100%);
        border: 1px solid #2a3a6a;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 12px;
    }
    .metric-card .label {
        font-size: 0.78rem; color: #8892b0;
        text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;
    }
    .metric-card .value { font-size: 2.2rem; font-weight: 700; color: #64b5f6; line-height: 1; }
    .metric-card .sub  { font-size: 0.82rem; color: #90a4ae; margin-top: 4px; }

    .main-title { font-size: clamp(1.1rem, 3vw, 1.9rem); ... }
    .main-subtitle { font-size: 0.95rem; color: #8892b0; margin-bottom: 1.5rem; }

    .section-title {
        font-size: 1.1rem; font-weight: 600; color: #cfd8dc;
        border-left: 3px solid #64b5f6;
        padding-left: 10px; margin: 1.5rem 0 0.8rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Chave API (via Streamlit Secrets) ───────────────────────────────────────
API_KEY = st.secrets["NEWSAPI_KEY"]

# ── Cache local ─────────────────────────────────────────────────────────────
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# ── Funções de dados ─────────────────────────────────────────────────────────

def buscar_noticias(keyword: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Busca notícias reais na NewsAPI com cache local de 24h."""

    cache_key = f"{keyword.lower()}_{start_date.date()}_{end_date.date()}"
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

    # Usar cache se existir e tiver menos de 24h
    if os.path.exists(cache_file):
        idade = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))).total_seconds()
        if idade < 86400:
            with open(cache_file, "r", encoding="utf-8") as f:
                return processar_json(json.load(f))

    params = {
        "q": keyword,
        "from": start_date.strftime("%Y-%m-%d"),
        "to":   end_date.strftime("%Y-%m-%d"),
        "language": "pt",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": API_KEY,
    }

    try:
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json()

        # Salvar cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False)

        return processar_json(raw)

    except requests.exceptions.HTTPError as e:
        st.error(f"Erro na NewsAPI: {e}")
        st.stop()
    except requests.exceptions.ConnectionError:
        st.error("Sem conexão com a internet. Verifique sua rede.")
        st.stop()
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        st.stop()


def processar_json(raw: dict) -> pd.DataFrame:
    """Converte JSON da NewsAPI em DataFrame limpo."""
    articles = raw.get("articles", [])
    records = []

    for a in articles:
        titulo = a.get("title", "") or ""
        # Ignorar artigos removidos ou sem título
        if not titulo or titulo == "[Removed]":
            continue

        source = a.get("source", {}).get("name", "Desconhecido")
        published_raw = a.get("publishedAt", "")

        records.append({
            "titulo":    titulo.strip(),
            "data":      published_raw[:10],
            "data_hora": published_raw[:16].replace("T", " "),
            "veiculo":   source.strip(),
            "url":       a.get("url", ""),
        })

    if not records:
        return pd.DataFrame(columns=["titulo", "data", "data_hora", "veiculo", "url"])

    df = pd.DataFrame(records)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"]).reset_index(drop=True)
    df = df.sort_values("data_hora").reset_index(drop=True)
    return df


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🩺 Termômetro de Saúde")
    st.markdown("<hr style='border-color:#2a3a6a; margin: 0.5rem 0 1rem'>", unsafe_allow_html=True)

    st.markdown("**🔍 Palavra-chave**")
    keyword = st.text_input("", value="vacina", label_visibility="collapsed",
                            placeholder="Ex: dengue, câncer, SUS…")

    st.markdown("**📅 Período**")
    # NewsAPI gratuita permite no máximo 30 dias no passado
    col_a, col_b = st.columns(2)
    with col_a:
        start_date = st.date_input("De", value=datetime.today() - timedelta(days=29),
                                   label_visibility="collapsed")
    with col_b:
        end_date = st.date_input("Até", value=datetime.today(),
                                 label_visibility="collapsed")

    if start_date > end_date:
        st.error("Data inicial maior que a final.")
        st.stop()

    # Limite do plano gratuito da NewsAPI: últimos 30 dias
    limite = datetime.today().date() - timedelta(days=30)
    if start_date < limite:
        st.warning("⚠️ O plano gratuito da NewsAPI cobre apenas os últimos 30 dias.")

    buscar = st.button("🔎 Buscar notícias", use_container_width=True, type="primary")

    st.markdown("<hr style='border-color:#2a3a6a; margin: 1rem 0'>", unsafe_allow_html=True)

    veiculo_selecionado = None  # será preenchido após a busca


# ── Estado de sessão ─────────────────────────────────────────────────────────

if "df" not in st.session_state:
    st.session_state.df = None
if "last_keyword" not in st.session_state:
    st.session_state.last_keyword = ""

# ── Área principal ────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">🩺 Termômetro de Saúde Pública na Mídia</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Monitore como a imprensa brasileira cobre temas de saúde pública</p>', unsafe_allow_html=True)

if buscar or st.session_state.df is None:
    if not keyword.strip():
        st.warning("Digite uma palavra-chave para buscar.")
        st.stop()

    with st.spinner(f"Buscando notícias sobre **{keyword}**…"):
        df_raw = buscar_noticias(
            keyword,
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date,   datetime.max.time()),
        )
        st.session_state.df = df_raw
        st.session_state.last_keyword = keyword

df = st.session_state.df

if df is None or df.empty:
    st.info("Nenhuma notícia encontrada para essa palavra-chave no período selecionado.")
    st.stop()

# ── Selectbox de veículo (após carregar dados) ────────────────────────────────

veiculos_disponiveis = ["Todos os Veículos"] + sorted(df["veiculo"].unique().tolist())

with st.sidebar:
    st.markdown("**📰 Veículo de imprensa**")
    veiculo_selecionado = st.selectbox("", veiculos_disponiveis, label_visibility="collapsed")

# ── Filtro ────────────────────────────────────────────────────────────────────

if veiculo_selecionado and veiculo_selecionado != "Todos os Veículos":
    df_view = df[df["veiculo"] == veiculo_selecionado].copy()
    modo = "individual"
else:
    df_view = df.copy()
    modo = "geral"

# ── MODO GERAL ────────────────────────────────────────────────────────────────

if modo == "geral":
    st.markdown(f'<p class="section-title">📊 Visão Geral — <em>{st.session_state.last_keyword}</em></p>',
                unsafe_allow_html=True)

    total      = len(df_view)
    n_veiculos = df_view["veiculo"].nunique()
    dias_ativ  = df_view["data"].nunique()
    media_dia  = round(total / max(dias_ativ, 1), 1)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, sub in zip(
        [c1, c2, c3, c4],
        [total, n_veiculos, dias_ativ, media_dia],
        ["Total de Notícias", "Veículos Ativos", "Dias com Publicações", "Média por Dia"],
        ["artigos encontrados", "fontes monitoradas", "no período", "artigos/dia"],
    ):
        col.markdown(f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{val}</div>
            <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    # Gráfico de área — volume por dia
    st.markdown('<p class="section-title">📈 Volume de Publicações por Dia</p>', unsafe_allow_html=True)
    ts = df_view.groupby("data").size().reset_index(name="qtd")
    fig_line = px.area(ts, x="data", y="qtd",
                       color_discrete_sequence=["#64b5f6"],
                       labels={"data": "Data", "qtd": "Notícias"},
                       template="plotly_dark")
    fig_line.update_traces(fillcolor="rgba(100,181,246,0.12)", line_width=2)
    fig_line.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           margin=dict(t=10, b=10, l=10, r=10),
                           xaxis=dict(gridcolor="#1e2a4a"),
                           yaxis=dict(gridcolor="#1e2a4a"))
    st.plotly_chart(fig_line, use_container_width=True)

    # Gráfico de barras — ranking de veículos
    st.markdown('<p class="section-title">🏆 Ranking de Veículos</p>', unsafe_allow_html=True)
    top = (df_view.groupby("veiculo").size()
           .reset_index(name="qtd")
           .sort_values("qtd", ascending=True)
           .tail(15))
    fig_bar = px.bar(top, x="qtd", y="veiculo", orientation="h",
                     color="qtd",
                     color_continuous_scale=["#1a3a6a", "#2196f3", "#64b5f6"],
                     labels={"qtd": "Notícias", "veiculo": "Veículo"},
                     template="plotly_dark")
    fig_bar.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                          margin=dict(t=10, b=10, l=10, r=10),
                          coloraxis_showscale=False,
                          yaxis=dict(gridcolor="#1e2a4a"),
                          xaxis=dict(gridcolor="#1e2a4a"))
    st.plotly_chart(fig_bar, use_container_width=True)


# ── MODO INDIVIDUAL ───────────────────────────────────────────────────────────

else:
    st.markdown(f'<p class="section-title">📰 {veiculo_selecionado} — <em>{st.session_state.last_keyword}</em></p>',
                unsafe_allow_html=True)

    total_v = len(df_view)
    dias_v  = df_view["data"].nunique()
    media_v = round(total_v / max(dias_v, 1), 1)
    pico_row  = df_view.groupby("data").size()
    pico_data = pico_row.idxmax().strftime("%d/%m") if not pico_row.empty else "—"
    pico_val  = int(pico_row.max()) if not pico_row.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, sub in zip(
        [c1, c2, c3, c4],
        [total_v, dias_v, media_v, f"{pico_val} ({pico_data})"],
        ["Total de Artigos", "Dias com Publicação", "Média Diária", "Pico de Publicações"],
        [veiculo_selecionado, "no período", "artigos/dia", "artigos no dia pico"],
    ):
        col.markdown(f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{val}</div>
            <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    # Gráfico de linhas individual
    st.markdown('<p class="section-title">📈 Comportamento ao Longo do Período</p>', unsafe_allow_html=True)
    ts_v = df_view.groupby("data").size().reset_index(name="qtd")
    fig_v = px.line(ts_v, x="data", y="qtd", markers=True,
                    color_discrete_sequence=["#81c784"],
                    labels={"data": "Data", "qtd": "Notícias"},
                    template="plotly_dark")
    fig_v.update_traces(line_width=2.5, marker_size=6)
    fig_v.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                        margin=dict(t=10, b=10, l=10, r=10),
                        xaxis=dict(gridcolor="#1e2a4a"),
                        yaxis=dict(gridcolor="#1e2a4a"))
    st.plotly_chart(fig_v, use_container_width=True)

    # Tabela de manchetes
    st.markdown('<p class="section-title">📋 Manchetes Publicadas</p>', unsafe_allow_html=True)
    tabela = df_view[["data", "titulo", "url"]].copy()
    tabela["data"] = tabela["data"].dt.strftime("%d/%m/%Y")
    tabela.columns = ["Data", "Manchete", "Link"]
    tabela = tabela.reset_index(drop=True)

    st.dataframe(
        tabela,
        use_container_width=True,
        column_config={
            "Data":     st.column_config.TextColumn("📅 Data",     width="small"),
            "Manchete": st.column_config.TextColumn("📰 Manchete", width="large"),
            "Link":     st.column_config.LinkColumn("🔗 Link",     width="small"),
        },
        hide_index=True,
        height=min(400, 35 * len(tabela) + 50),
    )

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<hr style='border-color:#1e2a4a'>"
    "<p style='text-align:center; color:#4a5568; font-size:0.78rem'>"
    "🩺 Termômetro de Saúde Pública na Mídia · Python + Streamlit + NewsAPI · Projeto A2"
    "</p>",
    unsafe_allow_html=True,
)

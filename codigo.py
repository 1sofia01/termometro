# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Termômetro de Saúde Pública na Mídia",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilo CSS customizado ──────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fundo e tipografia */
    [data-testid="stAppViewContainer"] {
        background-color: #0f1117;
        color: #e8eaf6;
    }
    [data-testid="stSidebar"] {
        background-color: #161b2e;
        border-right: 1px solid #1e2a4a;
    }
    .block-container {
        padding-top: 2rem;
    }

    /* Cards de métrica */
    .metric-card {
        background: linear-gradient(135deg, #1a2340 0%, #1e2d52 100%);
        border: 1px solid #2a3a6a;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 12px;
    }
    .metric-card .label {
        font-size: 0.78rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .metric-card .value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #64b5f6;
        line-height: 1;
    }
    .metric-card .sub {
        font-size: 0.82rem;
        color: #90a4ae;
        margin-top: 4px;
    }

    /* Título principal */
    .main-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #e8eaf6;
        margin-bottom: 0.2rem;
    }
    .main-subtitle {
        font-size: 0.95rem;
        color: #8892b0;
        margin-bottom: 1.5rem;
    }

    /* Badge de veículo */
    .source-badge {
        display: inline-block;
        background: #1e3a5f;
        color: #64b5f6;
        border: 1px solid #2a5a8f;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        margin: 2px;
    }

    /* Aviso de demo */
    .demo-banner {
        background: linear-gradient(90deg, #1a3a1a, #1e4a1e);
        border: 1px solid #2a6a2a;
        border-radius: 8px;
        padding: 10px 16px;
        color: #81c784;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }

    /* Seção de título */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #cfd8dc;
        border-left: 3px solid #64b5f6;
        padding-left: 10px;
        margin: 1.5rem 0 0.8rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Funções de dados ────────────────────────────────────────────────────────

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

DEMO_SOURCES = [
    "G1", "Folha de S.Paulo", "Estadão", "UOL", "CNN Brasil",
    "The Intercept Brasil", "Agência Brasil", "Veja Saúde"
]

DEMO_HEADLINES = {
    "vacina": [
        "Ministério da Saúde amplia campanha de vacinação contra gripe",
        "Nova vacina contra dengue chega ao SUS em 2025",
        "Cobertura vacinal cai 8% no Brasil, alerta Fiocruz",
        "Vacina contra COVID-19 bivalente disponível em todo o país",
        "Cientistas brasileiros desenvolvem vacina contra leishmaniose",
        "Calendário vacinal infantil ganha novo imunizante",
        "OMS recomenda vacinação em massa após surto de sarampo",
        "Vacinação contra HPV bate recorde em adolescentes",
        "Nova vacina contra tuberculose entra em fase 3 no Brasil",
        "Campanha de vacinação chega a aldeias indígenas remotas",
    ],
    "covid": [
        "Subvariante XEC do COVID-19 cresce no Brasil",
        "Pesquisa aponta sequelas cognitivas em pacientes pós-COVID",
        "Hospitalizações por COVID sobem 15% na região Sul",
        "Novo antiviral contra COVID aprovado pela Anvisa",
        "Estudo revela proteção de vacinas contra variante atual",
        "COVID longa afeta 20 milhões de brasileiros, diz pesquisa",
        "Ministério recomenda uso de máscara em unidades de saúde",
        "Variante JN.1 em monitoramento pela Fiocruz",
    ],
    "dengue": [
        "Brasil registra recorde histórico de casos de dengue em 2025",
        "Vacina contra dengue do Butantan recebe aprovação da Anvisa",
        "SP declara emergência por dengue em 120 municípios",
        "Mutirão de eliminação de focos do Aedes aegypti mobiliza cidades",
        "Dengue grave: UTIs pediátricas lotadas no Centro-Oeste",
        "Nova armadilha biológica reduz mosquitos em 70% em testes",
        "Chikungunya avança junto com dengue na mesma temporada",
    ],
    "nutrição": [
        "Ultra-processados causam 57 mil mortes prematuras por ano no Brasil",
        "Nova pirâmide alimentar brasileira será lançada em 2025",
        "Programa de alimentação escolar ganha reforço de R$ 2 bilhões",
        "Estudo liga dieta mediterrânea à redução de demência",
        "Açúcar adicionado em bebidas infantis supera limite recomendado",
        "Rotulagem nutricional frontal aumenta escolhas saudáveis",
        "Desnutrição infantil cresce em bolsões de pobreza, alerta Unicef",
    ],
    "saúde mental": [
        "Burnout afeta 30% dos trabalhadores brasileiros, aponta pesquisa",
        "SUS amplia cobertura de saúde mental com novos CAPS",
        "Adolescentes: uso de redes sociais ligado a ansiedade, diz estudo",
        "Suicídio de jovens cresce 40% em cinco anos no Brasil",
        "Meditação reduz sintomas de depressão em ensaio clínico brasileiro",
        "Governo lança plano nacional de saúde mental pós-pandemia",
    ],
    "câncer": [
        "INCA projeta 704 mil novos casos de câncer por ano até 2025",
        "Novo medicamento para câncer de mama aprovado pela Anvisa",
        "Detecção precoce de câncer de pele cresce com IA dermatológica",
        "Quimioterapia oral reduz internações em pacientes oncológicos",
        "Tabagismo ainda é principal causa de câncer de pulmão no Brasil",
    ],
    "diabetes": [
        "Brasil tem 16 milhões de diabéticos; metade sem diagnóstico",
        "Novo sensor contínuo de glicose chega ao SUS",
        "Obesidade infantil eleva risco de diabetes tipo 2 em adultos jovens",
        "Medicamento para diabetes reduz risco cardiovascular em 20%",
        "Exercício físico regular controla glicemia tão bem quanto remédio",
    ],
}

def gerar_dados_demo(keyword: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Gera dados realistas simulados quando a API não está disponível."""
    import random, hashlib

    seed = int(hashlib.md5(keyword.lower().encode()).hexdigest(), 16) % (10**8)
    random.seed(seed)

    kw_lower = keyword.lower()
    headlines_pool = []
    for key, titles in DEMO_HEADLINES.items():
        if key in kw_lower or kw_lower in key:
            headlines_pool.extend(titles)
    if not headlines_pool:
        headlines_pool = [
            f"Nova descoberta sobre {keyword} é publicada em revista científica",
            f"Ministério da Saúde emite nota sobre {keyword}",
            f"Pesquisa revela dados preocupantes sobre {keyword} no Brasil",
            f"Especialistas debatem impacto de {keyword} na saúde pública",
            f"SUS incorpora novo protocolo relacionado a {keyword}",
            f"Estudo brasileiro sobre {keyword} é destaque internacional",
            f"Campanha de conscientização sobre {keyword} é lançada",
        ]

    delta_days = (end_date - start_date).days + 1
    records = []

    for i in range(delta_days):
        date = start_date + timedelta(days=i)
        # Padrão semanal: menos notícias nos fins de semana
        weekday_weight = 0.4 if date.weekday() >= 5 else 1.0
        n_articles = max(0, int(random.gauss(12, 5) * weekday_weight))

        for _ in range(n_articles):
            source = random.choice(DEMO_SOURCES)
            title = random.choice(headlines_pool)
            variation = random.randint(1, 999)
            full_title = f"{title} [{variation}]"
            published = date + timedelta(
                hours=random.randint(6, 22),
                minutes=random.randint(0, 59)
            )
            records.append({
                "titulo": full_title,
                "data": date.strftime("%Y-%m-%d"),
                "data_hora": published.strftime("%Y-%m-%d %H:%M"),
                "veiculo": source,
                "url": f"https://exemplo.com/{source.lower().replace(' ', '-')}/{variation}",
            })

    if not records:
        return pd.DataFrame(columns=["titulo", "data", "data_hora", "veiculo", "url"])

    df = pd.DataFrame(records)
    df["data"] = pd.to_datetime(df["data"])
    df = df.sort_values("data_hora").reset_index(drop=True)
    return df


def buscar_noticias_api(keyword: str, start_date: datetime, end_date: datetime, api_key: str) -> pd.DataFrame:
    """Busca notícias reais via NewsAPI."""
    cache_key = f"{keyword}_{start_date.date()}_{end_date.date()}"
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")

    # Verificar cache (24h)
    if os.path.exists(cache_file):
        modified = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if (datetime.now() - modified).total_seconds() < 86400:
            with open(cache_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return processar_json(raw)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": keyword,
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "language": "pt",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": api_key,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False)
        return processar_json(raw)
    except Exception as e:
        st.warning(f"Erro na API: {e}. Usando dados demo.")
        return gerar_dados_demo(keyword, start_date, end_date)


def processar_json(raw: dict) -> pd.DataFrame:
    """Converte JSON da NewsAPI para DataFrame limpo."""
    articles = raw.get("articles", [])
    records = []
    for a in articles:
        source_name = a.get("source", {}).get("name", "Desconhecido")
        published = a.get("publishedAt", "")[:10]
        records.append({
            "titulo": a.get("title", ""),
            "data": published,
            "data_hora": a.get("publishedAt", "")[:16].replace("T", " "),
            "veiculo": source_name,
            "url": a.get("url", ""),
        })

    if not records:
        return pd.DataFrame(columns=["titulo", "data", "data_hora", "veiculo", "url"])

    df = pd.DataFrame(records)
    df["data"] = pd.to_datetime(df["data"])
    df = df.dropna(subset=["titulo"]).reset_index(drop=True)
    return df


def carregar_dados(keyword: str, start_date: datetime, end_date: datetime, api_key: str) -> pd.DataFrame:
    if api_key and len(api_key) > 10:
        return buscar_noticias_api(keyword, start_date, end_date, api_key)
    return gerar_dados_demo(keyword, start_date, end_date)


# ── Layout: Sidebar ─────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🩺 Termômetro de Saúde")
    st.markdown("<hr style='border-color:#2a3a6a; margin: 0.5rem 0 1rem'>", unsafe_allow_html=True)

    api_key = st.text_input(
        "🔑 Chave NewsAPI (opcional)",
        type="password",
        placeholder="Cole sua chave aqui…",
        help="Sem chave, o app usa dados simulados realistas.",
    )

    st.markdown("**🔍 Palavra-chave**")
    keyword = st.text_input("", value="vacina", label_visibility="collapsed", placeholder="Ex: dengue, câncer…")

    st.markdown("**📅 Período**")
    col_a, col_b = st.columns(2)
    with col_a:
        start_date = st.date_input("De", value=datetime.today() - timedelta(days=30), label_visibility="collapsed")
    with col_b:
        end_date = st.date_input("Até", value=datetime.today(), label_visibility="collapsed")

    if start_date > end_date:
        st.error("Data inicial maior que a final.")
        st.stop()

    buscar = st.button("🔎 Buscar notícias", use_container_width=True, type="primary")

    st.markdown("<hr style='border-color:#2a3a6a; margin: 1rem 0'>", unsafe_allow_html=True)

    # O selectbox de veículo será preenchido após a busca
    veiculo_selecionado = None


# ── Estado de sessão ─────────────────────────────────────────────────────────

if "df" not in st.session_state:
    st.session_state.df = None
if "last_keyword" not in st.session_state:
    st.session_state.last_keyword = ""

# ── Área principal ───────────────────────────────────────────────────────────

st.markdown('<p class="main-title">🩺 Termômetro de Saúde Pública na Mídia</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Monitore como a imprensa brasileira cobre temas de saúde pública</p>', unsafe_allow_html=True)

if buscar or st.session_state.df is None:
    if not keyword.strip():
        st.warning("Digite uma palavra-chave para buscar.")
        st.stop()

    with st.spinner(f"Buscando notícias sobre **{keyword}**…"):
        df_raw = carregar_dados(keyword, datetime.combine(start_date, datetime.min.time()),
                                datetime.combine(end_date, datetime.max.time()), api_key)
        st.session_state.df = df_raw
        st.session_state.last_keyword = keyword

df = st.session_state.df

if df is None or df.empty:
    st.info("Nenhuma notícia encontrada. Tente outra palavra-chave ou período.")
    st.stop()

# Banner de modo demo
if not (api_key and len(api_key) > 10):
    st.markdown(
        '<div class="demo-banner">📊 <b>Modo demo:</b> dados simulados com padrões jornalísticos realistas. '
        'Para dados reais, insira sua chave <a href="https://newsapi.org" target="_blank" style="color:#81c784">NewsAPI</a> na barra lateral.</div>',
        unsafe_allow_html=True
    )

# ── Sidebar: Filtro de veículo (após carregar dados) ─────────────────────────
veiculos_disponiveis = ["Todos os Veículos"] + sorted(df["veiculo"].unique().tolist())

with st.sidebar:
    st.markdown("**📰 Veículo de imprensa**")
    veiculo_selecionado = st.selectbox("", veiculos_disponiveis, label_visibility="collapsed")


# ── Aplicar filtro de veículo ────────────────────────────────────────────────
if veiculo_selecionado and veiculo_selecionado != "Todos os Veículos":
    df_view = df[df["veiculo"] == veiculo_selecionado].copy()
    modo = "individual"
else:
    df_view = df.copy()
    modo = "geral"

# ── MODO GERAL ───────────────────────────────────────────────────────────────
if modo == "geral":
    st.markdown(f'<p class="section-title">📊 Visão Geral — <em>{st.session_state.last_keyword}</em></p>', unsafe_allow_html=True)

    total = len(df_view)
    n_veiculos = df_view["veiculo"].nunique()
    dias_ativos = df_view["data"].nunique()
    media_dia = round(total / max(dias_ativos, 1), 1)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, sub in zip(
        [c1, c2, c3, c4],
        [total, n_veiculos, dias_ativos, media_dia],
        ["Total de Notícias", "Veículos Ativos", "Dias com Publicações", "Média por Dia"],
        ["artigos encontrados", "fontes monitoradas", "no período", "artigos/dia"],
    ):
        col.markdown(f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{val}</div>
            <div class="sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    # Gráfico de linhas — volume por dia
    st.markdown('<p class="section-title">📈 Volume de Publicações por Dia</p>', unsafe_allow_html=True)
    ts = df_view.groupby("data").size().reset_index(name="qtd")
    fig_line = px.area(
        ts, x="data", y="qtd",
        color_discrete_sequence=["#64b5f6"],
        labels={"data": "Data", "qtd": "Notícias"},
        template="plotly_dark",
    )
    fig_line.update_traces(fillcolor="rgba(100,181,246,0.12)", line_width=2)
    fig_line.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(gridcolor="#1e2a4a", showgrid=True),
        yaxis=dict(gridcolor="#1e2a4a", showgrid=True),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Gráfico de barras — ranking de veículos
    st.markdown('<p class="section-title">🏆 Ranking de Veículos</p>', unsafe_allow_html=True)
    top = (
        df_view.groupby("veiculo").size()
        .reset_index(name="qtd")
        .sort_values("qtd", ascending=True)
        .tail(15)
    )
    fig_bar = px.bar(
        top, x="qtd", y="veiculo", orientation="h",
        color="qtd",
        color_continuous_scale=["#1a3a6a", "#2196f3", "#64b5f6"],
        labels={"qtd": "Notícias", "veiculo": "Veículo"},
        template="plotly_dark",
    )
    fig_bar.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="#1e2a4a"),
        xaxis=dict(gridcolor="#1e2a4a"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ── MODO INDIVIDUAL ──────────────────────────────────────────────────────────
else:
    st.markdown(f'<p class="section-title">📰 {veiculo_selecionado} — <em>{st.session_state.last_keyword}</em></p>', unsafe_allow_html=True)

    total_v = len(df_view)
    dias_v = df_view["data"].nunique()
    media_v = round(total_v / max(dias_v, 1), 1)
    pico_row = df_view.groupby("data").size()
    pico_data = pico_row.idxmax().strftime("%d/%m") if not pico_row.empty else "—"
    pico_val = int(pico_row.max()) if not pico_row.empty else 0

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
        </div>
        """, unsafe_allow_html=True)

    # Gráfico de linhas individual
    st.markdown('<p class="section-title">📈 Comportamento ao Longo do Período</p>', unsafe_allow_html=True)
    ts_v = df_view.groupby("data").size().reset_index(name="qtd")
    fig_v = px.line(
        ts_v, x="data", y="qtd",
        markers=True,
        color_discrete_sequence=["#81c784"],
        labels={"data": "Data", "qtd": "Notícias"},
        template="plotly_dark",
    )
    fig_v.update_traces(line_width=2.5, marker_size=6)
    fig_v.update_layout(
        paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(gridcolor="#1e2a4a"),
        yaxis=dict(gridcolor="#1e2a4a"),
    )
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
            "Data": st.column_config.TextColumn("📅 Data", width="small"),
            "Manchete": st.column_config.TextColumn("📰 Manchete", width="large"),
            "Link": st.column_config.LinkColumn("🔗 Link", width="small"),
        },
        hide_index=True,
        height=min(400, 35 * len(tabela) + 50),
    )

# ── Rodapé ───────────────────────────────────────────────────────────────────
st.mar

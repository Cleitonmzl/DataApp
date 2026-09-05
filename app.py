"""
Data App: Ingestão por Web Scraping e Visualização de Dados (UFRN / EAJ)
Visualização de quantidade de notícias publicadas sobre a EAJ por ano.
Tecnologias: Streamlit, Requests, Pandas, Plotly.
"""

import os
import time
import pandas as pd
import streamlit as st

import scraper_ufrn
import utils

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="UFRN / EAJ - Notícias & Web Scraping",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# ESTILIZAÇÃO CSS CUSTOMIZADA (DESIGN MODERNO / GLASSMORPISM)
# ==============================================================================
st.markdown("""
<style>
    /* Estilos gerais */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0369a1 100%);
        padding: 2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }
    
    .badge-custom {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin-right: 0.5rem;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# INICIALIZAÇÃO DO ESTADO DE SESSÃO
# ==============================================================================
if "news_data" not in st.session_state:
    # Se já existir arquivo gerado, carrega automaticamente
    if os.path.exists(scraper_ufrn.DEFAULT_CSV_FILE):
        try:
            df_init = pd.read_csv(scraper_ufrn.DEFAULT_CSV_FILE)
            st.session_state["news_data"] = df_init.to_dict(orient="records")
        except Exception:
            st.session_state["news_data"] = []
    elif os.path.exists(scraper_ufrn.DEFAULT_TXT_FILE):
        st.session_state["news_data"] = scraper_ufrn.load_news_from_txt(scraper_ufrn.DEFAULT_TXT_FILE)
    else:
        st.session_state["news_data"] = []

if "last_scraped_time" not in st.session_state:
    st.session_state["last_scraped_time"] = None

# ==============================================================================
# BARRA LATERAL (CONTROLES E CONFIGURAÇÕES)
# ==============================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Bras%C3%A3o_da_UFRN.svg/300px-Bras%C3%A3o_da_UFRN.svg.png", width=70)
    st.title("Painel de Controle")
    st.markdown("---")
    
    st.markdown("### 🔍 Parâmetros de Coleta")
    keyword = st.text_input("Palavra-chave (Tag)", value="EAJ", help="Tag de filtro de notícias da UFRN").strip()
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        run_scrape = st.button("🚀 Coletar Notícias", type="primary", use_container_width=True)
    with col_btn2:
        reload_cache = st.button("📂 Recarregar", use_container_width=True)
        
    st.markdown("---")
    st.markdown("### 🌐 Fonte dos Dados")
    st.caption("**Portal da UFRN**:")
    st.markdown(f"[`ufrn.br/imprensa/noticias/filtros?keyword={keyword}`](https://www.ufrn.br/imprensa/noticias/filtros?keyword={keyword})")
    
    if st.session_state["last_scraped_time"]:
        st.success(f"⏱️ Última coleta: {st.session_state['last_scraped_time']}")

# ==============================================================================
# LÓGICA DE EXECUÇÃO DO SCRAPING
# ==============================================================================
if run_scrape:
    with st.status("🔄 Executando Web Scraping no Portal da UFRN...", expanded=True) as status:
        st.write(f"📡 Conectando ao serviço de notícias da UFRN para a keyword: **{keyword}**...")
        progress_bar = st.progress(0)
        
        def update_progress(page, total_pages, count):
            pct = min(1.0, page / max(1, total_pages))
            progress_bar.progress(pct)
            st.write(f"📄 Página **{page} de {total_pages}** processada | Notícias encontradas: **{count}**")
            
        start_time = time.perf_counter()
        news_list = scraper_ufrn.fetch_eaj_news(keyword=keyword, progress_callback=update_progress)
        elapsed = time.perf_counter() - start_time
        
        if news_list:
            # Salvar nos arquivos (.txt, .csv, .json)
            scraper_ufrn.save_to_txt(news_list, scraper_ufrn.DEFAULT_TXT_FILE)
            scraper_ufrn.save_to_csv(news_list, scraper_ufrn.DEFAULT_CSV_FILE)
            scraper_ufrn.save_to_json(news_list, scraper_ufrn.DEFAULT_JSON_FILE)
            
            st.session_state["news_data"] = news_list
            st.session_state["last_scraped_time"] = time.strftime("%H:%M:%S")
            status.update(
                label=f"✅ Scraping concluído! {len(news_list)} notícias extraídas em {elapsed:.2f}s.",
                state="complete",
                expanded=False
            )
            st.rerun()
        else:
            status.update(
                label="⚠️ Nenhuma notícia encontrada ou falha de conexão.",
                state="error",
                expanded=True
            )

if reload_cache:
    if os.path.exists(scraper_ufrn.DEFAULT_CSV_FILE):
        df_csv = pd.read_csv(scraper_ufrn.DEFAULT_CSV_FILE)
        st.session_state["news_data"] = df_csv.to_dict(orient="records")
        st.toast("Dados recarregados com sucesso do cache!", icon="✅")
        st.rerun()

# Obter DataFrame a partir dos dados em sessão
raw_data = st.session_state.get("news_data", [])
df_news = scraper_ufrn.get_news_dataframe(raw_data)

# ==============================================================================
# CABEÇALHO DA APLICAÇÃO
# ==============================================================================
st.markdown("""
<div class="main-header">
    <span class="badge-custom">UFRN - Ingestão & Visualização</span>
    <span class="badge-custom">Web Scraping</span>
    <span class="badge-custom">EAJ (Escola Agrícola de Jundiaí)</span>
    <h1>🌐 Painel de Notícias UFRN: Citações à EAJ por Ano</h1>
    <p>Monitoramento e análise histórica de publicações jornalísticas da Universidade Federal do Rio Grande do Norte relacionadas à Escola Agrícola de Jundiaí.</p>
</div>
""", unsafe_allow_html=True)

# Se ainda não houver dados, exibe instruções para coletar
if df_news.empty:
    st.info(
        "👋 **Nenhum dado carregado no momento.**\n\n"
        "Clique no botão **🚀 Coletar Notícias** na barra lateral para iniciar a raspagem em tempo real "
        "ou aguarde o carregamento dos dados.",
        icon="ℹ️"
    )
    if st.button("🚀 Iniciar Coleta Agora", type="primary"):
        st.session_state["run_scrape_trigger"] = True
        st.rerun()
    st.stop()

# ==============================================================================
# KPIS & MÉTRICAS PRINCIPAIS
# ==============================================================================
kpis = utils.calculate_kpis(df_news)

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total de Notícias Coletadas</div>
        <div class="metric-value">{kpis['total_noticias']}</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Período Temporal Coberto</div>
        <div class="metric-value">{kpis['periodo']}</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Ano de Pico ({kpis['ano_pico']})</div>
        <div class="metric-value">{kpis['qtd_ano_pico']} <span style="font-size: 1rem; color: #94a3b8;">notícias</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Média de Notícias / Ano</div>
        <div class="metric-value">{kpis['media_anual']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# ABAS DA APLICAÇÃO
# ==============================================================================
tab_charts, tab_data, tab_details = st.tabs([
    "📊 Gráficos por Ano",
    "📋 Tabela de Notícias & Downloads",
    "🛠️ Metodologia & Arquitetura"
])

# ------------------------------------------------------------------------------
# ABA 1: GRÁFICOS E VISUALIZAÇÃO POR ANO (REQUISITO 2)
# ------------------------------------------------------------------------------
with tab_charts:
    st.subheader("📈 Distribuição de Notícias que citam a EAJ por Ano")
    st.markdown(
        "Abaixo estão apresentadas as visualizações solicitadas na atividade, demonstrando "
        "a evolução cronológica da quantidade de notícias publicadas no portal da UFRN."
    )
    
    dist_df = utils.get_yearly_distribution(df_news)
    
    # 1. Gráfico Nativo Streamlit (st.bar_chart) - Solicitado explicitamente no enunciado
    st.markdown("#### 1️⃣ Gráfico de Barras Nativo Streamlit (`st.bar_chart`)")
    chart_data = dist_df.set_index("Ano_Str")["Quantidade"]
    st.bar_chart(chart_data, color="#00d2ff")
    
    st.markdown("---")
    
    # 2. Gráfico Interativo com Plotly e Comparativo Donut
    st.markdown("#### 2️⃣ Visualizações Interativas Avançadas (Plotly)")
    col_chart_left, col_chart_right = st.columns([3, 2])
    
    with col_chart_left:
        fig_bar = utils.create_plotly_bar_chart(dist_df)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_chart_right:
        fig_pie = utils.create_plotly_pie_chart(dist_df)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    # Tabela resumo por ano
    with st.expander("🔍 Ver Tabela de Contagem Numérica por Ano", expanded=False):
        st.dataframe(
            dist_df[["Ano", "Quantidade"]],
            use_container_width=True,
            hide_index=True
        )

# ------------------------------------------------------------------------------
# ABA 2: TABELA DE DADOS & DOWNLOADS (REQUISITO 1)
# ------------------------------------------------------------------------------
with tab_data:
    st.subheader("📋 Registros Coletados e Exportação de Arquivos")
    st.markdown(
        "Conforme o **Requisito 1** da atividade, os dados contendo o **Ano** e a **URL** "
        "estão estruturados e disponíveis para download imediato nos formatos `.txt`, `.csv` e `.json`."
    )
    
    # Botões de Download
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    # Ler conteúdo do TXT para download
    txt_content = ""
    if os.path.exists(scraper_ufrn.DEFAULT_TXT_FILE):
        with open(scraper_ufrn.DEFAULT_TXT_FILE, "r", encoding="utf-8") as f:
            txt_content = f.read()
    else:
        txt_content = "\n".join([f"{item.get('ano')}\t{item.get('url')}\t{item.get('titulo')}" for item in raw_data])
        
    with col_dl1:
        st.download_button(
            label="📥 Baixar Arquivo TXT (.txt)",
            data=txt_content,
            file_name="noticias_eaj.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True,
            help="Arquivo texto com Ano e URL conforme solicitado no Requisito 1"
        )
        
    with col_dl2:
        csv_content = df_news.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Baixar Dados em CSV (.csv)",
            data=csv_content,
            file_name="noticias_eaj.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_dl3:
        if os.path.exists(scraper_ufrn.DEFAULT_JSON_FILE):
            with open(scraper_ufrn.DEFAULT_JSON_FILE, "r", encoding="utf-8") as f:
                json_content = f.read()
        else:
            json_content = df_news.to_json(orient="records", force_ascii=False)
            
        st.download_button(
            label="📥 Baixar Dados em JSON (.json)",
            data=json_content,
            file_name="noticias_eaj.json",
            mime="application/json",
            use_container_width=True
        )
        
    st.markdown("---")
    
    # Filtros interativos na tabela
    col_filter1, col_filter2 = st.columns([2, 1])
    with col_filter1:
        search_query = st.text_input("🔎 Filtrar por termo no título da notícia:", placeholder="Ex: curso, processo seletivo, edital...")
    with col_filter2:
        available_years = sorted(df_news["ano"].dropna().unique().astype(int).tolist(), reverse=True)
        selected_year_filter = st.selectbox("📅 Filtrar por ano específico:", options=["Todos"] + available_years)
        
    df_filtered = df_news.copy()
    if search_query:
        df_filtered = df_filtered[df_filtered["titulo"].str.contains(search_query, case=False, na=False)]
    if selected_year_filter != "Todos":
        df_filtered = df_filtered[df_filtered["ano"] == int(selected_year_filter)]
        
    st.caption(f"Exibindo **{len(df_filtered)}** de **{len(df_news)}** notícias.")
    
    # Tabela com links clicáveis
    st.dataframe(
        df_filtered[["ano", "titulo", "url", "data"]],
        column_config={
            "ano": st.column_config.NumberColumn("Ano", format="%d", width="small"),
            "titulo": st.column_config.TextColumn("Título da Notícia", width="large"),
            "url": st.column_config.LinkColumn("URL no Portal UFRN", display_text="Abrir Notícia 🔗", width="medium"),
            "data": st.column_config.TextColumn("Data Publicação", width="small")
        },
        use_container_width=True,
        hide_index=True
    )

# ------------------------------------------------------------------------------
# ABA 3: METODOLOGIA & ARQUITETURA TÉCNICA
# ------------------------------------------------------------------------------
with tab_details:
    st.subheader("🛠️ Detalhamento da Engenharia de Raspagem e Pipeline")
    
    st.markdown("""
    ### 📌 Fluxo da Ingestão de Dados
    
    1. **Requisição HTTP com Paginação Dinâmica:**
       - O portal de notícias da UFRN (`https://www.ufrn.br/imprensa/noticias/filtros?keyword=EAJ`) carrega as notícias através de chamadas assíncronas ao endpoint REST de notícias com cabeçalhos de controle de paginação (`X-WP-TotalPages`, `X-WP-Total`).
       - O módulo `scraper_ufrn.py` consome a paginação completa iterando até o fim dos registros.
       
    2. **Extração e Tratamento dos Campos:**
       - **Ano de Publicação**: Extraído a partir da propriedade ISO `date` (ex: `2026-08-31T...`) e com suporte a fallback via timestamp UNIX do campo `acf.data_de_publicacao`.
       - **URL da Notícia**: Reconstrução da URL pública do portal no padrão canônico `https://www.ufrn.br/imprensa/noticias/{id}/{slug}`.
       - **Metadados Adicionais**: Título decodificado, data formatada em padrão brasileiro (`DD/MM/YYYY`) e identificador único (`id`).
       
    3. **Persistência de Dados (Requisito 1):**
       - Arquivo **`noticias_eaj.txt`** gerado com ano, URL e título tabular.
       - Formatos adicionais **`.csv`** e **`.json`** para análise em pipelines de ciência de dados.
    """)
    
    st.code("""
# Exemplo do código de raspagem (scraper_ufrn.py)
params = {
    "_embed": "",
    "per_page": 100,
    "page": current_page,
    "tags": "EAJ"
}
response = requests.get(API_BUSCA_URL, params=params, verify=False, timeout=20)
items = response.json()
for item in items:
    ano = datetime.fromisoformat(item["date"]).year
    url = f"https://www.ufrn.br/imprensa/noticias/{item['id']}/{item['slug']}"
    news_list.append({"ano": ano, "url": url, "titulo": item["title"]["rendered"]})
    """, language="python")

# ==============================================================================
# RODAPÉ
# ==============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>"
    "Data App - Web Scraping UFRN (EAJ) | Universidade Federal do Rio Grande do Norte | "
    "Desenvolvido com Python & Streamlit"
    "</div>",
    unsafe_allow_html=True
)

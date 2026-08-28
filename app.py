"""
Data App - Web Scraping Wikipédia (UFRN)
Interface Streamlit completa para raspagem de dados, análise de texto,
geração de nuvem de palavras e comparação BS4 vs Scrapy.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# Importação dos módulos internos
from scraper_bs4 import scrape_wikipedia_bs4, build_wikipedia_url as url_bs4
from scraper_scrapy import scrape_wikipedia_scrapy, build_wikipedia_url as url_scrapy
from utils import (
    clean_text_portuguese,
    generate_wordcloud_figure,
    count_word_occurrences,
    get_top_frequent_words,
    STOPWORDS_PT
)

# Configuração da Página
st.set_page_config(
    page_title="Data App Wikipedia Scraping | UFRN",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada (Modern Dark UI)
st.markdown("""
<style>
    /* Estilo geral e fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Cartões de Métricas Customizados */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.5);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #F8FAFC;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #38BDF8;
        margin-top: 4px;
    }

    /* Destaques de Contagem */
    .search-result-box {
        background: linear-gradient(135deg, #1e1b4b, #172554);
        border: 2px solid #6366f1;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin: 16px 0;
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.25);
    }
    .search-count {
        font-size: 3.5rem;
        font-weight: 800;
        color: #38bdf8;
        line-height: 1.1;
    }
    .search-label {
        font-size: 1.1rem;
        color: #e2e8f0;
        margin-top: 6px;
    }

    /* Badge de Tag */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-blue { background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
    .badge-green { background-color: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
    .badge-purple { background-color: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #a855f7; }

    /* Custom snippet card */
    .snippet-card {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #6366f1;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
        color: #cbd5e1;
    }
    .snippet-highlight {
        background-color: rgba(234, 179, 8, 0.25);
        color: #fde047;
        padding: 1px 4px;
        border-radius: 4px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Inicialização de Session State para persistência entre abas
if "bs4_result" not in st.session_state:
    st.session_state.bs4_result = None
if "scrapy_result" not in st.session_state:
    st.session_state.scrapy_result = None
if "multi_result" not in st.session_state:
    st.session_state.multi_result = None
if "benchmark_history" not in st.session_state:
    st.session_state.benchmark_history = []

# ==============================================================================
# BARRA LATERAL (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🌐 Data App Scraping")
    st.markdown("<span class='badge badge-blue'>UFRN - Ciência de Dados</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("⚙️ Configurações da Nuvem")
    colormap_choice = st.selectbox(
        "Paleta de Cores (Colormap):",
        options=["viridis", "magma", "plasma", "inferno", "cividis", "coolwarm", "turbo"],
        index=0
    )
    max_words_slider = st.slider("Máximo de Palavras na Nuvem:", min_value=30, max_value=300, value=120, step=10)
    remove_stopwords_toggle = st.checkbox("Remover Stopwords (Português)", value=True)
    
    st.markdown("---")
    st.subheader("ℹ️ Sobre o Projeto")
    st.markdown("""
    **Objetivo:** Coleta, processamento de conteúdo HTML da Wikipédia e geração de insights com NLP e WordCloud.
    
    **Bibliotecas Chave:**
    - `Requests` + `BeautifulSoup4`
    - `Scrapy` + `Crochet` (Twisted Reactor)
    - `NLTK` (Stopwords em Português)
    - `WordCloud` & `Matplotlib`
    - `Streamlit` & `Plotly`
    """)
    st.markdown("---")
    st.caption("Desenvolvido para avaliação acadêmica • UFRN")


# ==============================================================================
# CABEÇALHO PRINCIPAL
# ==============================================================================
col_logo, col_header = st.columns([1, 6])
with col_header:
    st.title("🌐 Data App: Web Scraping Wikipédia")
    st.markdown("""
    Plataforma interativa de raspagem de dados, análise de tempo de resposta e processamento de linguagem natural 
    utilizando **Requests + BeautifulSoup4** e **Scrapy + Crochet**.
    """)

# Criação das 5 Abas Principais
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📑 1. Requests + BeautifulSoup",
    "⚡ 2. Scrapy + Crochet",
    "🔍 3. Raspagem Múltipla & Contagem",
    "📊 4. Benchmark & Comparativo",
    "🎓 5. Guia de Entrega & Colab"
])

# ==============================================================================
# ABA 1: REQUESTS + BEAUTIFUL SOUP 4
# ==============================================================================
with tab1:
    st.header("1. Raspagem com Requests + BeautifulSoup4")
    st.markdown("Extração síncrona dos parágrafos `<p>` de artigos da Wikipédia com medição precisa de tempo via `time.perf_counter()`.")
    
    col_in1, col_in2 = st.columns([4, 1])
    with col_in1:
        termo_bs4 = st.text_input(
            "Digite o termo de busca na Wikipédia:",
            value="Ciência de dados",
            key="input_bs4",
            help="Ex: Ciência de dados, Inteligência artificial, Rio Grande do Norte"
        )
    with col_in2:
        st.write("")
        st.write("")
        btn_scrape_bs4 = st.button("🚀 Raspar com BS4", type="primary", use_container_width=True)
        
    if btn_scrape_bs4:
        with st.spinner(f"Raspando 'https://pt.wikipedia.org/wiki/{termo_bs4.replace(' ', '_')}' com Requests + BS4..."):
            res = scrape_wikipedia_bs4(termo_bs4)
            st.session_state.bs4_result = res
            
            # Registrar no histórico de benchmark
            if res["status"] == "success":
                st.session_state.benchmark_history.append({
                    "Termo": termo_bs4,
                    "Motor": "Requests + BS4",
                    "Tempo (s)": res["execution_time"],
                    "Parágrafos": len(res["paragraphs"]),
                    "Palavras": res["word_count"],
                    "Caracteres": res["char_count"]
                })
                
    if st.session_state.bs4_result:
        res = st.session_state.bs4_result
        if res["status"] == "success":
            st.success(f"✅ Scraping concluído com sucesso em **{res['execution_time']} segundos**!")
            
            # Cards de Métricas
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">⏱️ Tempo de Execução</div>
                    <div class="metric-value">{res['execution_time']} <span style="font-size:1rem;font-weight:400;">s</span></div>
                    <div class="metric-subtitle">Requests + BS4</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">📝 Total de Palavras</div>
                    <div class="metric-value">{res['word_count']:,}</div>
                    <div class="metric-subtitle">{res['char_count']:,} caracteres</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">📄 Parágrafos Extraídos</div>
                    <div class="metric-value">{len(res['paragraphs'])}</div>
                    <div class="metric-subtitle">Tags &lt;p&gt; identificadas</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🔗 Status HTTP</div>
                    <div class="metric-value">{res.get('status_code', 200)} <span style="font-size:1rem;color:#10b981;">OK</span></div>
                    <div class="metric-subtitle"><a href="{res['url']}" target="_blank" style="color:#38bdf8;">Abrir Artigo ↗</a></div>
                </div>
                """, unsafe_allow_html=True)

            # Limpeza e Geração de WordCloud
            cleaned_text, cleaned_tokens = clean_text_portuguese(
                res["text"],
                remove_stopwords=remove_stopwords_toggle
            )
            
            st.markdown("---")
            col_wc, col_stats = st.columns([3, 2])
            
            with col_wc:
                st.subheader("☁️ Nuvem de Palavras (WordCloud)")
                fig_wc = generate_wordcloud_figure(
                    cleaned_text,
                    title=f"Nuvem: {res['term']} (BS4)",
                    max_words=max_words_slider,
                    colormap=colormap_choice
                )
                st.pyplot(fig_wc, use_container_width=True)
                
            with col_stats:
                st.subheader("📊 Top 10 Termos Mais Frequentes")
                df_top = get_top_frequent_words(cleaned_tokens, top_n=10)
                if not df_top.empty:
                    fig_bar = px.bar(
                        df_top,
                        x="Frequência",
                        y="Palavra",
                        orientation="h",
                        color="Frequência",
                        color_continuous_scale="Blues",
                        title="Frequência de Palavras Filtradas"
                    )
                    fig_bar.update_layout(
                        yaxis={'categoryorder':'total ascending'},
                        margin=dict(l=0, r=0, t=30, b=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#CBD5E1")
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Nenhum token disponível para contagem.")

            # Expander com o texto completo
            with st.expander("📖 Visualizar Conteúdo Bruto Extraído (Tags <p>)"):
                st.text_area("Texto Completo:", value=res["text"], height=250, disabled=True)
                st.write(f"**URL:** [{res['url']}]({res['url']})")
                
        else:
            st.error(f"❌ Erro ao extrair com BS4: {res.get('error')}")


# ==============================================================================
# ABA 2: SCRAPY + CROCHET
# ==============================================================================
with tab2:
    st.header("2. Raspagem com Scrapy + Crochet")
    st.markdown("""
    O **Scrapy** opera de forma assíncrona sobre o reactor **Twisted**.
    Com o **Crochet** (`crochet.setup()` e anotação `@wait_for`), executamos a Spider de forma segura dentro da thread do Streamlit / Google Colab sem conflito de loops.
    """)
    
    col_in_s1, col_in_s2 = st.columns([4, 1])
    with col_in_s1:
        termo_scrapy = st.text_input(
            "Digite o termo de busca para o Scrapy:",
            value="Ciência de dados",
            key="input_scrapy",
            help="Termo para raspar usando Scrapy Spider"
        )
    with col_in_s2:
        st.write("")
        st.write("")
        btn_scrape_scrapy = st.button("⚡ Raspar com Scrapy", type="primary", use_container_width=True)
        
    if btn_scrape_scrapy:
        with st.spinner(f"Executando Spider do Scrapy via Crochet para '{termo_scrapy}'..."):
            res_scrapy = scrape_wikipedia_scrapy(termo_scrapy)
            st.session_state.scrapy_result = res_scrapy
            
            # Registrar no histórico de benchmark
            if res_scrapy["status"] == "success":
                st.session_state.benchmark_history.append({
                    "Termo": termo_scrapy,
                    "Motor": "Scrapy + Crochet",
                    "Tempo (s)": res_scrapy["execution_time"],
                    "Parágrafos": len(res_scrapy["paragraphs"]),
                    "Palavras": res_scrapy["word_count"],
                    "Caracteres": res_scrapy["char_count"]
                })
                
    if st.session_state.scrapy_result:
        res = st.session_state.scrapy_result
        if res["status"] == "success":
            st.success(f"✅ Scraping com Scrapy concluído em **{res['execution_time']} segundos**!")
            
            # Cards de Métricas
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">⏱️ Tempo de Execução</div>
                    <div class="metric-value">{res['execution_time']} <span style="font-size:1rem;font-weight:400;">s</span></div>
                    <div class="metric-subtitle">Scrapy + Crochet (Twisted)</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">📝 Total de Palavras</div>
                    <div class="metric-value">{res['word_count']:,}</div>
                    <div class="metric-subtitle">{res['char_count']:,} caracteres</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">🕷️ Parágrafos Scrapy</div>
                    <div class="metric-value">{len(res['paragraphs'])}</div>
                    <div class="metric-subtitle">XPath //p string(.)</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">⚙️ Reactor Engine</div>
                    <div class="metric-value">Twisted <span style="font-size:1rem;color:#a855f7;">Async</span></div>
                    <div class="metric-subtitle"><a href="{res['url']}" target="_blank" style="color:#38bdf8;">Abrir Artigo ↗</a></div>
                </div>
                """, unsafe_allow_html=True)

            # Nuvem de Palavras
            cleaned_text_s, cleaned_tokens_s = clean_text_portuguese(
                res["text"],
                remove_stopwords=remove_stopwords_toggle
            )
            
            st.markdown("---")
            col_wc_s, col_comp = st.columns([3, 2])
            
            with col_wc_s:
                st.subheader("☁️ Nuvem de Palavras (Scrapy)")
                fig_wc_s = generate_wordcloud_figure(
                    cleaned_text_s,
                    title=f"Nuvem: {res['term']} (Scrapy)",
                    max_words=max_words_slider,
                    colormap=colormap_choice
                )
                st.pyplot(fig_wc_s, use_container_width=True)
                
            with col_comp:
                st.subheader("⚖️ Comparativo BS4 vs Scrapy")
                if st.session_state.bs4_result and st.session_state.bs4_result["status"] == "success":
                    t_bs4 = st.session_state.bs4_result["execution_time"]
                    t_scrapy = res["execution_time"]
                    diff = round(abs(t_bs4 - t_scrapy), 4)
                    faster = "BS4" if t_bs4 < t_scrapy else "Scrapy"
                    
                    st.info(f"🏆 O **{faster}** foi mais rápido nesta rodada por uma diferença de **{diff}s**.")
                    
                    df_compare = pd.DataFrame({
                        "Motor": ["Requests + BS4", "Scrapy + Crochet"],
                        "Tempo (s)": [t_bs4, t_scrapy]
                    })
                    fig_comp = px.bar(
                        df_compare,
                        x="Motor",
                        y="Tempo (s)",
                        color="Motor",
                        color_discrete_sequence=["#3b82f6", "#a855f7"],
                        text="Tempo (s)",
                        title="Comparação de Latência (segundos)"
                    )
                    fig_comp.update_traces(textposition='outside')
                    fig_comp.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#CBD5E1"),
                        showlegend=False
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-title">💡 Dica</div>
                        <div style="color:#CBD5E1; font-size:0.9rem;">
                            Execute a raspagem na <b>Aba 1 (BS4)</b> com o mesmo termo para visualizar o gráfico comparativo lado a lado aqui!
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with st.expander("📖 Visualizar Conteúdo Scrapy Extraído"):
                st.text_area("Texto Scrapy:", value=res["text"], height=250, disabled=True)
        else:
            st.error(f"❌ Erro ao extrair com Scrapy: {res.get('error')}")


# ==============================================================================
# ABA 3: RASPAGEM MÚLTIPLA (5 TERMOS), LIMPEZA STOPWORDS E CONTAGEM
# ==============================================================================
with tab3:
    st.header("3. Raspagem Múltipla (5 Termos), Limpeza e Contagem")
    st.markdown("""
    Nesta seção, realizamos a extração de **5 páginas da Wikipédia**, concatenamos seus conteúdos em um corpus unificado,
    aplicamos **remoção de stopwords em língua portuguesa com NLTK**, e realizamos a **busca exata de ocorrências** de uma palavra informada pelo usuário.
    """)
    
    # Input dos 5 termos
    default_terms = "Universidade Federal do Rio Grande do Norte, Ciência de Dados, Aprendizado de Máquina, Engenharia de Software, Armazém de Dados"
    
    st.subheader("Passo 1: Definir os 5 Termos de Busca")
    terms_input = st.text_area(
        "Digite 5 termos separados por vírgula:",
        value=default_terms,
        height=70,
        help="Separe cada termo com vírgula."
    )
    
    col_opt1, col_opt2 = st.columns([3, 1])
    with col_opt1:
        engine_choice = st.radio(
            "Selecione o motor de raspagem para as 5 páginas:",
            options=["Requests + BeautifulSoup4", "Scrapy + Crochet"],
            horizontal=True
        )
    with col_opt2:
        btn_scrape_multi = st.button("🚀 Raspar 5 Páginas e Unificar", type="primary", use_container_width=True)

    # Processamento da Raspagem Múltipla
    if btn_scrape_multi:
        term_list = [t.strip() for t in terms_input.split(",") if t.strip()]
        
        if len(term_list) < 1:
            st.error("Por favor, informe pelo menos 1 termo (recomendado: 5 termos).")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            scraped_pages = []
            combined_raw_text = []
            total_time_start = time.perf_counter()
            
            for idx, term in enumerate(term_list):
                status_text.text(f"⏳ Raspando ({idx+1}/{len(term_list)}): '{term}'...")
                progress_bar.progress((idx + 1) / len(term_list))
                
                if "Scrapy" in engine_choice:
                    page_res = scrape_wikipedia_scrapy(term)
                else:
                    page_res = scrape_wikipedia_bs4(term)
                    
                scraped_pages.append(page_res)
                if page_res["status"] == "success" and page_res["text"]:
                    combined_raw_text.append(page_res["text"])
                    
            total_multi_time = time.perf_counter() - total_time_start
            status_text.text("✨ Raspagem e unificação finalizadas com sucesso!")
            
            full_corpus_raw = "\n\n".join(combined_raw_text)
            
            # Limpeza com NLTK
            cleaned_corpus, cleaned_tokens = clean_text_portuguese(full_corpus_raw, remove_stopwords=True)
            
            st.session_state.multi_result = {
                "term_list": term_list,
                "engine": engine_choice,
                "scraped_pages": scraped_pages,
                "raw_text": full_corpus_raw,
                "cleaned_text": cleaned_corpus,
                "cleaned_tokens": cleaned_tokens,
                "total_time": round(total_multi_time, 4)
            }

    # Se já temos o resultado consolidado das 5 páginas
    if st.session_state.multi_result:
        m_data = st.session_state.multi_result
        
        st.markdown("---")
        st.subheader("📊 Estatísticas do Corpus Consolidado")
        
        raw_word_count = len(m_data["raw_text"].split())
        cleaned_word_count = len(m_data["cleaned_tokens"])
        reduction = round((1 - (cleaned_word_count / max(raw_word_count, 1))) * 100, 1)
        
        cm1, cm2, cm3, cm4 = st.columns(4)
        with cm1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📚 Páginas Processadas</div>
                <div class="metric-value">{len(m_data['scraped_pages'])}</div>
                <div class="metric-subtitle">{m_data['engine']} em {m_data['total_time']}s</div>
            </div>
            """, unsafe_allow_html=True)
        with cm2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📄 Palavras Brutas</div>
                <div class="metric-value">{raw_word_count:,}</div>
                <div class="metric-subtitle">{len(m_data['raw_text']):,} caracteres</div>
            </div>
            """, unsafe_allow_html=True)
        with cm3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🧹 Palavras Limpas</div>
                <div class="metric-value">{cleaned_word_count:,}</div>
                <div class="metric-subtitle">Sem pontuação e stopwords</div>
            </div>
            """, unsafe_allow_html=True)
        with cm4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📉 Redução por Stopwords</div>
                <div class="metric-value">{reduction}%</div>
                <div class="metric-subtitle">Tokens irrelevantes filtrados</div>
            </div>
            """, unsafe_allow_html=True)

        # ======================================================================
        # PASSO 2: BUSCA E CONTAGEM DA PALAVRA
        # ======================================================================
        st.markdown("---")
        st.subheader("Passo 2: Buscar Ocorrências de uma Palavra no Corpus")
        
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_word = st.text_input(
                "Digite uma palavra para contar no texto consolidado:",
                value="dados",
                help="A busca é insensível a maiúsculas/minúsculas e busca a palavra exata nos tokens limpos."
            )
        with col_s2:
            st.write("")
            st.write("")
            btn_count = st.button("🔍 Contar Ocorrências", type="secondary", use_container_width=True)

        # Processar contagem
        if search_word:
            count_data = count_word_occurrences(
                m_data["cleaned_tokens"],
                m_data["raw_text"],
                search_word
            )
            
            st.markdown(f"""
            <div class="search-result-box">
                <div class="search-count">{count_data['count']}</div>
                <div class="search-label">
                    Ocorrências da palavra <b>'{count_data['target_word']}'</b> no corpus das 5 páginas
                </div>
                <div style="font-size:0.9rem; color:#94a3b8; margin-top:8px;">
                    Frequência Relativa: <b>{count_data['frequency_pct']}%</b> do total de {count_data['total_words']:,} palavras filtradas.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Snippets de Contexto
            if count_data["snippets"]:
                st.markdown("##### 🔍 Trechos de Contexto Onde a Palavra Aparece:")
                for snippet in count_data["snippets"]:
                    # Realçar a palavra procurada no snippet
                    highlighted = snippet.replace(
                        search_word, f"<span class='snippet-highlight'>{search_word}</span>"
                    ).replace(
                        search_word.capitalize(), f"<span class='snippet-highlight'>{search_word.capitalize()}</span>"
                    ).replace(
                        search_word.upper(), f"<span class='snippet-highlight'>{search_word.upper()}</span>"
                    )
                    st.markdown(f"<div class='snippet-card'>... {highlighted} ...</div>", unsafe_allow_html=True)
            else:
                if count_data['count'] == 0:
                    st.warning(f"A palavra '{search_word}' não foi encontrada no corpus limpo.")

        # Nuvem e Top Palavras das 5 Páginas
        st.markdown("---")
        col_m_wc, col_m_bar = st.columns([3, 2])
        
        with col_m_wc:
            st.subheader("☁️ Nuvem de Palavras Consolidada (5 Páginas)")
            fig_multi_wc = generate_wordcloud_figure(
                m_data["cleaned_text"],
                title="Corpus Consolidado (5 Páginas)",
                max_words=max_words_slider,
                colormap=colormap_choice
            )
            st.pyplot(fig_multi_wc, use_container_width=True)
            
        with col_m_bar:
            st.subheader("📊 Top 15 Palavras do Corpus")
            df_multi_top = get_top_frequent_words(m_data["cleaned_tokens"], top_n=15)
            if not df_multi_top.empty:
                fig_m_bar = px.bar(
                    df_multi_top,
                    x="Frequência",
                    y="Palavra",
                    orientation="h",
                    color="Frequência",
                    color_continuous_scale="Viridis",
                    title="Top 15 Palavras Consolidadas"
                )
                fig_m_bar.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    margin=dict(l=0, r=0, t=30, b=0),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#CBD5E1")
                )
                st.plotly_chart(fig_m_bar, use_container_width=True)

        # Detalhes das 5 páginas em tabs internas
        with st.expander("📑 Detalhes Individuais das 5 Páginas Raspadas"):
            page_tabs = st.tabs([f"📄 {p['term']}" for p in m_data["scraped_pages"]])
            for i, p in enumerate(m_data["scraped_pages"]):
                with page_tabs[i]:
                    st.write(f"**URL:** [{p['url']}]({p['url']})")
                    st.write(f"**Tempo de extração:** {p['execution_time']}s | **Parágrafos:** {len(p['paragraphs'])} | **Palavras:** {p['word_count']}")
                    st.text_area(f"Conteúdo de {p['term']}:", value=p["text"][:1500] + "...", height=150, disabled=True)


# ==============================================================================
# ABA 4: BENCHMARK & COMPARATIVO
# ==============================================================================
with tab4:
    st.header("4. Benchmark Comparativo & Análise de Desempenho")
    st.markdown("""
    Comparação técnica detalhada entre **Requests + BeautifulSoup4** e **Scrapy + Crochet**.
    """)
    
    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        bench_term = st.text_input(
            "Termo para rodar Benchmark comparativo automatizado:",
            value="Ciência de dados",
            key="bench_term_input"
        )
    with col_b2:
        st.write("")
        st.write("")
        btn_run_bench = st.button("⚡ Executar Benchmark", type="primary", use_container_width=True)
        
    if btn_run_bench:
        with st.spinner(f"Executando teste comparativo para '{bench_term}'..."):
            # 1. Rodar BS4
            res_b_bs4 = scrape_wikipedia_bs4(bench_term)
            # 2. Rodar Scrapy
            res_b_scrapy = scrape_wikipedia_scrapy(bench_term)
            
            st.session_state.benchmark_history.append({
                "Termo": bench_term,
                "Motor": "Requests + BS4",
                "Tempo (s)": res_b_bs4["execution_time"],
                "Parágrafos": len(res_b_bs4["paragraphs"]),
                "Palavras": res_b_bs4["word_count"],
                "Caracteres": res_b_bs4["char_count"]
            })
            st.session_state.benchmark_history.append({
                "Termo": bench_term,
                "Motor": "Scrapy + Crochet",
                "Tempo (s)": res_b_scrapy["execution_time"],
                "Parágrafos": len(res_b_scrapy["paragraphs"]),
                "Palavras": res_b_scrapy["word_count"],
                "Caracteres": res_b_scrapy["char_count"]
            })
            
            st.success("Benchmark concluído!")
            
    # Tabela comparativa e gráficos
    if st.session_state.benchmark_history:
        df_bench = pd.DataFrame(st.session_state.benchmark_history)
        
        st.subheader("📈 Histórico de Execuções e Tempos de Resposta")
        st.dataframe(df_bench, use_container_width=True)
        
        fig_b = px.bar(
            df_bench,
            x="Termo",
            y="Tempo (s)",
            color="Motor",
            barmode="group",
            color_discrete_map={"Requests + BS4": "#3b82f6", "Scrapy + Crochet": "#a855f7"},
            title="Comparativo de Tempo de Execução por Termo (s)"
        )
        fig_b.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1")
        )
        st.plotly_chart(fig_b, use_container_width=True)
    else:
        st.info("Execute o benchmark acima ou faça buscas nas abas anteriores para popular o comparativo.")

    st.markdown("---")
    st.subheader("📚 Tabela Comparativa de Arquitetura")
    st.markdown("""
    | Característica | Requests + BeautifulSoup4 | Scrapy + Crochet |
    | :--- | :--- | :--- |
    | **Modelo de Execução** | Síncrono / Sequencial | Assíncrono / Baseado em Eventos (Twisted) |
    | **Complexidade** | Simples, direto e leve | Framework robusto para pipelines e crawling em escala |
    | **Consumo de Memória** | Muito baixo | Médio |
    | **Gerenciamento de Loops** | Nativo (Thread padrão do Python) | Requer desacoplamento com `crochet` em Colab/Streamlit |
    | **Ideal para** | Páginas individuais e scrapers pontuais | Crawlers em larga escala, múltiplos domínios e paginação |
    """)


# ==============================================================================
# ABA 5: GUIA DE ENTREGA & GOOGLE COLAB
# ==============================================================================
with tab5:
    st.header("🎓 Guia de Entrega, Google Colab e Roteiro de Vídeo")
    
    st.markdown("""
    ### 📦 Entregáveis da Tarefa
    1. **Link do Google Colab**: Notebook interativo pronto para execução na nuvem.
    2. **Repositório GitHub**: Código modular e estruturado com `app.py`, `scraper_bs4.py`, `scraper_scrapy.py`, `utils.py`, `requirements.txt` e `README.md`.
    3. **Vídeo Demonstrativo**: Vídeo de no máximo 2 minutos apresentando os 3 requisitos em funcionamento.
    """)
    
    st.markdown("---")
    st.subheader("🎬 Roteiro Sugerido para o Vídeo (Máx. 2 Minutos)")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("""
        **[0:00 - 0:25] Abertura e Requisito 1 (BS4)**
        - Apresentar o Data App e o objetivo (Web scraping da Wikipédia + WordCloud).
        - Mostrar a **Aba 1**, buscar `Ciência de dados`, exibir o tempo de execução e a Nuvem de Palavras gerada.
        
        **[0:25 - 0:50] Requisito 2 (Scrapy + Crochet)**
        - Navegar para a **Aba 2**, explicar o uso do `crochet.setup()` para desacoplar o reactor Twisted.
        - Executar a raspagem com Scrapy e mostrar o tempo medido e o gráfico comparativo BS4 vs Scrapy.
        """)
    with col_v2:
        st.markdown("""
        **[0:50 - 1:35] Requisito 3 (5 Termos + Stopwords + Contagem)**
        - Ir para a **Aba 3**, mostrar os 5 termos padrão (UFRN, Ciência de Dados, etc.).
        - Clicar em raspar e unificar, destacar a redução percentual de palavras com NLTK stopwords.
        - Digitar a palavra (ex: `dados`) e mostrar a contagem exata e os snippets de contexto.
        
        **[1:35 - 2:00] Conclusão e Entrega**
        - Mostrar a **Aba 4** de benchmark e o notebook Colab.
        - Encerramento.
        """)

    st.markdown("---")
    st.subheader("💻 Execução no Google Colab")
    st.markdown("""
    Para rodar o Streamlit diretamente no Google Colab, utilize as seguintes células:
    
    ```python
    # 1. Instalar dependências no Colab
    !pip install streamlit requests beautifulsoup4 scrapy crochet wordcloud matplotlib nltk pandas plotly localtunnel

    # 2. Executar o Streamlit em segundo plano com LocalTunnel
    !streamlit run app.py & npx localtunnel --port 8501
    ```
    """)

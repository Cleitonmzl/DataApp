"""
Teste End-to-End completo simulando a execução exata do Data App
e validando todos os 3 requisitos do trabalho da faculdade.
"""

import time
from scraper_bs4 import scrape_wikipedia_bs4
from scraper_scrapy import scrape_wikipedia_scrapy
from utils import (
    clean_text_portuguese,
    count_word_occurrences,
    get_top_frequent_words,
    generate_wordcloud_figure
)

def test_full_pipeline():
    print("=" * 70)
    print("VALIDAÇÃO COMPLETA DOS 3 REQUISITOS DO DATA APP (UFRN)")
    print("=" * 70)

    # -------------------------------------------------------------
    # REQUISITO 1: Requests + BeautifulSoup + Medição + WordCloud
    # -------------------------------------------------------------
    print("\n[REQUISITO 1] Testando 'Ciência de dados' com Requests + BS4...")
    termo = "Ciência de dados"
    res_bs4 = scrape_wikipedia_bs4(termo)
    print(f" -> URL: {res_bs4['url']}")
    print(f" -> Status: {res_bs4['status']}")
    print(f" -> Tempo medido: {res_bs4['execution_time']}s")
    print(f" -> Parágrafos extraídos: {len(res_bs4['paragraphs'])}")
    print(f" -> Total de palavras: {res_bs4['word_count']}")
    assert res_bs4["status"] == "success"
    
    clean_bs4, tokens_bs4 = clean_text_portuguese(res_bs4["text"], remove_stopwords=True)
    fig_bs4 = generate_wordcloud_figure(clean_bs4, title=f"Nuvem BS4: {termo}")
    assert fig_bs4 is not None
    print(" -> Nuvem de palavras gerada com sucesso.")
    print(" ✓ Requisito 1 validado!")

    # -------------------------------------------------------------
    # REQUISITO 2: Scrapy + Crochet + Medição + Comparativo
    # -------------------------------------------------------------
    print("\n[REQUISITO 2] Testando 'Ciência de dados' com Scrapy + Crochet...")
    res_scrapy = scrape_wikipedia_scrapy(termo)
    print(f" -> URL: {res_scrapy['url']}")
    print(f" -> Status: {res_scrapy['status']}")
    print(f" -> Tempo medido: {res_scrapy['execution_time']}s")
    print(f" -> Parágrafos extraídos: {len(res_scrapy['paragraphs'])}")
    print(f" -> Total de palavras: {res_scrapy['word_count']}")
    assert res_scrapy["status"] == "success"
    
    clean_scrapy, tokens_scrapy = clean_text_portuguese(res_scrapy["text"], remove_stopwords=True)
    fig_scrapy = generate_wordcloud_figure(clean_scrapy, title=f"Nuvem Scrapy: {termo}")
    assert fig_scrapy is not None
    
    print(f" -> Comparativo: BS4={res_bs4['execution_time']}s vs Scrapy={res_scrapy['execution_time']}s")
    print(" ✓ Requisito 2 validado!")

    # -------------------------------------------------------------
    # REQUISITO 3: 5 Páginas, Concatenação, Stopwords NLTK e Contagem
    # -------------------------------------------------------------
    print("\n[REQUISITO 3] Testando 5 páginas simultâneas, unificação, stopwords e busca...")
    cinco_termos = [
        "Universidade Federal do Rio Grande do Norte",
        "Ciência de Dados",
        "Aprendizado de Máquina",
        "Engenharia de Software",
        "Armazém de Dados"
    ]
    
    corpus_bruto = []
    t_start = time.perf_counter()
    for t in cinco_termos:
        r = scrape_wikipedia_bs4(t)
        assert r["status"] == "success", f"Falha ao raspar {t}: {r.get('error')}"
        corpus_bruto.append(r["text"])
        print(f"   - Raspado: '{t}' ({len(r['paragraphs'])} parágrafos, {r['word_count']} palavras)")
        
    t_total = time.perf_counter() - t_start
    texto_unificado = "\n\n".join(corpus_bruto)
    print(f" -> Tempo total das 5 páginas: {round(t_total, 4)}s")
    print(f" -> Total de caracteres do corpus bruto: {len(texto_unificado):,}")
    print(f" -> Total de palavras do corpus bruto: {len(texto_unificado.split()):,}")

    # Limpeza de Stopwords com NLTK
    texto_limpo, tokens_limpos = clean_text_portuguese(texto_unificado, remove_stopwords=True)
    print(f" -> Total de palavras limpas (sem stopwords): {len(tokens_limpos):,}")
    reducao = (1 - (len(tokens_limpos) / len(texto_unificado.split()))) * 100
    print(f" -> Redução por stopwords: {round(reducao, 2)}%")

    # Teste de contagem com a palavra "dados"
    palavra_alvo = "dados"
    resultado_contagem = count_word_occurrences(tokens_limpos, texto_unificado, palavra_alvo)
    print(f"\n -> Contagem da palavra '{palavra_alvo}':")
    print(f"    * Total de ocorrências: {resultado_contagem['count']}")
    print(f"    * Frequência relativa: {resultado_contagem['frequency_pct']}%")
    print(f"    * Snippets de contexto capturados: {len(resultado_contagem['snippets'])}")
    assert resultado_contagem["count"] > 0, "A contagem da palavra 'dados' deveria ser maior que 0"

    # Teste com outra palavra: "software"
    res_sw = count_word_occurrences(tokens_limpos, texto_unificado, "software")
    print(f"\n -> Contagem da palavra 'software': {res_sw['count']} ocorrências")

    # Nuvem de palavras do corpus consolidado
    fig_corpus = generate_wordcloud_figure(texto_limpo, title="Nuvem do Corpus (5 Páginas)")
    assert fig_corpus is not None
    print(" -> Nuvem de palavras do corpus consolidado gerada com sucesso.")

    # Top 10 mais frequentes
    df_top = get_top_frequent_words(tokens_limpos, top_n=10)
    print("\n -> Top 10 palavras mais frequentes no corpus:")
    for _, row in df_top.iterrows():
        print(f"    - {row['Palavra']}: {row['Frequência']}")

    print("\n" + "=" * 70)
    print("🎉 TODOS OS REQUISITOS DO PROJETO FORAM VALIDADOS COM 100% DE SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    test_full_pipeline()

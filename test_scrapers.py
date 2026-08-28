"""
Script de Testes Automatizados para validação dos módulos:
- scraper_bs4
- scraper_scrapy
- utils (stopwords, WordCloud, contagem)
"""

import sys
import os

def run_tests():
    print("=" * 60)
    print("INICIANDO TESTES DO PROJETO DATA APP (WEB SCRAPING UFRN)")
    print("=" * 60)

    # 1. Testar BS4
    print("\n[1/4] Testando Scraper BS4 (Requests + BeautifulSoup)...")
    from scraper_bs4 import scrape_wikipedia_bs4
    res_bs4 = scrape_wikipedia_bs4("Ciência de dados")
    print(f" -> Status: {res_bs4['status']}")
    print(f" -> URL: {res_bs4['url']}")
    print(f" -> Tempo de execução: {res_bs4['execution_time']}s")
    print(f" -> Qtd Parágrafos: {len(res_bs4['paragraphs'])}")
    print(f" -> Caracteres extraídos: {res_bs4['char_count']}")
    assert res_bs4["status"] == "success", f"Falha no BS4: {res_bs4.get('error')}"
    assert len(res_bs4["paragraphs"]) > 0, "Nenhum parágrafo extraído no BS4"
    print("  ✓ Teste BS4 passou com sucesso!")

    # 2. Testar Scrapy + Crochet
    print("\n[2/4] Testando Scraper Scrapy (Scrapy + Crochet)...")
    from scraper_scrapy import scrape_wikipedia_scrapy
    res_scrapy = scrape_wikipedia_scrapy("Ciência de dados")
    print(f" -> Status: {res_scrapy['status']}")
    print(f" -> URL: {res_scrapy['url']}")
    print(f" -> Tempo de execução: {res_scrapy['execution_time']}s")
    print(f" -> Qtd Parágrafos: {len(res_scrapy['paragraphs'])}")
    print(f" -> Caracteres extraídos: {res_scrapy['char_count']}")
    assert res_scrapy["status"] == "success", f"Falha no Scrapy: {res_scrapy.get('error')}"
    assert len(res_scrapy["paragraphs"]) > 0, "Nenhum parágrafo extraído no Scrapy"
    print("  ✓ Teste Scrapy passou com sucesso!")

    # 3. Testar NLP e Limpeza de Stopwords
    print("\n[3/4] Testando Limpeza de Stopwords e Tokenização NLTK...")
    from utils import clean_text_portuguese, count_word_occurrences, get_top_frequent_words
    sample_text = res_bs4["text"]
    cleaned_text, cleaned_tokens = clean_text_portuguese(sample_text, remove_stopwords=True)
    print(f" -> Tokens brutos aproximados: {len(sample_text.split())}")
    print(f" -> Tokens limpos (sem stopwords): {len(cleaned_tokens)}")
    assert len(cleaned_tokens) < len(sample_text.split()), "As stopwords não reduziram os tokens"
    
    # Testar contagem de palavra
    count_info = count_word_occurrences(cleaned_tokens, sample_text, "dados")
    print(f" -> Ocorrências da palavra 'dados': {count_info['count']}")
    print(f" -> Frequência relativa: {count_info['frequency_pct']}%")
    print(f" -> Snippets encontrados: {len(count_info['snippets'])}")
    assert count_info["count"] > 0, "Palavra 'dados' deveria aparecer no artigo de Ciência de dados"
    print("  ✓ Teste NLP e contagem passou com sucesso!")

    # 4. Testar Geração de WordCloud
    print("\n[4/4] Testando Geração de Nuvem de Palavras (WordCloud)...")
    from utils import generate_wordcloud_figure
    fig = generate_wordcloud_figure(cleaned_text, title="Teste Nuvem")
    assert fig is not None, "Figura da WordCloud não foi gerada"
    print("  ✓ Teste WordCloud passou com sucesso!")

    print("\n" + "=" * 60)
    print(" TODOS OS TESTES PASSARAM COM SUCESSO! ")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()

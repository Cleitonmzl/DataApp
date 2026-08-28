"""
Módulo de Web Scraping utilizando Scrapy + Crochet
Projeto Data App - Web Scraping UFRN

O Scrapy utiliza o reactor Twisted (orientado a eventos/assíncrono).
Para permitir a execução segura em ambientes interativos como Streamlit e Google Colab,
utilizamos o Crochet para desacoplar e gerenciar o reactor em background thread.
"""

import time
import urllib.parse
import requests
import crochet
import scrapy
from scrapy.crawler import CrawlerRunner

# Inicializar o Crochet para rodar o Twisted reactor em background thread
crochet.setup()

# Configurações do CrawlerRunner
CRAWLER_SETTINGS = {
    "USER_AGENT": "WikiDataApp-UFRN/1.0 (Academic Research; cleiton@ufrn.br) Scrapy/2.11",
    "LOG_LEVEL": "ERROR",
    "ROBOTSTXT_OBEY": False,
    "COOKIES_ENABLED": False,
    "DOWNLOAD_TIMEOUT": 15,
    "RETRY_TIMES": 2,
    "TWISTED_REACTOR": "twisted.internet.epollreactor.EPollReactor",
    "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7"
}

runner = CrawlerRunner(settings=CRAWLER_SETTINGS)


class WikipediaSpider(scrapy.Spider):
    """
    Spider do Scrapy especializada em raspar o conteúdo de artigos da Wikipédia em português.
    """
    name = "wikipedia_spider"

    def __init__(self, target_url: str, items_collector: list, *args, **kwargs):
        super(WikipediaSpider, self).__init__(*args, **kwargs)
        self.start_urls = [target_url]
        self.items_collector = items_collector

    def parse(self, response):
        """
        Extrai todos os parágrafos <p> do corpo do artigo da Wikipédia.
        Utiliza XPath string(.) para garantir a captura do texto completo.
        """
        paragraphs_selectors = response.xpath(
            "//div[@id='bodyContent']//p | //div[contains(@class, 'mw-parser-output')]//p | //p"
        )
        
        extracted_paragraphs = []
        for p in paragraphs_selectors:
            text = p.xpath("string(.)").get()
            if text:
                cleaned = text.strip()
                if cleaned and len(cleaned) > 5:
                    extracted_paragraphs.append(cleaned)
                    
        item = {
            "url": response.url,
            "status": response.status,
            "paragraphs": extracted_paragraphs
        }
        self.items_collector.append(item)
        yield item


@crochet.wait_for(timeout=30.0)
def _run_spider(target_url: str) -> list[dict]:
    """
    Executa o crawler no reactor do Crochet e aguarda a finalização síncrona.
    """
    items = []
    deferred = runner.crawl(WikipediaSpider, target_url=target_url, items_collector=items)
    deferred.addBoth(lambda _: items)
    return deferred


def build_wikipedia_url(term: str) -> str:
    """
    Formata e resolve a URL canônica da Wikipédia em português para o termo pesquisado.
    Lida com variações de maiúsculas/minúsculas e redirecionamentos.
    """
    cleaned_term = term.strip()
    if not cleaned_term:
        return ""
        
    headers = {"User-Agent": "WikiDataApp-UFRN/1.0 (Academic Research; cleiton@ufrn.br)"}
    formatted_term = cleaned_term.replace(" ", "_")
    encoded_term = urllib.parse.quote(formatted_term, safe=":/_")
    direct_url = f"https://pt.wikipedia.org/wiki/{encoded_term}"
    
    # 1. Checar tentativa direta
    try:
        head_resp = requests.head(direct_url, headers=headers, timeout=4, allow_redirects=True)
        if head_resp.status_code == 200:
            return head_resp.url
    except Exception:
        pass
        
    # 2. Tentativa com Sentence case (ex: 'Ciência de dados' em vez de 'Ciência de Dados')
    try:
        sentence_cased = cleaned_term[0].upper() + cleaned_term[1:].lower()
        formatted_sc = sentence_cased.replace(" ", "_")
        encoded_sc = urllib.parse.quote(formatted_sc, safe=":/_")
        sc_url = f"https://pt.wikipedia.org/wiki/{encoded_sc}"
        head_resp = requests.head(sc_url, headers=headers, timeout=4, allow_redirects=True)
        if head_resp.status_code == 200:
            return head_resp.url
    except Exception:
        pass
        
    # 3. Fallback via Wikipedia OpenSearch API
    try:
        api_url = f"https://pt.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(cleaned_term)}&limit=1&namespace=0&format=json"
        api_resp = requests.get(api_url, headers=headers, timeout=4)
        if api_resp.status_code == 200:
            data = api_resp.json()
            if len(data) >= 4 and data[3]:
                return data[3][0]
    except Exception:
        pass

    return direct_url


def scrape_wikipedia_scrapy(term: str) -> dict:
    """
    Função pública para executar o scraping da Wikipédia via Scrapy + Crochet.
    Mede o tempo exato com time.perf_counter().
    
    Retorna:
        dict: Dicionário padronizado com os dados raspados, tempo de execução e status.
    """
    if not term or not term.strip():
        return {
            "term": term,
            "url": "",
            "text": "",
            "paragraphs": [],
            "execution_time": 0.0,
            "char_count": 0,
            "word_count": 0,
            "status": "error",
            "error": "Termo de busca vazio."
        }

    start_time = time.perf_counter()
    url = build_wikipedia_url(term)

    try:
        results = _run_spider(target_url=url)
        elapsed_time = time.perf_counter() - start_time

        if not results:
            return {
                "term": term,
                "url": url,
                "text": "",
                "paragraphs": [],
                "execution_time": round(elapsed_time, 4),
                "char_count": 0,
                "word_count": 0,
                "status": "error",
                "error": f"Nenhum dado foi retornado pelo Scrapy para '{term}' (página inexistente ou inacessível)."
            }

        item = results[0]
        paragraphs = item.get("paragraphs", [])
        full_text = "\n\n".join(paragraphs)

        return {
            "term": term,
            "url": item.get("url", url),
            "text": full_text,
            "paragraphs": paragraphs,
            "execution_time": round(elapsed_time, 4),
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
            "status": "success",
            "status_code": item.get("status", 200),
            "error": None
        }

    except crochet.TimeoutError:
        elapsed_time = time.perf_counter() - start_time
        return {
            "term": term,
            "url": url,
            "text": "",
            "paragraphs": [],
            "execution_time": round(elapsed_time, 4),
            "char_count": 0,
            "word_count": 0,
            "status": "error",
            "error": f"Tempo limite (timeout) excedido ao raspar '{term}' com Scrapy."
        }
    except Exception as e:
        elapsed_time = time.perf_counter() - start_time
        return {
            "term": term,
            "url": url,
            "text": "",
            "paragraphs": [],
            "execution_time": round(elapsed_time, 4),
            "char_count": 0,
            "word_count": 0,
            "status": "error",
            "error": f"Erro na execução do Scrapy: {str(e)}"
        }

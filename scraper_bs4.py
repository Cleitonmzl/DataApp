"""
Módulo de Web Scraping utilizando Requests + BeautifulSoup4
Projeto Data App - Web Scraping UFRN
"""

import time
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "WikiDataApp-UFRN/1.0 (Academic Research; cleiton@ufrn.br) python-requests/2.31.0"
}


def build_wikipedia_url(term: str) -> str:
    """
    Formata e resolve a URL canônica da Wikipédia em português para o termo pesquisado.
    Lida inteligentemente com variações de maiúsculas/minúsculas e redirecionamentos.
    """
    cleaned_term = term.strip()
    if not cleaned_term:
        return ""
        
    formatted_term = cleaned_term.replace(" ", "_")
    encoded_term = urllib.parse.quote(formatted_term, safe=":/_")
    direct_url = f"https://pt.wikipedia.org/wiki/{encoded_term}"
    
    # 1. Checar tentativa direta rápida
    try:
        head_resp = requests.head(direct_url, headers=HEADERS, timeout=4, allow_redirects=True)
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
        head_resp = requests.head(sc_url, headers=HEADERS, timeout=4, allow_redirects=True)
        if head_resp.status_code == 200:
            return head_resp.url
    except Exception:
        pass
        
    # 3. Fallback via Wikipedia OpenSearch API
    try:
        api_url = f"https://pt.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(cleaned_term)}&limit=1&namespace=0&format=json"
        api_resp = requests.get(api_url, headers=HEADERS, timeout=4)
        if api_resp.status_code == 200:
            data = api_resp.json()
            if len(data) >= 4 and data[3]:
                return data[3][0]
    except Exception:
        pass

    return direct_url


def scrape_wikipedia_bs4(term: str) -> dict:
    """
    Realiza o scraping de uma página da Wikipédia utilizando Requests e BeautifulSoup4.
    Mede com precisão o tempo de execução através de time.perf_counter().
    
    Retorna:
        dict: Dicionário contendo os dados extraídos, tempo de execução e metadados.
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
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code == 404:
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
                "status_code": 404,
                "error": f"Página não encontrada na Wikipédia para o termo '{term}' (404)."
            }
            
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Localizar a área de conteúdo principal da Wikipédia
        content_div = soup.find("div", {"id": "bodyContent"}) or soup.find("div", {"class": "mw-parser-output"}) or soup
        
        # Extrair todos os parágrafos <p>
        paragraphs_tags = content_div.find_all("p")
        
        paragraphs = []
        for p in paragraphs_tags:
            text = p.get_text().strip()
            if text and len(text) > 5:
                paragraphs.append(text)
                
        full_text = "\n\n".join(paragraphs)
        elapsed_time = time.perf_counter() - start_time
        
        return {
            "term": term,
            "url": response.url,
            "text": full_text,
            "paragraphs": paragraphs,
            "execution_time": round(elapsed_time, 4),
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
            "status": "success",
            "status_code": response.status_code,
            "error": None
        }
        
    except requests.exceptions.RequestException as e:
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
            "error": f"Erro de conexão com a Wikipédia: {str(e)}"
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
            "error": f"Erro inesperado no parsing BS4: {str(e)}"
        }

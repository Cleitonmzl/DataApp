"""
Módulo de Web Scraping para Notícias da UFRN (Filtro por Keyword / EAJ).
Coleta URLs, ano de publicação e metadados das notícias do portal da UFRN.
"""

import os
import json
import requests
import urllib3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Callable

# Desativar avisos de certificados SSL da UFRN se necessário
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URLs e Endpoints da UFRN
BASE_PORTAL_URL = "https://www.ufrn.br/imprensa/noticias/"
API_BUSCA_URL = "https://webcache01-producao.info.ufrn.br/admin/portal-ufrn/wp-json/wp/v2/noticias-busca/"
DEFAULT_KEYWORD = "EAJ"
DEFAULT_TXT_FILE = "noticias_eaj.txt"
DEFAULT_CSV_FILE = "noticias_eaj.csv"
DEFAULT_JSON_FILE = "noticias_eaj.json"


def fetch_eaj_news(
    keyword: str = DEFAULT_KEYWORD,
    max_pages: Optional[int] = None,
    per_page: int = 100,
    timeout: int = 20,
    progress_callback: Optional[Callable[[int, int, int], None]] = None
) -> List[Dict]:
    """
    Coleta todas as notícias da UFRN associadas à keyword especificada (padrão: EAJ).
    
    Args:
        keyword: Termo ou tag de busca (ex: 'EAJ').
        max_pages: Limite opcional de páginas a consultar (None para todas).
        per_page: Quantidade de itens por página da requisição (máx 100).
        timeout: Tempo limite de cada requisição em segundos.
        progress_callback: Função callback(page_atual, total_paginas, total_itens_coletados).
        
    Returns:
        Lista de dicionários com as chaves: 'ano', 'url', 'titulo', 'data', 'id', 'slug'.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
    }
    
    all_news: List[Dict] = []
    current_page = 1
    total_pages = 1
    
    while True:
        params = {
            "_embed": "",
            "per_page": per_page,
            "page": current_page,
            "tags": keyword
        }
        
        try:
            response = requests.get(
                API_BUSCA_URL,
                params=params,
                headers=headers,
                verify=False,
                timeout=timeout
            )
            
            if response.status_code != 200:
                # Se ultrapassou o total de páginas da API
                if response.status_code == 400 and current_page > 1:
                    break
                print(f"[Aviso] Requisição falhou na página {current_page} com status {response.status_code}")
                break
                
            # Atualiza o total de páginas informado nos cabeçalhos HTTP
            header_pages = response.headers.get("X-WP-TotalPages")
            if header_pages:
                total_pages = int(header_pages)
                
            items = response.json()
            if not isinstance(items, list) or len(items) == 0:
                break
                
            for item in items:
                news_id = item.get("id")
                slug = item.get("slug", "")
                
                # Extração do ano e data
                date_str = item.get("date", "")
                year = None
                
                if date_str:
                    try:
                        # Formato ISO: 2026-08-31T08:57:14
                        dt = datetime.fromisoformat(date_str)
                        year = dt.year
                        formatted_date = dt.strftime("%d/%m/%Y %H:%M")
                    except Exception:
                        year = int(date_str[:4]) if len(date_str) >= 4 else None
                        formatted_date = date_str
                else:
                    # Fallback para timestamp ACF
                    acf_date = item.get("acf", {}).get("data_de_publicacao")
                    if acf_date:
                        try:
                            dt = datetime.fromtimestamp(int(acf_date))
                            year = dt.year
                            formatted_date = dt.strftime("%d/%m/%Y %H:%M")
                        except Exception:
                            year = None
                            formatted_date = ""
                    else:
                        formatted_date = ""
                
                # Título da notícia
                title_obj = item.get("title", {})
                title = title_obj.get("rendered", "") if isinstance(title_obj, dict) else str(title_obj)
                
                # URL oficial no portal da UFRN
                if slug:
                    url = f"{BASE_PORTAL_URL}{news_id}/{slug}"
                else:
                    url = f"{BASE_PORTAL_URL}{news_id}"
                    
                all_news.append({
                    "ano": year,
                    "url": url,
                    "titulo": title,
                    "data": formatted_date,
                    "id": news_id,
                    "slug": slug
                })
            
            if progress_callback:
                progress_callback(current_page, total_pages, len(all_news))
                
            if max_pages and current_page >= max_pages:
                break
                
            if current_page >= total_pages:
                break
                
            current_page += 1
            
        except Exception as e:
            print(f"[Erro] Falha ao coletar página {current_page}: {e}")
            break
            
    return all_news


def save_to_txt(news_list: List[Dict], filepath: str = DEFAULT_TXT_FILE) -> str:
    """
    Salva os dados coletados em arquivo .txt conforme especificado no Requisito 1.
    Formato: [ANO] URL (ou formato tabular ANO \t URL).
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# ====================================================================\n")
        f.write("# NOTICIAS UFRN - PALAVRA-CHAVE: EAJ\n")
        f.write(f"# Coletado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"# Total de registros: {len(news_list)}\n")
        f.write("# Formato: ANO | URL | TITULO\n")
        f.write("# ====================================================================\n\n")
        for item in news_list:
            ano = item.get("ano", "N/D")
            url = item.get("url", "")
            titulo = item.get("titulo", "").replace("\n", " ").strip()
            f.write(f"{ano}\t{url}\t{titulo}\n")
    return filepath


def save_to_csv(news_list: List[Dict], filepath: str = DEFAULT_CSV_FILE) -> str:
    """Salva os dados coletados em formato CSV para análise de dados."""
    df = pd.DataFrame(news_list)
    df.to_csv(filepath, index=False, encoding="utf-8")
    return filepath


def save_to_json(news_list: List[Dict], filepath: str = DEFAULT_JSON_FILE) -> str:
    """Salva os dados coletados em formato JSON estruturado."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    return filepath


def load_news_from_txt(filepath: str = DEFAULT_TXT_FILE) -> List[Dict]:
    """Carrega dados previamente salvos a partir de arquivo .txt."""
    if not os.path.exists(filepath):
        return []
    news = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                try:
                    ano = int(parts[0])
                except ValueError:
                    ano = parts[0]
                url = parts[1]
                titulo = parts[2] if len(parts) > 2 else ""
                news.append({"ano": ano, "url": url, "titulo": titulo})
    return news


def get_news_dataframe(news_list: List[Dict]) -> pd.DataFrame:
    """Converte a lista de notícias em um DataFrame Pandas pronto para gráficos."""
    if not news_list:
        return pd.DataFrame(columns=["ano", "url", "titulo", "data", "id"])
    df = pd.DataFrame(news_list)
    if "ano" in df.columns:
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    return df


if __name__ == "__main__":
    print(f"[*] Iniciando Web Scraping de notícias da UFRN (Keyword: {DEFAULT_KEYWORD})...")
    
    def on_progress(p, tp, total):
        print(f" -> Página {p}/{tp} processada | Total de notícias coletadas: {total}")
        
    news = fetch_eaj_news(progress_callback=on_progress)
    print(f"[+] Coleta finalizada com sucesso! Total de {len(news)} notícias extraídas.")
    
    txt_path = save_to_txt(news)
    csv_path = save_to_csv(news)
    json_path = save_to_json(news)
    
    print(f"[+] Arquivo TXT gerado: {txt_path}")
    print(f"[+] Arquivo CSV gerado: {csv_path}")
    print(f"[+] Arquivo JSON gerado: {json_path}")
    
    df = get_news_dataframe(news)
    print("\n--- Distribuição de Notícias por Ano ---")
    contagem_ano = df["ano"].value_counts().sort_index(ascending=False)
    print(contagem_ano)

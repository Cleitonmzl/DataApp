"""
Módulo de Utilitários para Processamento de Linguagem Natural (NLP),
Geração de Nuvem de Palavras (WordCloud) e Métricas Estatísticas.
Projeto Data App - Web Scraping UFRN
"""

import re
import string
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import nltk

import os
import warnings

# Suprimir avisos desnecessários do NLTK downloader
warnings.filterwarnings("ignore", category=UserWarning, module="nltk")

# Garantir download seguro de recursos do NLTK
def setup_nltk():
    """Baixa os recursos necessários do NLTK caso não estejam presentes."""
    nltk_data_dir = os.path.expanduser("~/nltk_data")
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.append(nltk_data_dir)
        
    resources = ['stopwords', 'punkt', 'punkt_tab']
    for resource in resources:
        try:
            nltk.download(resource, download_dir=nltk_data_dir, quiet=True)
        except Exception:
            pass

setup_nltk()

try:
    from nltk.corpus import stopwords
    STOPWORDS_PT = set(stopwords.words('portuguese'))
except Exception:
    # Fallback caso haja indisponibilidade de rede
    STOPWORDS_PT = {
        'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma',
        'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele',
        'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já',
        'está', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era',
        'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles',
        'estão', 'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha',
        'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe',
        'deles', 'essas', 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos',
        'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos',
        'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles',
        'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve',
        'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos',
        'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver',
        'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram',
        'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem',
        'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão',
        'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram',
        'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse',
        'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão',
        'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos',
        'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos',
        'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei',
        'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam', 'artigo', 'artigos', 'links',
        'externos', 'referências', 'ver', 'também', 'página', 'wikipédia', 'conteúdo', 'sobre'
    }

# Adicionar termos extras comumente presentes em páginas wiki
CUSTOM_WIKI_STOPWORDS = {
    'artigo', 'artigos', 'links', 'externos', 'referências', 'ver', 'também', 
    'página', 'wikipédia', 'conteúdo', 'sobre', 'editar', 'pelo', 'pela', 'segundo', 
    'sendo', 'onde', 'além', 'ainda', 'assim', 'após', 'durante', 'sob', 'sobre'
}
STOPWORDS_PT.update(CUSTOM_WIKI_STOPWORDS)


def clean_text_portuguese(raw_text: str, remove_stopwords: bool = True) -> tuple[str, list[str]]:
    """
    Limpa o texto bruto da Wikipédia:
    - Converte para minúsculas
    - Remove referências numéricas como [1], [2], [nota 1]
    - Remove pontuação e caracteres especiais
    - Remove stopwords em português (opcional)
    
    Retorna:
        tuple[str, list[str]]: (texto limpo concatenado, lista de tokens limpos)
    """
    if not raw_text or not isinstance(raw_text, str):
        return "", []

    # 1. Remover referências da Wikipédia como [1], [12], [carece de fontes], etc.
    text = re.sub(r'\[.*?\]', ' ', raw_text)
    
    # 2. Converter para minúsculas
    text = text.lower()
    
    # 3. Remover caracteres especiais e pontuação, mantendo letras acentuadas e espaços
    # Expressão preserva letras do alfabeto latino estendido (incluindo acentos e ç)
    text = re.sub(r'[^a-záàâãéèêíïóôõöúçñ\s]', ' ', text)
    
    # 4. Normalizar espaços múltiplos
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 5. Tokenizar palavras
    tokens = text.split()
    
    # 6. Filtrar stopwords e palavras muito curtas (<= 2 caracteres)
    if remove_stopwords:
        cleaned_tokens = [
            word for word in tokens 
            if word not in STOPWORDS_PT and len(word) > 2
        ]
    else:
        cleaned_tokens = [word for word in tokens if len(word) > 1]
        
    cleaned_string = " ".join(cleaned_tokens)
    return cleaned_string, cleaned_tokens


def generate_wordcloud_figure(
    text: str,
    title: str = "Nuvem de Palavras",
    max_words: int = 150,
    colormap: str = "viridis",
    background_color: str = "#111827",
    width: int = 1000,
    height: int = 500
) -> plt.Figure:
    """
    Gera uma figura matplotlib contendo a Nuvem de Palavras estilizada.
    """
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=background_color)
    
    if not text.strip():
        ax.text(
            0.5, 0.5, "Texto insuficiente para gerar Nuvem de Palavras",
            horizontalalignment='center', verticalalignment='center',
            color='#9CA3AF', fontsize=14, transform=ax.transAxes
        )
        ax.axis("off")
        return fig
        
    wc = WordCloud(
        width=width,
        height=height,
        background_color=background_color,
        colormap=colormap,
        max_words=max_words,
        stopwords=STOPWORDS_PT,
        collocations=False,
        random_state=42,
        contour_width=0,
        prefer_horizontal=0.85
    ).generate(text)
    
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=16, color="#F3F4F6", pad=12, fontweight="bold")
        
    plt.tight_layout(pad=0)
    return fig


def count_word_occurrences(
    cleaned_tokens: list[str],
    raw_text: str,
    target_word: str
) -> dict:
    """
    Conta o número exato de ocorrências da palavra pesquisada no texto limpo
    e extrai trechos de contexto (snippets) do texto original.
    
    Retorna:
        dict: Estatísticas e trechos de contexto da ocorrência da palavra.
    """
    if not target_word or not target_word.strip():
        return {
            "target_word": "",
            "count": 0,
            "total_words": len(cleaned_tokens),
            "frequency_pct": 0.0,
            "snippets": []
        }
        
    normalized_target = target_word.strip().lower()
    
    # Contagem exata na lista de tokens limpos
    count = cleaned_tokens.count(normalized_target)
    total_words = len(cleaned_tokens)
    freq_pct = (count / total_words * 100) if total_words > 0 else 0.0
    
    # Extrair snippets do texto original onde a palavra aparece (com regex boundary)
    snippets = []
    if raw_text:
        pattern = rf'([^.!?\n]*?\b{re.escape(normalized_target)}\b[^.!?\n]*)'
        matches = re.finditer(pattern, raw_text, flags=re.IGNORECASE)
        for i, match in enumerate(matches):
            snippet = match.group(1).strip()
            if snippet and len(snippet) > 10:
                snippets.append(snippet)
            if len(snippets) >= 8:  # Limitar para não poluir a interface
                break
                
    return {
        "target_word": normalized_target,
        "count": count,
        "total_words": total_words,
        "frequency_pct": round(freq_pct, 4),
        "snippets": snippets
    }


def get_top_frequent_words(cleaned_tokens: list[str], top_n: int = 15) -> pd.DataFrame:
    """
    Retorna um DataFrame com as palavras mais frequentes do texto limpo.
    """
    if not cleaned_tokens:
        return pd.DataFrame(columns=["Palavra", "Frequência"])
        
    counter = Counter(cleaned_tokens)
    most_common = counter.most_common(top_n)
    df = pd.DataFrame(most_common, columns=["Palavra", "Frequência"])
    return df

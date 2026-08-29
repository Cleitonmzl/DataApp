# 🌐 Data App: Web Scraping Wikipédia (UFRN)

Aplicação interativa desenvolvida em **Streamlit** para raspagem de dados em páginas HTML da Wikipédia em língua portuguesa, medição e comparação de desempenho entre bibliotecas (**Requests + BeautifulSoup4** vs **Scrapy + Crochet**), processamento de linguagem natural com remoção de *stopwords* em português (**NLTK**) e geração de nuvens de palavras (**WordCloud**).

---

## 🎯 Objetivos e Requisitos Atendidos

1. **Raspagem com Requests + BeautifulSoup4**:
   - Extração dos parágrafos `<p>` de artigos da Wikipédia a partir de termo pesquisado pelo usuário.
   - Medição e registro preciso do tempo de execução com `time.perf_counter()`.
   - Geração de Nuvem de Palavras (*WordCloud*) estilizada.
2. **Raspagem com Scrapy + Crochet**:
   - Implementação de Spider Scrapy executada em reactor Twisted desacoplado via `crochet` (`crochet.setup()` e `@wait_for`).
   - Medição de tempo de execução e comparativo de desempenho com a solução BS4.
3. **Raspagem Múltipla (5 Páginas), Limpeza e Contagem de Palavra**:
   - Entrada para 5 termos separados por vírgula (Padrão: *Universidade Federal do Rio Grande do Norte, Ciência de Dados, Aprendizado de Máquina, Engenharia de Software, Armazém de Dados*).
   - Extração e unificação do conteúdo das 5 páginas em um corpus único.
   - Pré-processamento e limpeza de texto: conversão para minúsculas, remoção de pontuação e filtragem de stopwords em português com `nltk.corpus.stopwords`.
   - Campo para o usuário buscar uma palavra específica e exibição da **contagem exata de ocorrências**, frequência relativa e snippets de contexto no texto consolidado.

---

## 📂 Arquitetura do Projeto

```
projeto-scraping-ufrn/
│
├── app.py                 # Aplicação principal Streamlit com 5 abas interativas
├── scraper_bs4.py         # Módulo de raspagem via Requests + BeautifulSoup4
├── scraper_scrapy.py      # Módulo de raspagem via Scrapy + Crochet
├── utils.py               # Utilitários de NLP (NLTK), WordCloud e métricas estatísticas
├── test_scrapers.py       # Script de testes automatizados de validação
├── notebook_colab.ipynb   # Notebook configurado para execução no Google Colab
├── requirements.txt       # Lista de dependências do Python
└── README.md              # Documentação completa e instruções de entrega
```

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
- Python 3.10, 3.11 ou 3.12 instalado.

### 2. Clonar ou Acessar a Pasta do Projeto
```bash
git clone <url-do-repositorio>
cd "Data App"
```

### 3. Criar e Ativar o Ambiente Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate   # No Linux/macOS
# .venv\Scripts\activate    # No Windows
```

### 4. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 5. Executar os Testes Automatizados
```bash
python test_scrapers.py
```

### 6. Iniciar o Data App Streamlit
```bash
streamlit run app.py
```
Acesse a aplicação no navegador em: `http://localhost:8501`.

---

## ☁️ Como Executar no Google Colab

Você pode executar o projeto diretamente no Google Colab utilizando o notebook incluído:

1. Abra o [Google Colab](https://colab.research.google.com/).
2. Faça o upload do arquivo [`notebook_colab.ipynb`](file:///home/cleiton/Área%20de%20trabalho/Codes/Data%20App/notebook_colab.ipynb).
3. Execute as células em sequência para testar o scraping BS4, Scrapy com `crochet` e a raspagem múltipla dos 5 termos.
4. Para abrir a interface web Streamlit no Colab, execute a célula com `localtunnel` conforme demonstrado no notebook.

## 📊 Comparativo Técnico: Requests+BS4 vs Scrapy+Crochet

| Critério | Requests + BeautifulSoup4 | Scrapy + Crochet |
| :--- | :--- | :--- |
| **Paradigma** | Síncrono / I/O Bloqueante | Assíncrono / Orientado a Eventos (Twisted) |
| **Complexidade de Código** | Simples e direto (`requests.get` + `soup.find_all`) | Requer definição de Spider, Runner e Crochet |
| **Desempenho em 1 Página** | Mais rápido para páginas isoladas (sem overhead de engine) | Overhead de inicialização do Twisted Reactor |
| **Escalabilidade** | Limitado para milhares de páginas simultâneas | Excelente para crawling massivo, paginação e pipelines |
| **Ambientes Interativos** | Funciona nativamente em qualquer thread | Requer `crochet.setup()` e `@wait_for` em Jupyter/Streamlit |

---

## 👨‍💻 Autor & Metadados
- **Instituição:** Universidade Federal do Rio Grande do Norte (UFRN)
- **Tecnologias:** Python, Streamlit, Scrapy, Twisted, Crochet, BeautifulSoup4, NLTK, WordCloud, Plotly.

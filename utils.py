"""
Utilitários de processamento de dados, métricas estatísticas e gráficos para o Data App UFRN/EAJ.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Tuple, Optional


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula os principais KPIs e métricas do conjunto de notícias.
    """
    if df.empty or "ano" not in df.columns:
        return {
            "total_noticias": 0,
            "periodo": "N/D",
            "ano_pico": "N/D",
            "qtd_ano_pico": 0,
            "media_anual": 0.0,
            "total_anos": 0
        }
        
    df_valid = df.dropna(subset=["ano"]).copy()
    df_valid["ano"] = df_valid["ano"].astype(int)
    
    total = len(df_valid)
    if total == 0:
        return {
            "total_noticias": 0,
            "periodo": "N/D",
            "ano_pico": "N/D",
            "qtd_ano_pico": 0,
            "media_anual": 0.0,
            "total_anos": 0
        }
        
    min_year = int(df_valid["ano"].min())
    max_year = int(df_valid["ano"].max())
    
    counts_by_year = df_valid["ano"].value_counts().sort_index()
    ano_pico = int(counts_by_year.idxmax())
    qtd_ano_pico = int(counts_by_year.max())
    total_anos = len(counts_by_year)
    media_anual = round(total / total_anos, 1) if total_anos > 0 else 0.0
    
    return {
        "total_noticias": total,
        "periodo": f"{min_year} – {max_year}",
        "min_year": min_year,
        "max_year": max_year,
        "ano_pico": ano_pico,
        "qtd_ano_pico": qtd_ano_pico,
        "media_anual": media_anual,
        "total_anos": total_anos
    }


def get_yearly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna a tabela agregada de contagem de notícias por ano, ordenada cronologicamente.
    """
    if df.empty or "ano" not in df.columns:
        return pd.DataFrame(columns=["Ano", "Quantidade"])
        
    df_valid = df.dropna(subset=["ano"]).copy()
    df_valid["Ano"] = df_valid["ano"].astype(int)
    
    dist = df_valid["Ano"].value_counts().reset_index()
    dist.columns = ["Ano", "Quantidade"]
    dist = dist.sort_values(by="Ano", ascending=True).reset_index(drop=True)
    dist["Ano_Str"] = dist["Ano"].astype(str)
    return dist


def create_plotly_bar_chart(dist_df: pd.DataFrame) -> go.Figure:
    """
    Gera um gráfico interativo de barras de alta qualidade com Plotly.
    """
    if dist_df.empty:
        fig = go.Figure()
        fig.update_layout(title="Nenhum dado disponível")
        return fig
        
    max_qtd = dist_df["Quantidade"].max()
    
    # Cores personalizadas: destaque para o ano de maior publicação
    colors = [
        "#00d2ff" if q == max_qtd else "#3a7bd5" 
        for q in dist_df["Quantidade"]
    ]
    
    fig = go.Figure(
        data=[
            go.Bar(
                x=dist_df["Ano_Str"],
                y=dist_df["Quantidade"],
                text=dist_df["Quantidade"],
                textposition="outside",
                textfont=dict(size=14, color="#ffffff", family="Inter, sans-serif"),
                marker=dict(
                    color=colors,
                    line=dict(color="#ffffff", width=1.2),
                    opacity=0.9
                ),
                hovertemplate="<b>Ano:</b> %{x}<br><b>Notícias publicadas:</b> %{y}<extra></extra>"
            )
        ]
    )
    
    # Linha de tendência média
    media = dist_df["Quantidade"].mean()
    fig.add_hline(
        y=media,
        line_dash="dot",
        line_color="#ff9900",
        annotation_text=f"Média Anual: {media:.1f}",
        annotation_position="top left",
        annotation_font_color="#ff9900"
    )
    
    fig.update_layout(
        title=dict(
            text="📊 Publicações de Notícias Citando a EAJ por Ano",
            font=dict(size=20, color="#ffffff", family="Inter, sans-serif")
        ),
        xaxis=dict(
            title=dict(text="Ano de Publicação", font=dict(size=14, color="#e0e0e0")),
            type="category",
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=12, color="#ffffff")
        ),
        yaxis=dict(
            title=dict(text="Quantidade de Notícias", font=dict(size=14, color="#e0e0e0")),
            gridcolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(size=12, color="#ffffff")
        ),
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        paper_bgcolor="rgba(15, 23, 42, 0.8)",
        margin=dict(l=40, r=40, t=60, b=40),
        height=450
    )
    
    return fig


def create_plotly_pie_chart(dist_df: pd.DataFrame) -> go.Figure:
    """
    Gera um gráfico de pizza/donut para distribuição percentual por ano.
    """
    if dist_df.empty:
        fig = go.Figure()
        return fig
        
    fig = px.pie(
        dist_df,
        names="Ano_Str",
        values="Quantidade",
        title="🥧 Proporção de Notícias por Ano (EAJ)",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#1e293b", width=1.5))
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        paper_bgcolor="rgba(15, 23, 42, 0.8)",
        font=dict(color="#ffffff", family="Inter, sans-serif"),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig

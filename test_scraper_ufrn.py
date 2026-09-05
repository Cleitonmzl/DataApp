"""
Script de testes automatizados para validar a integridade do Web Scraping e geração dos arquivos.
"""

import os
import unittest
import pandas as pd
import scraper_ufrn
import utils


class TestScraperUFRN(unittest.TestCase):
    
    def test_01_scraping_sample(self):
        """Valida se o scraper consegue coletar notícias da UFRN com a keyword EAJ."""
        news = scraper_ufrn.fetch_eaj_news(keyword="EAJ", max_pages=1, per_page=10)
        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0, "Deveria retornar ao menos 1 notícia")
        
        first_item = news[0]
        self.assertIn("ano", first_item)
        self.assertIn("url", first_item)
        self.assertIn("titulo", first_item)
        self.assertIsNotNone(first_item["ano"])
        self.assertTrue(first_item["url"].startswith("https://www.ufrn.br/imprensa/noticias/"))
        
    def test_02_save_and_load_txt(self):
        """Valida a persistência e carregamento do arquivo TXT (Requisito 1)."""
        sample_news = [
            {"ano": 2026, "url": "https://www.ufrn.br/imprensa/noticias/123/teste-1", "titulo": "Notícia Teste 1"},
            {"ano": 2025, "url": "https://www.ufrn.br/imprensa/noticias/124/teste-2", "titulo": "Notícia Teste 2"}
        ]
        test_file = "test_noticias_temp.txt"
        scraper_ufrn.save_to_txt(sample_news, test_file)
        self.assertTrue(os.path.exists(test_file))
        
        loaded = scraper_ufrn.load_news_from_txt(test_file)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["ano"], 2026)
        self.assertEqual(loaded[0]["url"], "https://www.ufrn.br/imprensa/noticias/123/teste-1")
        
        if os.path.exists(test_file):
            os.remove(test_file)
            
    def test_03_utils_kpis(self):
        """Valida o cálculo de KPIs e métricas."""
        df = pd.DataFrame([
            {"ano": 2024, "url": "http://a", "titulo": "a"},
            {"ano": 2024, "url": "http://b", "titulo": "b"},
            {"ano": 2025, "url": "http://c", "titulo": "c"},
            {"ano": 2026, "url": "http://d", "titulo": "d"}
        ])
        kpis = utils.calculate_kpis(df)
        self.assertEqual(kpis["total_noticias"], 4)
        self.assertEqual(kpis["ano_pico"], 2024)
        self.assertEqual(kpis["qtd_ano_pico"], 2)
        self.assertEqual(kpis["total_anos"], 3)
        
    def test_04_utils_distribution(self):
        """Valida a geração da distribuição por ano para o st.bar_chart."""
        df = pd.DataFrame([
            {"ano": 2024, "url": "http://a", "titulo": "a"},
            {"ano": 2024, "url": "http://b", "titulo": "b"},
            {"ano": 2025, "url": "http://c", "titulo": "c"},
        ])
        dist = utils.get_yearly_distribution(df)
        self.assertEqual(len(dist), 2)
        self.assertIn("Ano", dist.columns)
        self.assertIn("Quantidade", dist.columns)
        
        # Testar criação do gráfico Plotly
        fig = utils.create_plotly_bar_chart(dist)
        self.assertIsNotNone(fig)


if __name__ == "__main__":
    unittest.main()

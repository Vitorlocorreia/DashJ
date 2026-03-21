from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

load_dotenv()
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_db']

def migrate():
    # Ler o arquivo HTML legado
    html_path = r'd:\DashJ\static\reports\relatorio_rcgoleiros.html'
    if not os.path.exists(html_path):
        print("Arquivo HTML não encontrado.")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tentar extrair o logotipo (base64)
    # No HTML vimos que o logo está em uma tag <img> dentro de <div class="logo-box">
    # Vou pegar o primeiro Base64 que encontrar que pareça ser o logo
    logo_match = re.search(r'src="data:image/png;base64,([^"]+)"', content)
    logo_base64 = logo_match.group(1) if logo_match else ""

    cliente_data = {
        "login": "rcgoleiros",
        "nome_empresa": "RC Goleiros",
        "subtitulo": "Escola de Goleiros",
        "logo_base64": logo_base64,
        "dados": {
            "mes_referencia": "Fevereiro/2025",
            "kpi_alcance_total": "0",
            "kpi_visitas": "0",
            "kpi_novos_seg": "0",
            "kpi_base_atual": "0",
            "chart_reels": 0,
            "chart_stories": 0,
            "chart_posts": 0,
            "aud_seguidores": 0,
            "aud_nao_seguidores": 0,
            "insight_texto": "Direcionamento estratégico em breve."
        }
    }

    # Inserir ou atualizar no MongoDB
    db.clientes.update_one(
        {"login": "rcgoleiros"},
        {"$set": cliente_data},
        upsert=True
    )
    print("Migração do RC Goleiros concluída com sucesso!")

if __name__ == "__main__":
    migrate()

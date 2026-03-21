import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_jota']
collection = db['clientes']

rcgoleiros_data = {
    "client_id": "rcgoleiros",
    "dados": {
        "mes_referencia": "Fevereiro 2026",
        "kpi_alcance_total": "3.2M",
        "kpi_visitas": "8.5k",
        "kpi_novos_seg": "+568",
        "kpi_base_atual": "118k",
        "chart_reels": 55.3,
        "chart_stories": 40.8,
        "chart_posts": 3.9,
        "aud_nao_seguidores": 76.5,
        "aud_seguidores": 23.5,
        "eng_curtidas": "85.5k",
        "eng_comentarios": "1.8k",
        "eng_compartilhamentos": "13.7k",
        "eng_reposts": "1.9k",
        "insight_texto": "Formatos como <strong>“REACT com Rodrigo”</strong> e <strong>“Memes de Goleiros”</strong> estão dominando o alcance e engajamento. Refinaremos esses modelos para aumentar autoridade e colocar em prática o planejamento estratégico para expansão de vizualizações e retenção da base massiva de <strong>118k seguidores</strong>."
    }
}

# Update or insert
result = collection.update_one(
    {"client_id": "rcgoleiros"},
    {"$set": rcgoleiros_data},
    upsert=True
)

print("Dados do RC Goleiros inseridos/atualizados no MongoDB Atlas com sucesso!")

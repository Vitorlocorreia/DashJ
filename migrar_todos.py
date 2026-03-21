import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['dashboard_db']
collection = db['clientes']

def extract_base64(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract logo (usually the first img base64 in header)
    # Looking for: <img src="data:image/png;base64,iVBOR..." alt="Grupo Jota Logo">
    logo_match = re.search(r'alt="Grupo Jota Logo".*?src="data:image/[^;]+;base64,([^"]+)"', content, re.DOTALL)
    if not logo_match:
        # try the other way
        logo_match = re.search(r'src="data:image/[^;]+;base64,([^"]+)".*?alt="Grupo Jota Logo"', content, re.DOTALL)
    
    # Extract avatar (in client-avatar div)
    avatar_match = re.search(r'<div class="client-avatar">.*?src="data:image/[^;]+;base64,([^"]+)"', content, re.DOTALL)
    
    logo = logo_match.group(1) if logo_match else ""
    avatar = avatar_match.group(1) if avatar_match else ""
    
    return logo, avatar

clients_config = [
    {
        "login": "mateus",
        "nome": "Mateus Saka",
        "subtitulo": "Mateus Saka • Cliente Premium",
        "file": "static/reports/relatorio_Matheus_Saka.html"
    },
    {
        "login": "basebjj",
        "nome": "BASE BJJ PE",
        "subtitulo": "BASE BJJ • Jiu-Jitsu",
        "file": "static/reports/relatorio_basebjj.html"
    },
    {
        "login": "futtime",
        "nome": "FUTTIME",
        "subtitulo": "FUTTIME • Escola de Futevôlei",
        "file": "static/reports/relatoriofuttime.html"
    }
]

for c in clients_config:
    print(f"Processando {c['nome']}...")
    try:
        logo, avatar = extract_base64(c['file'])
        
        doc = {
            "login": c['login'],
            "nome_empresa": c['nome'],
            "subtitulo": c['subtitulo'],
            "logo_base64": logo,
            "avatar_base64": avatar,
            "cor_primaria": "#1a1a1a", # default initial
            "configuracoes": {
                "show_metrics": True
            }
        }
        
        collection.update_one({"login": c['login']}, {"$set": doc}, upsert=True)
        print(f"Sucesso: {c['login']} migrado.")
    except Exception as e:
        print(f"Erro ao processar {c['login']}: {e}")

print("Migração concluída.")

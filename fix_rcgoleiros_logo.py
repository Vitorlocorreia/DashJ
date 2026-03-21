from pymongo import MongoClient
import os
from dotenv import load_dotenv
import re

load_dotenv()
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_db']

def fix_logo():
    # Ler o arquivo HTML legado
    html_path = r'd:\DashJ\static\reports\relatorio_rcgoleiros.html'
    if not os.path.exists(html_path):
        print("Arquivo HTML não encontrado.")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Procurar o logo na div client-avatar
    # <div class="client-avatar">\s*<img src="data:image/png;base64,([^"]+)"
    avatar_match = re.search(r'<div class="client-avatar">\s*<img src="data:image/png;base64,([^"]+)"', content, re.DOTALL)
    
    if avatar_match:
        logo_base64 = avatar_match.group(1)
        db.clientes.update_one(
            {"login": "rcgoleiros"},
            {"$set": {"logo_base64": logo_base64}}
        )
        print("Logotipo do RC Goleiros atualizado com sucesso!")
    else:
        print("Logotipo não encontrado no local esperado.")

if __name__ == "__main__":
    fix_logo()

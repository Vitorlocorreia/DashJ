from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_db']

def fix_avatar():
    # Pegar o logo atual e usar como avatar também
    cliente = db.clientes.find_one({"login": "rcgoleiros"})
    if cliente and "logo_base64" in cliente:
        db.clientes.update_one(
            {"login": "rcgoleiros"},
            {"$set": {"avatar_base64": cliente["logo_base64"]}}
        )
        print("Avatar do RC Goleiros atualizado com sucesso!")
    else:
        print("Cliente ou logotipo não encontrado.")

if __name__ == "__main__":
    fix_avatar()

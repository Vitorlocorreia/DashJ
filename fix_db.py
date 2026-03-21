from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_db']

# Garante que todos os documentos tenham o campo 'dados' se não existir
result = db.clientes.update_many(
    {"dados": {"$exists": False}},
    {"$set": {"dados": {}}}
)

print(f"Número de documentos atualizados: {result.modified_count}")

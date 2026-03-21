from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_db']

def migrate_to_history():
    # 1. Pegar todos os clientes
    clientes = list(db.clientes.find())
    
    for c in clientes:
        login = c.get('login')
        dados = c.get('dados')
        
        if dados and 'mes_referencia' in dados:
            mes = dados['mes_referencia']
            
            # 2. Criar ou atualizar registro na coleção 'metricas'
            # Usando login + mes_referencia como chave única
            db.metricas.update_one(
                {"login": login, "mes_referencia": mes},
                {"$set": dados},
                upsert=True
            )
            print(f"Migrado histórico de {login} para {mes}")
            
            # 3. Remover 'dados' do documento principal do cliente para manter limpo
            # (Opcional, mas recomendado para evitar ambiguidade)
            # db.clientes.update_one({"_id": c["_id"]}, {"$unset": {"dados": ""}})
    
    print("Migração concluída com sucesso!")

if __name__ == "__main__":
    migrate_to_history()

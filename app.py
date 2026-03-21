import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_jota']


app = Flask(__name__)
# Chave secreta via variável de ambiente para produção no Vercel
app.secret_key = os.environ.get('SECRET_KEY', 'grupo_jota_secret_default_12345')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Serve arquivos da pasta public/ (Vercel faz isso automaticamente; Flask precisa de rota)
@app.route('/public/<path:filename>')
def public_files(filename):
    return send_from_directory('public', filename)

def load_users():
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)['clientes']

@app.route('/')
def index():
    # Se o usuário acessar a raiz e não estiver logado, garante que vá para o login
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_users()
        user = next((u for u in users if u['login'] == username and u['senha'] == password), None)
        
        if user:
            session.clear() 
            session.permanent = False # Garante que a sessão expire ao fechar o navegador
            session['username'] = user['login']
            session['relatorio'] = user['relatorio_file']
            session['nome'] = user['nome']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Login ou senha incorretos.')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Se o cliente já tiver um template pronto na pasta templates, injetamos pelo Jinja2
    # Por enquanto apenas rcgoleiros
    if session['username'] == 'rcgoleiros':
        client_data = db.clientes.find_one({"client_id": session['username']})
        dados = client_data.get('dados', {}) if client_data else {}
        return render_template(session['relatorio'], dados=dados)
    else:
        # Fallback para relatórios ainda estáticos
        return send_from_directory('static/reports', session['relatorio'])

@app.route('/editar-dashboard', methods=['GET', 'POST'])
def editar_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    client_id = session['username']
    
    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        # Casting the chart data to floats because Chart.js expects numbers
        try:
            form_data['chart_reels'] = float(form_data.get('chart_reels', 0))
            form_data['chart_stories'] = float(form_data.get('chart_stories', 0))
            form_data['chart_posts'] = float(form_data.get('chart_posts', 0))
            form_data['aud_nao_seguidores'] = float(form_data.get('aud_nao_seguidores', 0))
            form_data['aud_seguidores'] = float(form_data.get('aud_seguidores', 0))
        except ValueError:
            pass # se der erro, deixa como string mesmo ou trata
            
        db.clientes.update_one(
            {"client_id": client_id},
            {"$set": {"dados": form_data}},
            upsert=True
        )
        return redirect(url_for('dashboard'))
    
    client_data = db.clientes.find_one({"client_id": client_id})
    dados = client_data.get('dados', {}) if client_data else {}
    
    return render_template('editar.html', dados=dados)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

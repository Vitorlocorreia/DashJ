import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

app = Flask(__name__)
# Chave secreta via variável de ambiente para produção no Vercel
app.secret_key = os.environ.get('SECRET_KEY', 'grupo_jota_secret_default_12345')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

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
    
    # Servir o arquivo HTML estático do cliente da pasta static/reports
    return send_from_directory('static/reports', session['relatorio'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'grupo_jota_secret_key' # Em produção, use uma chave segura

def load_users():
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)['clientes']

@app.route('/')
def index():
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
    
    # Servir o arquivo HTML estático do cliente
    # Nota: Em um sistema final, o dashboard seria um template dinâmico único
    # Mas para rapidez, serviremos os arquivos que o usuário já tem.
    return send_from_directory('.', session['relatorio'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Usar porta 5000 como padrão
    app.run(debug=True, port=5000)

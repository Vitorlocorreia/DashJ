import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['dashboard_db']

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'grupo_jota_secret_default_12345')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

@app.route('/public/<path:filename>')
def public_files(filename):
    return send_from_directory('public', filename)

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
            session.clear() 
            session.permanent = False 
            session['username'] = user['login']
            session['nome'] = user['nome']
            session['role'] = user.get('role', 'cliente')
            
            if session['role'] == 'admin':
                return redirect(url_for('admin_panel'))
                
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Login ou senha incorretos.')
            
    return render_template('login.html')

@app.route('/dashboard')
@app.route('/dashboard/<target_login>')
def dashboard(target_login=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    login_vinculado = target_login if (session.get('role') == 'admin' and target_login) else session['username']
    
    # 1. Busca info fixa do cliente
    cliente_config = db.clientes.find_one({"login": login_vinculado})
    if not cliente_config:
        return f"Configuração do cliente '{login_vinculado}' não encontrada.", 404

    # 2. Busca métricas do mês solicitado ou o mais recente da nova coleção
    mes_selecionado = request.args.get('mes')
    if mes_selecionado:
        dados = db.metricas.find_one({"login": login_vinculado, "mes_referencia": mes_selecionado})
    else:
        dados = db.metricas.find_one({"login": login_vinculado}, sort=[("mes_referencia", -1)])
    
    if not dados:
        dados = {"mes_referencia": "Sem dados"}
        
    # 3. Lista histórico para o seletor
    historico_db = list(db.metricas.find({"login": login_vinculado}, {"mes_referencia": 1}).sort("mes_referencia", -1))
    meses_disponiveis = [h['mes_referencia'] for h in historico_db]

    # Previne erros no template
    campos_formatacao = {
        'kpi_alcance_total': '---', 'kpi_visitas': '---', 
        'kpi_novos_seg': '---', 'kpi_base_atual': '---',
        'mes_referencia': '---',
        'chart_reels': 0, 'chart_stories': 0, 'chart_posts': 0,
        'aud_nao_seguidores': 0, 'aud_seguidores': 0,
        'eng_curtidas': '0', 'eng_comentarios': '0', 
        'eng_compartilhamentos': '0', 'eng_reposts': '0',
        'insight_texto': 'Direcionamento estratégico não cadastrado para este mês.'
    }
    for campo, default in campos_formatacao.items():
        if campo not in dados:
            dados[campo] = default

    # 4. Dados para o gráfico de tendência (últimos 6 meses)
    tendencia_db = list(db.metricas.find({"login": login_vinculado}, {"mes_referencia": 1, "kpi_alcance_total": 1}).sort("_id", 1).limit(6))
    
    eixo_x = [t['mes_referencia'] for t in tendencia_db]
    eixo_y = []
    for t in tendencia_db:
        try:
            # Tenta converter o alcance para número para o gráfico
            val = str(t.get('kpi_alcance_total', '0')).replace('.', '').replace(',', '').replace(' ', '')
            eixo_y.append(int(val))
        except:
            eixo_y.append(0)

    return render_template('relatorio_padrao.html', 
                          cliente=cliente_config, 
                          dados=dados, 
                          meses_disponiveis=meses_disponiveis,
                          eixo_x=eixo_x,
                          eixo_y=eixo_y)

@app.route('/admin')
def admin_panel():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    clientes = list(db.clientes.find({}, {"logo_base64": 0, "avatar_base64": 0}))
    return render_template('admin.html', clientes=clientes)

@app.route('/admin/editar/<target_login>', methods=['GET', 'POST'])
def editar_cliente(target_login):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        # Converte campos numéricos
        numeric_fields = ['chart_reels', 'chart_stories', 'chart_posts', 'aud_nao_seguidores', 'aud_seguidores']
        for field in numeric_fields:
            if field in form_data:
                try:
                    form_data[field] = float(form_data.get(field, 0))
                except ValueError:
                    form_data[field] = 0
            
        # Salva na coleção de métricas separada (Historificando por Mês de Referência)
        mes_ref = form_data.get('mes_referencia')
        if mes_ref:
            db.metricas.update_one(
                {"login": target_login, "mes_referencia": mes_ref},
                {"$set": form_data},
                upsert=True
            )
        
        # Atualiza info fixa do cliente
        update_cliente = {}
        if 'nome_empresa' in form_data: update_cliente["nome_empresa"] = form_data.get('nome_empresa')
        if 'subtitulo' in form_data: update_cliente["subtitulo"] = form_data.get('subtitulo')
        if form_data.get('logo_base64'): update_cliente['logo_base64'] = form_data.get('logo_base64')
            
        if update_cliente:
            db.clientes.update_one({"login": target_login}, {"$set": update_cliente})
            
        return redirect(url_for('editar_cliente', target_login=target_login, mes=mes_ref, success=1))
    
    # GET: Busca info fixa e dados do mês solicitado
    cliente_config = db.clientes.find_one({"login": target_login})
    if not cliente_config:
        return "Cliente não encontrado.", 404
        
    mes_editor = request.args.get('mes')
    if mes_editor:
        metrics_data = db.metricas.find_one({"login": target_login, "mes_referencia": mes_editor}) or {}
    else:
        metrics_data = db.metricas.find_one({"login": target_login}, sort=[("mes_referencia", -1)]) or {}
    
    historico = list(db.metricas.find({"login": target_login}, {"mes_referencia": 1}).sort("mes_referencia", -1))
    meses_disponiveis = [h['mes_referencia'] for h in historico]
        
    return render_template('editar.html', 
                          cliente=cliente_config, 
                          dados=metrics_data, 
                          meses_disponiveis=meses_disponiveis, 
                          success=request.args.get('success'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

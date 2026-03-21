import re
import os

template_path = r'd:\DashJ\templates\relatorio_padrao.html'

if not os.path.exists(template_path):
    print(f"Erro: {template_path} não encontrado.")
    exit(1)

with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Substituir o logo (primeiro base64 encontrado)
# Procuramos por src="data:image/png;base64,... seguido de alt="Grupo Jota Logo"
new_content = re.sub(
    r'src="data:image/png;base64,[^"]+"(\s+alt="Grupo Jota Logo")',
    r'src="data:image/png;base64,{{ cliente.logo_base64 }}"\1',
    content,
    count=1
)

# 2. Substituir o avatar (segundo base64 significativo)
# Ele vem depois de <div class="client-avatar">
new_content = re.sub(
    r'(<div class="client-avatar">\s+<img src=")data:image/png;base64,[^"]+"',
    r'\1data:image/png;base64,{{ cliente.avatar_base64 }}"',
    new_content,
    count=1
)

# 3. Substituir nomes e textos fixos
new_content = new_content.replace('<h1>Grupo Jota</h1>', '<h1>{{ cliente.nome_empresa }}</h1>')
new_content = new_content.replace('<p>RC GOLEIROS • Escola de Goleiros</p>', '<p>{{ cliente.subtitulo }}</p>')
new_content = new_content.replace('<span class="client-name">RC GOLEIROS</span>', '<span class="client-name">{{ cliente.nome_empresa }}</span>')

# 4. Ajustar o status para capturar do dicionário de dados ou do cliente
new_content = new_content.replace('<span class="client-status">Relatório de Março/2026</span>', '<span class="client-status">{{ dados.mes_referencia }}</span>')

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Template atualizado com sucesso para modo dinâmico.")

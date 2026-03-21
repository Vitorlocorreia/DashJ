import os
import re

template_path = r'd:\DashJ\templates\relatorio_padrao.html'

if not os.path.exists(template_path):
    print("Erro: Arquivo não encontrado.")
    exit(1)

with open(template_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    # Localiza o botão de editar dashboard (usando o link como referência)
    if 'href="/editar-dashboard"' in line:
        # Substitui o botão por uma versão condicional e aponta para a nova rota de edição
        # O botão original parece ser algo como:
        # <a href="/editar-dashboard" class="logout-btn" title="Editar Dashboard"><i class="ph-bold ph-pencil-simple"></i></a>
        new_line = line.replace('href="/editar-dashboard"', 'href="/admin/editar/{{ cliente.login }}"')
        new_lines.append('            {% if session.role == "admin" %}\n')
        new_lines.append(new_line)
        new_lines.append('            {% endif %}\n')
    else:
        new_lines.append(line)

with open(template_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Botão de edição ocultado para clientes comuns com sucesso.")

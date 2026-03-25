from flask import Flask, render_template, request, redirect, url_for
from models import db, Beneficiario, Doacao
from datetime import datetime

app = Flask(__name__)

# 1. CONFIGURAÇÃO DO BANCO DE DADOS
# O arquivo 'paroquia.db' será criado automaticamente na pasta do projeto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paroquia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco de dados com as configurações do app
db.init_app(app)

# 2. CRIAÇÃO DAS TABELAS
# Esse comando lê o seu arquivo models.py e cria as tabelas no SQLITE
with app.app_context():
    db.create_all()

# --- ROTA 1: PÁGINA INICIAL (ESTOQUE) ---
@app.route('/')
def index():
    # Buscamos todas as movimentações para calcular o saldo
    todas_doacoes = Doacao.query.all()
    
    # Lógica para somar Entradas e subtrair Saídas por item
    estoque = {}
    for d in todas_doacoes:
        item_nome = d.item.upper() # Padroniza para maiúsculas
        if item_nome not in estoque:
            estoque[item_nome] = 0
        
        if d.tipo == 'ENTRADA':
            estoque[item_nome] += d.quantidade
        else:
            estoque[item_nome] -= d.quantidade
            
    return render_template('index.html', estoque=estoque)

# --- ROTA 2: REGISTRAR ENTRADA/SAÍDA DE ALIMENTOS ---
@app.route('/registrar', methods=['POST'])
def registrar():
    # Captura os dados vindos do formulário do index.html
    nova_movimentacao = Doacao(
        item=request.form['item'].upper(),
        quantidade=int(request.form['quantidade']),
        tipo=request.form['tipo'], # Recebe 'ENTRADA' ou 'SAIDA'
        responsavel=request.form['responsavel'],
        data=datetime.now()
    )
    db.session.add(nova_movimentacao)
    db.session.commit()
    return redirect(url_for('index'))

# --- ROTA 3: PÁGINA DE BENEFICIÁRIOS (LISTAR E CADASTRAR) ---
@app.route('/beneficiarios/', methods=['GET', 'POST']) # Adicionei uma / no final
def beneficiarios():
    if request.method == 'POST':
        # Se o usuário preencheu o formulário de pessoas:
        novo_b = Beneficiario(
            nome=request.form['nome'],
            telefone=request.form['telefone'],
            endereco=request.form['endereco']
        )
        db.session.add(novo_b)
        db.session.commit()
        return redirect(url_for('beneficiarios'))

    # Se for apenas acessando a página, mostra a lista de quem já existe
    lista_familias = Beneficiario.query.all()
    return render_template('beneficiarios.html', beneficiarios=lista_familias)
# --- EXECUÇÃO DO PROJETO ---
if __name__ == '__main__':
    # Esta linha liga o servidor e o mantém rodando
    app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for
from models import db, Beneficiario, Doacao
from datetime import datetime
import os

app = Flask(__name__)

# 1. CONFIGURAÇÃO DO BANCO DE DADOS
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paroquia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 2. CRIAÇÃO DAS TABELAS
with app.app_context():
    db.create_all()

# --- ROTA 1: PÁGINA INICIAL (ESTOQUE + DASHBOARD) ---
@app.route('/')
def index():
    # Busca todas as movimentações
    todas_movimentacoes = Doacao.query.order_by(Doacao.data.desc()).all()
    
    # Lógica para calcular o saldo atual por item
    estoque = {}
    for d in todas_movimentacoes:
        item_nome = d.item.upper()
        if item_nome not in estoque:
            estoque[item_nome] = 0
        
        if d.tipo == 'ENTRADA':
            estoque[item_nome] += d.quantidade
        else:
            estoque[item_nome] -= d.quantidade
            
    # --- DADOS PARA O DASHBOARD (CONTROLE) ---
    total_familias = Beneficiario.query.count()
    total_itens_estoque = len(estoque) # Tipos de produtos diferentes
    
    # Conta movimentações feitas hoje (comparando apenas a data, sem a hora)
    hoje = Doacao.query.filter(db.func.date(Doacao.data) == datetime.now().date()).count()

    return render_template('index.html', 
                           estoque=estoque, 
                           movimentacoes=todas_movimentacoes,
                           total_familias=total_familias,
                           total_itens=total_itens_estoque,
                           hoje=hoje)

# --- ROTA 2: REGISTRAR ENTRADA/SAÍDA ---
@app.route('/registrar', methods=['POST'])
def registrar():
    nova_movimentacao = Doacao(
        item=request.form['item'].upper(),
        quantidade=int(request.form['quantidade']),
        tipo=request.form['tipo'],
        responsavel=request.form['responsavel'],
        data=datetime.now()
    )
    db.session.add(nova_movimentacao)
    db.session.commit()
    return redirect(url_for('index'))

# --- ROTA: EXCLUIR MOVIMENTAÇÃO ---
@app.route('/excluir_movimentacao/<int:id>')
def excluir_movimentacao(id):
    mov = Doacao.query.get(id)
    if mov:
        db.session.delete(mov)
        db.session.commit()
    return redirect(url_for('index'))

# --- ROTA 3: PÁGINA DE BENEFICIÁRIOS ---
@app.route('/beneficiarios/', methods=['GET', 'POST'])
def beneficiarios():
    if request.method == 'POST':
        novo_b = Beneficiario(
            nome=request.form['nome'],
            telefone=request.form['telefone'],
            endereco=request.form['endereco'],
            categoria=request.form['categoria']
        )
        db.session.add(novo_b)
        db.session.commit()
        return redirect(url_for('beneficiarios'))

    lista_familias = Beneficiario.query.all()
    return render_template('beneficiarios.html', beneficiarios=lista_familias)

# --- ROTA 4: EXCLUIR BENEFICIÁRIO ---
@app.route('/excluir_beneficiario/<int:id>')
def excluir_beneficiario(id):
    beneficiario_para_excluir = Beneficiario.query.get(id)
    if beneficiario_para_excluir:
        db.session.delete(beneficiario_para_excluir)
        db.session.commit()
    return redirect(url_for('beneficiarios'))

# --- CONFIGURAÇÃO PARA O DEPLOY (RENDER) ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
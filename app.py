from flask import Flask, render_template, request, redirect, url_for, Response, flash
from models import db, Beneficiario, Doacao
from datetime import datetime
import os
import csv
import io

app = Flask(__name__)

# --- CONFIGURAÇÕES DO SISTEMA ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paroquia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Secret Key: Necessária para que o sistema possa exibir mensagens de alerta (Flash Messages)
app.secret_key = 'santuario_sao_jose_secret'

db.init_app(app)

# Cria as tabelas no banco de dados caso elas não existam ao iniciar o app
with app.app_context():
    db.create_all()

# --- ROTA 1: PAINEL PRINCIPAL (TELA DE ESTOQUE) ---
@app.route('/')
def index():
    # Busca todas as movimentações do banco, da mais recente para a mais antiga
    todas_movimentacoes = Doacao.query.order_by(Doacao.data.desc()).all()
    
    # LÓGICA DE CÁLCULO DE SALDO:
    # Percorre todas as doações. Se for 'ENTRADA', somamos. Se for 'SAIDA', subtraímos.
    estoque = {}
    for d in todas_movimentacoes:
        item_nome = d.item.upper()
        if item_nome not in estoque:
            estoque[item_nome] = 0
        
        if d.tipo == 'ENTRADA':
            estoque[item_nome] += d.quantidade
        else:
            estoque[item_nome] -= d.quantidade
            
    # --- LOGICA DO SELECT (DATALIST) ---
    # Pegamos apenas os nomes dos itens que já existem no estoque para sugerir no formulário
    lista_itens_existentes = sorted(estoque.keys())

    # Estatísticas para o Dashboard
    total_familias = Beneficiario.query.count()
    total_itens_estoque = len(estoque) 
    hoje = Doacao.query.filter(db.func.date(Doacao.data) == datetime.now().date()).count()

    return render_template('index.html', 
                           estoque=estoque, 
                           movimentacoes=todas_movimentacoes,
                           total_familias=total_familias,
                           total_itens=total_itens_estoque,
                           hoje=hoje,
                           lista_itens_existentes=lista_itens_existentes) # Enviado para o HTML

# --- ROTA 2: REGISTRO DE MOVIMENTAÇÃO (COM TRAVA DE SEGURANÇA) ---
@app.route('/registrar', methods=['POST'])
def registrar():
    item_nome = request.form['item'].upper().strip()
    quantidade = int(request.form['quantidade'])
    tipo = request.form['tipo']
    responsavel = request.form['responsavel']

    # VERIFICAÇÃO NO CASO DE ESTOQUE NEGATIVO:
    if tipo == 'SAIDA':
        # Calcula o saldo atual do item antes de permitir a saída
        movs = Doacao.query.filter_by(item=item_nome).all()
        saldo_atual = sum(m.quantidade if m.tipo == 'ENTRADA' else -m.quantidade for m in movs)

        if quantidade > saldo_atual:
            # Envia mensagem de erro que aparecerá no index.html
            flash(f'ERRO: Estoque insuficiente de {item_nome}! Você tentou retirar {quantidade}, mas só temos {saldo_atual}.', 'danger')
            return redirect(url_for('index'))

    # Se passar na validação ou for ENTRADA, salva no banco
    nova_movimentacao = Doacao(
        item=item_nome,
        quantidade=quantidade,
        tipo=tipo,
        responsavel=responsavel,
        data=datetime.now()
    )
    db.session.add(nova_movimentacao)
    db.session.commit()
    return redirect(url_for('index'))

# --- ROTA 3: EXPORTAR DADOS (CSV/EXCEL) ---
@app.route('/exportar_csv')
def exportar_csv():
    movimentacoes = Doacao.query.order_by(Doacao.data.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Data', 'Item', 'Quantidade', 'Tipo', 'Responsavel'])
    for m in movimentacoes:
        writer.writerow([m.data.strftime('%d/%m/%Y %H:%M'), m.item, m.quantidade, m.tipo, m.responsavel])
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=relatorio_santuario.csv"})

@app.route('/exportar_beneficiarios_csv')
def exportar_beneficiarios_csv():
    pessoas = Beneficiario.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nome', 'Categoria', 'Telefone', 'Endereco'])
    for p in pessoas:
        writer.writerow([p.nome, p.categoria, p.telefone, p.endereco])
    output.seek(0)
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=contatos_santuario.csv"})

# --- ROTA 4: GESTÃO DE BENEFICIÁRIOS ---
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

# --- ROTAS DE EXCLUSÃO ---
@app.route('/excluir_movimentacao/<int:id>')
def excluir_movimentacao(id):
    mov = Doacao.query.get(id)
    if mov:
        db.session.delete(mov)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/excluir_beneficiario/<int:id>')
def excluir_beneficiario(id):
    b = Beneficiario.query.get(id)
    if b:
        db.session.delete(b)
        db.session.commit()
    return redirect(url_for('beneficiarios'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
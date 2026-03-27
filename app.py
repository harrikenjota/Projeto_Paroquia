from flask import Flask, render_template, request, redirect, url_for, Response, flash
from models import db, Beneficiario, Doacao
from datetime import datetime
import os
import csv
import io

app = Flask(__name__)

# --- 1. CONFIGURAÇÕES DO SISTEMA ---
# Define o banco de dados e a chave de segurança para mensagens de alerta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paroquia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'santuario_sao_jose_secret'

db.init_app(app)

# --- 2. INICIALIZAÇÃO DO BANCO ---
# Cria as tabelas automaticamente se elas ainda não existirem
with app.app_context():
    db.create_all()

# --- 3. ROTA: PAINEL PRINCIPAL (ESTOQUE) ---
@app.route('/')
def index():
    # Busca todas as movimentações e beneficiários no banco
    todas_movimentacoes = Doacao.query.order_by(Doacao.data.desc()).all()
    lista_beneficiarios = Beneficiario.query.order_by(Beneficiario.nome).all()
    
    # Cálculo dinâmico do saldo atual de cada item
    estoque = {}
    for d in todas_movimentacoes:
        item_nome = d.item.upper()
        if item_nome not in estoque:
            estoque[item_nome] = 0
        
        if d.tipo == 'ENTRADA':
            estoque[item_nome] += d.quantidade
        else:
            estoque[item_nome] -= d.quantidade
            
    # Lista de nomes de itens para sugestão no formulário
    lista_itens_existentes = sorted(estoque.keys())

    # KPIs: Indicadores para o topo da página
    total_familias = len(lista_beneficiarios)
    total_itens_estoque = len(estoque) 
    hoje = Doacao.query.filter(db.func.date(Doacao.data) == datetime.now().date()).count()

    return render_template('index.html', 
                           estoque=estoque, 
                           movimentacoes=todas_movimentacoes,
                           total_familias=total_familias,
                           total_itens=total_itens_estoque,
                           hoje=hoje,
                           lista_itens_existentes=lista_itens_existentes,
                           lista_beneficiarios=lista_beneficiarios) # Enviando a lista para o Select

# --- 4. ROTA: DASHBOARD (ESTATÍSTICAS) ---
@app.route('/dashboard')
def dashboard():
    todas_movimentacoes = Doacao.query.all()
    estoque_grafico = {}
    entradas_totais = 0
    saidas_totais = 0
    
    for d in todas_movimentacoes:
        item = d.item.upper()
        if item not in estoque_grafico: 
            estoque_grafico[item] = 0
        
        if d.tipo == 'ENTRADA':
            estoque_grafico[item] += d.quantidade
            entradas_totais += d.quantidade
        else:
            estoque_grafico[item] -= d.quantidade
            saidas_totais += d.quantidade

    labels = [item for item, qtd in estoque_grafico.items() if qtd > 0]
    valores = [qtd for item, qtd in estoque_grafico.items() if qtd > 0]
    
    total_familias = Beneficiario.query.count()
    itens_criticos = sum(1 for qtd in estoque_grafico.values() if 0 < qtd <= 5)

    return render_template('dashboard.html', 
                           labels=labels, valores=valores,
                           entradas=entradas_totais, saidas=saidas_totais,
                           total_familias=total_familias, itens_criticos=itens_criticos)

# --- 5. ROTA: PROCESSAR REGISTRO (VINCULANDO BENEFICIÁRIO) ---
@app.route('/registrar', methods=['POST'])
def registrar():
    item_nome = request.form['item'].upper().strip()
    quantidade = int(request.form['quantidade'])
    tipo = request.form['tipo']
    # Agora o 'responsavel' recebe o nome selecionado no Select do formulário
    responsavel = request.form['responsavel']

    # Validação de estoque para saídas
    if tipo == 'SAIDA':
        movs = Doacao.query.filter_by(item=item_nome).all()
        saldo_atual = sum(m.quantidade if m.tipo == 'ENTRADA' else -m.quantidade for m in movs)

        if quantidade > saldo_atual:
            flash(f'ERRO: Estoque insuficiente de {item_nome}! Saldo atual: {saldo_atual}.', 'danger')
            return redirect(url_for('index'))

    # Salva a nova doação/movimentação no banco
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

# --- 6. ROTAS DE EXPORTAÇÃO (CSV) ---
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

# --- 7. ROTA: GESTÃO DE BENEFICIÁRIOS (CADASTRO) ---
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

# --- 8. ROTAS DE EXCLUSÃO ---
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

# --- 9. EXECUÇÃO DO APP ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
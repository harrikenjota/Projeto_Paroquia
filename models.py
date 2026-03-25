from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Beneficiario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))

class Voluntario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50))

class Doacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    # Adicionamos estas colunas para o app.py não dar erro:
    tipo = db.Column(db.String(10), nullable=False) # 'ENTRADA' ou 'SAIDA'
    responsavel = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    # Mantendo sua referência se precisar:
    voluntario_id = db.Column(db.Integer, db.ForeignKey('voluntario.id'))
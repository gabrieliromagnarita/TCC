from connect import db
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, Flask
import firebase_admin
from firebase_admin import credentials, firestore, auth
#import requests
from collections import Counter

carrinho_bp = Blueprint('carrinho', __name__)
#FIREBASE_API_KEY = 'AIzaSyB83_gLrndTGy1mx5jG8CJEA_LrCsCijdw'

@carrinho_bp.route('/carrinho-render')
def carrinho():
    carrinho_ids = session.get('carrinho', [])
    contagem = Counter(carrinho_ids)
    produtos_carrinho = []
    total = 0.0
    total_itens = 0

    for produto_id, qtd in contagem.items():
        doc = db.collection("produtos").document(produto_id).get()
        if not doc.exists:
            continue
        produto = doc.to_dict()
        produto["id"] = produto_id
        produto["quantidade"] = qtd
        produto["subtotal"] = produto.get("preco", 0) * qtd
        produtos_carrinho.append(produto)
        total += produto["subtotal"]
        total_itens += qtd
    
    return render_template('carrinho.html', produtos=produtos_carrinho, total=total, total_itens=total_itens)

@carrinho_bp.route('/remove_carrinho/<produto_id>', methods=['POST','GET'])
def remove_carrinho(produto_id):
    produto_id = str(produto_id)
    carrinho = session.get('carrinho', [])
    
    if produto_id in carrinho:
        carrinho.remove(produto_id)
        session['carrinho'] = carrinho
    return(redirect(request.referrer or url_for('carrinho.carrinho')))

@carrinho_bp.route('/add_carrinho/<produto_id>')
def add_carrinho(produto_id):
    produto_id = str(produto_id)
    session.setdefault('carrinho',[])
    session['carrinho'].append(produto_id)
    session.modified = True
    return(redirect(request.referrer or url_for('produto.produto', id="produto_id")))

@carrinho_bp.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    carrinho_ids = session.get('carrinho', [])
    if not carrinho_ids:
        return(redirect(url_for('carrinho.carrinho')))
    
    from collections import Counter
    contagem = Counter(carrinho_ids)
    produtos_carrinho = []
    total = 0.0
    total_itens = 0

    for produto_id, qtd in contagem.items():
        doc = db.collection("produtos").document(produto_id).get()
        if not doc.exists:
            continue
        produto = doc.to_dict()
        produto["id"] = produto_id
        produto["quantidade"] = qtd
        produto["subtotal"] = produto.get("preco", 0) * qtd

        produtos_carrinho.append(produto)
        total += produto["subtotal"]

    session['compra'] = {
        'produtos': produtos_carrinho,
        'total': total
    }

    return(redirect(url_for('compra.compra')))
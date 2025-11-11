from connect import db
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, Flask
import firebase_admin
from firebase_admin import credentials, firestore, auth
from collections import Counter

carrinho_bp = Blueprint('carrinho', __name__)

def atualizar_carrinho(user_email, carrinho_atual):
    doc_ref = db.collection("carrinhos").document(user_email)
    doc_ref.set({"produtos": carrinho_atual}, merge=True)

@carrinho_bp.route('/carrinho-render')
def carrinho():
    carrinho_ids = session.get('carrinho', [])
    if not isinstance(carrinho_ids, list):
        session['carrinho'] = []
        carrinho_ids = []
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
    user = session.get('user')
    
    if produto_id in carrinho:
        carrinho.remove(produto_id)
        session['carrinho'] = carrinho
        session.modified =  True

        if user:
            atualizar_carrinho(user['email'], carrinho)
    return(redirect(request.referrer or url_for('carrinho.carrinho')))

@carrinho_bp.route('/add_carrinho/<produto_id>')
def add_carrinho(produto_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login.login_render'))
    produto_id = str(produto_id)
    user_email = user.get('email')

    carrinho_atual = session.get("carrinho", [])
    carrinho_atual.append(produto_id)

    session['carrinho'] = carrinho_atual
    session.modified = True

    atualizar_carrinho(user_email, carrinho_atual)
    return(redirect(request.referrer or url_for('produto.produto', id=produto_id)))

@carrinho_bp.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    user = session.get('user')
    if not user:
        return redirect(url_for('login.login'))
    selecionados = request.form.getlist('produto-carrinho-ids')
    if not selecionados:
        return(redirect(url_for('carrinho.carrinho')))
    
    carrinho_ids = session.get('carrinho', [])
    contagem = Counter(carrinho_ids)
    produtos_carrinho = []
    total = 0.0

    for produto_id in selecionados:
        qtd = contagem.get(produto_id, 1)
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

    return redirect(url_for('compra.compra'))

@carrinho_bp.route('/checkbox_precos', methods=['POST'])
def checkbox_precos():
    selecionados = request.form.getlist('produto-carrinho-ids')
    carrinho_ids = session.get('carrinho', [])
    contagem = Counter(carrinho_ids)
    produtos_carrinho = []
    total = 0.0
    total_itens = 0

    for produto_carrinho_id, qtd in contagem.items():
        if produto_carrinho_id not in selecionados:
            continue
        doc = db.collection("produtos").document(produto_carrinho_id).get()
        if doc.exists:
            produto = doc.to_dict()
            produto["id"] = produto_carrinho_id
            produto["quantidade"] = qtd
            produto["subtotal"] = produto.get("preco", 0) * qtd
            produtos_carrinho.append(produto)
            total += produto["subtotal"]
    return render_template('carrinho.html', produtos = produtos_carrinho, total= total, total_itens=total_itens)
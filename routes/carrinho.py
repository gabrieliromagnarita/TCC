from connect import db
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, Flask
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests

carrinho_bp = Blueprint('carrinho', __name__)
FIREBASE_API_KEY = 'AIzaSyB83_gLrndTGy1mx5jG8CJEA_LrCsCijdw'

@carrinho_bp.route('/carrinho-render')
def carrinho():
    carrinho_cod = session.get('carrinho', [])
    produtos_carrinho = []
    total = 0

    for produto_id in carrinho_cod:
        produto_ref = db.collection("produtos").document(produto_id).get()
        if produto_ref:
            produto = produto_ref.to_dict()
            produto["cod"] = produto_id
            produtos_carrinho.append(produto)
            total += produto.get("preco", 0)
    
    return render_template('carrinho.html', produtos = produtos_carrinho, total = total)

@carrinho_bp.route('/remove_carrinho/<produto_id>')
def remove_carrinho(produto_id):
    if carrinho in session and produto_id in session['carrinho']:
        session['carrinho'].remove(produto_id)
    return(redirect(url_for('carrinho.carrinho')))
from connect import db
from flask import Blueprint, render_template, request

home_bp = Blueprint('home', __name__)

@home_bp.route('/home-render')
def home():
    categoria = request.args.get('categoria')

    produtos = []

    if categoria:
        produtos_ref = db.collection('produtos')
        for doc in produtos_ref.where('categorias', 'array_contains', categoria.lower()).stream():
            produto = doc.to_dict()
            produto['id'] = doc.id
            produtos.append(produto)

        """ produtos = [doc.to_dict() for doc in produtos_ref.where('categorias', 'array_contains', categoria.lower()).stream()] """
    else:
        for doc in db.collection('produtos').stream():
            produto = doc.to_dict()
            produto['id'] = doc.id
            produtos.append(produto)

        """ produtos = [doc.to_dict() for doc in db.collection('produtos').stream()] """
    return render_template('home.html', produtos=produtos, categoria_atual=categoria)
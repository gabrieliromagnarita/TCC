from connect import db
from flask import Blueprint, render_template, request

home_bp = Blueprint('home', __name__)

@home_bp.route('/home-render')
def home():
    categoria = request.args.get('categoria')

    produtos = []

    if categoria:
        produtos_ref = db.collection('produtos')
        produtos = [doc.to_dict() for doc in produtos_ref.where('categorias', 'array_contains', categoria.lower()).stream()]
    else:
        produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
    return render_template('home.html', produtos=produtos, categoria_atual=categoria)

@home_bp.route('/produto/<id>')
def produto(id):
    doc_ref = db.collection('produtos').document(id)
    doc = doc_ref.get()
    if doc.exists:
        produto = doc.to_dict()
        produto['id'] = doc.id
        return render_template('produto.html', produto=produto)
    else:
        return "Produto não encontrado", 404
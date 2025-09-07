from flask import Blueprint, render_template, request
""" from connect import db """

home_bp = Blueprint('home', __name__)

@home_bp.route('/home-render')
def home():
    return render_template('home.html')

def home_filters():
    produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
    
    categoria = request.args.get('categoria')
    subcategoria = request.args.get('subcategoria')

    if categoria:
        produtos = [i for i in produtos if categoria in i.get('categorias', [])]
    if subcategoria:
        produtos = [i for i in produtos if subcategoria in i.get('categorias', [])]

    return render_template("home.html", produtos=produtos)
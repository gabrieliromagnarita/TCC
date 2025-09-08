from flask import Blueprint, render_template, request
from connect import db

home_bp = Blueprint('home', __name__)

@home_bp.route('/home-render')
def home():
    produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]

    categorias_dict = {}
    for produto in produtos:
        for categoria in produto.get('categorias', []):
            categorias_dict.setdefault(categoria, set())  # ou lista, depende de como seus dados estão
            # Aqui você pode adicionar subcategorias se houver
            for sub in produto.get('subcategorias', []):  # supondo que tenha esse campo
                categorias_dict[categoria].add(sub)

    # Converta sets para listas (Jinja não renderiza sets corretamente)
    categorias_dict = {k: list(v) for k, v in categorias_dict.items()}

    return render_template('home.html', produtos=produtos, categorias_dict=categorias_dict)
    
    
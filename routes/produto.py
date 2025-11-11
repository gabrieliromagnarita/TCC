import random
from connect import db
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from firebase_admin import firestore

produto_bp = Blueprint('produto', __name__)

@produto_bp.route('/produto/<id>')
def produto(id):
    produto_ref = db.collection("produtos").document(id).get()
    produto = produto_ref.to_dict()
    produto["id"] = id

    print(">>> Produto atual:", produto)

    categorias = produto.get("categorias", [])
    if isinstance(categorias, str):
        categorias = [categorias]

    print(">>> Categorias:", categorias)

    # Buscar todos os produto
    todos_ref = db.collection("produtos").stream()
    todos = [p.to_dict() | {"id": p.id} for p in todos_ref if p.id != id]

    print(">>> Qtd produto no banco:", len(todos))

    # Filtrar recomendados
    recomendados = [
        p for p in todos
        if any(cat in p.get("categorias", []) for cat in categorias)
    ]

    # Se não houver recomendados, pega aleatórios
    if not recomendados:
        #recomendados = random.sample(todos, min(6, len(todos)))
        recomendados = random.sample(todos)
    else:
        #recomendados = recomendados[:6]
        recomendados = todos

    print(">>> Qtd recomendados:", len(recomendados))
    for r in recomendados:
        print("   -", r["nome"], r.get("categorias"))

    # Mais vendidos
    """ mais_vendidos_ref = db.collection("produtos")\
        .order_by("vendas", direction=firestore.Query.DESCENDING)\
        .limit(5).stream()
    mais_vendidos = [p.to_dict() | {"id": p.id} for p in mais_vendidos_ref]

    print(">>> Qtd mais vendidos:", len(mais_vendidos)) """

    return render_template(
        "produto.html",
        produto=produto,
        recomendados=recomendados
    )
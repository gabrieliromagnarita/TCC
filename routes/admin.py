from flask import Blueprint, render_template, request, redirect, url_for
from connect import db
import uuid
import os

admin_bp = Blueprint('admin', __name__)

PASTA_UPLOADS = 'static/uploads/'

@admin_bp.route('/admin-render')
def admin():
    return render_template('admin.html')

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_actions():
    if request.method == 'POST':
        acao = request.form['acao-admin']
        codigo = request.form['codigo-admin'].strip()
        nome = request.form.get('nome-admin')
        marca = request.form.get('marca-admin')
        desc = request.form.get('desc-admin')
        preco = request.form.get('preco-admin')
        categorias = request.form.getlist('categorias-admin')
        qtd = request.form.get('qtd-admin')
        foto = request.files.get('foto-admin')

        if not codigo and acao == 'adicionar':
            codigo = str(uuid.uuid4())[:8]

        doc_ref = db.collection('produtos').document(codigo)

        if acao == 'adicionar':
            produto = {'codigo': codigo}
            if nome: produto['nome'] = nome
            if marca: produto['marca'] = marca
            if desc: produto['descricao'] = desc
            if preco: produto['preco'] = float(preco)
            if categorias: produto['categorias'] = categorias
            if qtd: produto['quantidade'] = qtd
            if foto:
                caminho_foto = os.path.join(PASTA_UPLOADS, foto.filename)
                foto.save(caminho_foto)
                produto['foto'] = caminho_foto

            doc_ref.set(produto, merge=True)

        elif acao == 'deletar':
            doc_ref.delete()

        return redirect(url_for('admin.admin'))
    
    produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
    return render_template('admin.html', produtos=produtos)
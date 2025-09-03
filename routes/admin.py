from flask import Blueprint, render_template, request, redirect, url_for
from connect import db
import uuid
import os

admin_bp = Blueprint('admin', __name__)

PASTA_UPLOADS = 'TCC/static/uploads'

@admin_bp.route('/admin-render')
def admin():
    return render_template('admin.html')

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_actions():
    print("[DEBUG] Rota /admin acessada.")
    if request.method == 'POST':
        print("[DEBUG] Requisição POST recebida.")
        acao = request.form['acao-admin']
        codigo = request.form['codigo-admin'].strip()
        nome = request.form.get('nome-admin')
        marca = request.form.get('marca-admin')
        desc = request.form.get('desc-admin')
        preco = request.form.get('preco-admin')
        categorias = request.form.getlist('categorias-admin')
        qtd = request.form.get('qtd-admin')
        foto1 = request.files.get('foto-admin1')
        foto2 = request.files.get('foto-admin2')

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
            if foto1:
                if not os.path.exists(PASTA_UPLOADS):
                    os.makedirs(PASTA_UPLOADS)
                caminho_foto = os.path.join(PASTA_UPLOADS, foto1.filename)
                foto1.save(caminho_foto)
                produto['foto1'] = '/' + caminho_foto.replace('\\', '/')
                doc_ref.set(produto, merge=True)
            if foto2:
                if not os.path.exists(PASTA_UPLOADS):
                    os.makedirs(PASTA_UPLOADS)
                caminho_foto = os.path.join(PASTA_UPLOADS, foto2.filename)
                foto2.save(caminho_foto)
                produto['foto2'] = '/' + caminho_foto.replace('\\', '/')
                doc_ref.set(produto, merge=True)

        elif acao == 'deletar':
            print(f"[DEBUG] Tentando deletar o código: '{codigo}'")
            doc_snapshot = doc_ref.get()
            if doc_snapshot.exists:
                doc_ref.delete()
                print(f"[DEBUG] Documento '{codigo}' deletado com sucesso.")
            else:
                print(f"[DEBUG] Documento '{codigo}' não existe.")
            return redirect(url_for('admin.admin'))

        return redirect(url_for('admin.admin'))
    
    produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
    return render_template('admin.html', produtos=produtos)
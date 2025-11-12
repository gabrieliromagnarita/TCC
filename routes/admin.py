from connect import db
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
import uuid
import os

admin_bp = Blueprint('admin', __name__)

""" PASTA_UPLOADS = 'TCC/static/uploads' """
PASTA_UPLOADS = os.path.join('static', 'uploads')

@admin_bp.route('/admin-render')
def admin():
    print("[DEBUG] Entrou na rota /admin-render")
    print("[DEBUG] session =", session) 
    user = session.get('user', {})
    if not isinstance(user, dict) or user.get('email') != 'gabihromagna@gmail.com':
        abort(403)
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
        categorias = request.form.get('categorias-admin', "").split(",")
        categorias = [i.strip() for i in categorias if i.strip()]
        qtd = request.form.get('qtd-admin')
        foto1 = request.files.get('foto-admin1')
        foto2 = request.files.get('foto-admin2')

        doc_ref = db.collection('produtos').document(codigo)

        if acao == 'adicionar':
            if not codigo:
                obrigatorios = [nome, marca, preco, categorias, qtd]
                if not all(obrigatorios):
                    erro = "preencha todos os campos"
                    produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
                    return render_template('admin.html', erro=erro, produtos=produtos,
                                           codigo=codigo, nome=nome, marca=marca, desc=desc,
                                           preco=preco, categorias=",".join(categorias), qtd=qtd)
                codigo = str(uuid.uuid4())[:8]

            doc_ref = db.collection('produtos').document(codigo)
            produto = {}

            if nome:
                produto['nome'] = nome
            if marca:
                produto['marca'] = marca
            if desc:
                produto['descricao'] = desc
            if preco:
                try:
                    produto['preco'] = float(preco)
                except ValueError:
                    erro = "Preço inválido."
                    produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
                    return render_template('admin.html', erro=erro, produtos=produtos)
            if categorias:
                produto['categorias'] = categorias
            if qtd:
                produto['quantidade'] = qtd

            if foto1 and foto1.filename != '':
                if not os.path.exists(PASTA_UPLOADS):
                    os.makedirs(PASTA_UPLOADS)
                caminho_foto = os.path.join(PASTA_UPLOADS, foto1.filename)
                foto1.save(caminho_foto)
                produto['foto1'] = f"uploads/{foto1.filename}"

            if foto2 and foto2.filename != '':
                if not os.path.exists(PASTA_UPLOADS):
                    os.makedirs(PASTA_UPLOADS)
                caminho_foto = os.path.join(PASTA_UPLOADS, foto2.filename)
                foto2.save(caminho_foto)
                produto['foto2'] = f"uploads/{foto2.filename}"

            if not produto:
                erro = "Nenhum dado para adicionar ou atualizar."
                produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
                return render_template('admin.html', erro=erro, produtos=produtos)

            produto['codigo'] = codigo  # garante que o código estará no documento

            doc_ref.set(produto, merge=True)

        elif acao == 'deletar':
            if not codigo:
                erro = "Informe o código do produto para deletar."
                produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
                return render_template('admin.html', erro=erro, produtos=produtos)

            doc_ref = db.collection('produtos').document(codigo)
            print(f"[DEBUG] Tentando deletar o código: '{codigo}'")
            doc_snapshot = doc_ref.get()
            if doc_snapshot.exists:
                doc_ref.delete()
                print(f"[DEBUG] Documento '{codigo}' deletado com sucesso.")
            else:
                print(f"[DEBUG] Documento '{codigo}' não existe.")
            return redirect(url_for('admin.admin'))

        return redirect(url_for('admin.admin'))
    
    #parte para ver a lista de produtos
    produtos = [doc.to_dict() for doc in db.collection('produtos').stream()]
    return render_template('admin.html', produtos=produtos)
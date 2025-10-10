from connect import db
from flask import Blueprint, render_template, request
import firebase_admin
from firebase_admin import auth, firestore
from email_validator import validate_email, EmailNotValidError
#import requests

cadastro_bp = Blueprint('cadastro', __name__)

def email_valido(email):
    try:
        validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError:
        return False
    
@cadastro_bp.route('/cadastro-render')
def cadastro():
    return render_template('cadastro.html')

@cadastro_bp.route('/cadastrar', methods=['POST'])
def cadastrar_user():
    email = request.form['email-cadastro']
    senha = request.form['senha-cadastro']
    senhaConfirm = request.form['senhaConfirm-cadastro']
    nome = request.form['nome-cadastro']
    telefone = request.form['fone-cadastro']
    nascimento = request.form['dataNasc-cadastro']

    if email_valido(email) == False:
        return "Email inválido!"
    if senhaConfirm != senha:
        return "As senhas não conferem!"

    try: 
        user = auth.create_user(
            email = email,
            password = senha,
        )

        try:
            user_info = {
                'email': email,
                'nome': nome,
                'telefone': telefone,
                'nascimento': nascimento,
            }
            db.collection('usuarios').add(user_info)
            return'Usuário criado com sucesso!'
        except Exception:
            return'Falha na criação do usuário!'
    except Exception:
        return'Falha na criação do usuário!1'
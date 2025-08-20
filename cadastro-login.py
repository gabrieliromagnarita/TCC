from connect import db
from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore, auth
from email_validator import validate_email, EmailNotValidError
import requests

app = Flask(__name__) #__name__ é o nome do módulo atual

FIREBASE_API_KEY = 'AIzaSyB83_gLrndTGy1mx5jG8CJEA_LrCsCijdw'

# cadastro #
def email_valido(email):
    try:
        validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError:
        return False
    
@app.route('/cadastro-render')
def cadastro():
    return render_template('cadastro.html')

@app.route('/cadastrar', methods=['POST'])
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
    
# log-in #
@app.route('/login-render')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    email = request.form['email-login']
    senha = request.form['senha-login']

    url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'

    payload = {
        'email' : email,
        'password' : senha,
        'returnSecureToken' : True
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if 'idToken' in data:
        return "Log-in bem sucedido!"
    else:
        erro = data.get('error', {}).get('message', 'Erro desconhecido')
        return f'Erro ao logar: {erro}', 401
    
# rota inicial #
@app.route('/')
def home():
    return redirect('/cadastro-render')

if __name__ == '__main__':
    app.run(debug=True)
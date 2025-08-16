from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, firestore, auth
from email_validator import validate_email, EmailNotValidError

cred = credentials.Certificate("chaveAcesso/loja-face-a-face-firebase-adminsdk-fbsvc-6acafc7c88.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__) #__name__ é o nome do módulo atual

def email_valido(email):
    try:
        validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError:
        return False
    
@app.route('/')
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
            print(f'Usuário criado com sucesso!')
        except Exception:
            print(f'Falha na criação do usuário!')
    except Exception:
        print(f'Falha na criação do usuário!1')        

if __name__ == "__main__":
    app.run(debug=True)
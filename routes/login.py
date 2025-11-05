from connect import db
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests, os

login_bp = Blueprint('login', __name__)
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

@login_bp.route('/login-render')
def login():
    return render_template('login.html')

@login_bp.route('/login', methods=['POST'])
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
        users_ref = db.collection('usuarios')
        query = users_ref.where('email', '==', email).stream()
        user_data = None
        for doc in query:
            user_data = doc.to_dict()
            break

        if user_data:
            session['user'] = user_data
        else:
            session['user'] = {'email': email}

        user_email = session['user'].get('email')
        doc_ref = db.collection("carrinhos").document(user_email)
        doc = doc_ref.get()
        if doc.exists:
            session['carrinho'] = doc.to_dict().get("produtos", [])
        else:
            session['carrinho'] = []

        if email == 'gabihromagna@gmail.com':
            return(redirect(url_for('admin.admin')))
        else:
            return(redirect(url_for('home.home')))
    
    return render_template('login.html', erro="E-mail ou senha inválidos.")
    
@login_bp.route('/recuperar-senha', methods=['POST'])
def recuperar_senha():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return 'E-mail não informado', 400
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_API_KEY}"

    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }

    response = requests.post(url, json=payload)
    res_data = response.json()
    print("Resposta Firebase:", res_data)

    if 'email' in res_data:
        return "E-mail de recuperação enviado com sucesso!"
    else:
        erro = res_data.get("error", {}).get("message", "Erro desconhecido")
        return f"Erro ao enviar e-mail de recuperação: {erro}", 400
    
@login_bp.route('/logout')
def logout():
    user = session.get('user')
    if user:
        user_email = user.get('email')
        carrinho = session.get('carrinho', [])
        db.collection("carrinhos").document(user_email).set({"produtos": carrinho}, merge=True)
    session.clear()# remove o usuário e o carrinho da sessão
    return redirect(url_for('home.home'))
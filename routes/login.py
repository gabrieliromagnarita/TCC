from connect import db
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests

login_bp = Blueprint('login', __name__)
FIREBASE_API_KEY = 'AIzaSyB83_gLrndTGy1mx5jG8CJEA_LrCsCijdw'

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
        session['user'] = email
        if email == 'gabihromagna@gmail.com':
            return redirect(url_for('admin.admin'))
        else:
            return redirect(url_for('home.home'))
    else:
        erro = data.get('error', {}).get('message', 'Erro desconhecido')
        return f'Erro ao logar: {erro}', 401
    
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

    if 'email' in res_data:
        return "E-mail de recuperação enviado com sucesso!"
    else:
        erro = res_data.get("error", {}).get("message", "Erro desconhecido")
        return f"Erro ao enviar e-mail de recuperação: {erro}", 400
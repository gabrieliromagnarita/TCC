from flask import Blueprint, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
from connect import db

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
        return "Log-in bem sucedido!"
    else:
        erro = data.get('error', {}).get('message', 'Erro desconhecido')
        return f'Erro ao logar: {erro}', 401
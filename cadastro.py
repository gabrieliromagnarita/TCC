import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from email_validator import validate_email, EmailNotValidError

cred = credentials.Certificate("chaveAcesso/loja-face-a-face-firebase-adminsdk-fbsvc-6acafc7c88.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

def email_valido(email):
    try:
        validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError:
        return False

def cadastrar_user():
    email = input("Email: ")
    senha = input("Senha: ")
    senhaConfirm = input("Confirme a senha: ")
    nome = input("Nome: ")
    telefone = input("Telefone: ")
    nascimento = input("Nascimento: ")

    if email_valido(email) == False:
        print("Email inválido!")
    if senhaConfirm != senha:
        print("Senha inválida!")
    else:
        try: 
            auth.create_user(
                email = email,
                password = senha,
            )

            try:
                user_info = {
                    'email': email,
                    'senha': senha,
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

cadastrar_user()
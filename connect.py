from dotenv import load_dotenv
import os, json
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
cred_json = os.getenv("FIREBASE_CREDENTIALS")
cred_dict = json.loads(cred_json)

if not firebase_admin._apps:
    credential = credentials.Certificate(cred_dict)
    app = firebase_admin.initialize_app(credential)
else:
    print("App inicializado!")

db = firestore.client()

print("Banco conectado!")

mercado_pago_key = os.getenv("MERCADO_PAGO_KEY")
if not mercado_pago_key:
    raise ValueError("ERRO na conexão com o Mercado Pago")

print("Conectado")
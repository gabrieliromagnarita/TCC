import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("chaveAcesso/loja-face-a-face-firebase-adminsdk-fbsvc-6acafc7c88.json")

app = firebase_admin.initialize_app(cred)

db = firestore.client()

print("Banco conectado!")
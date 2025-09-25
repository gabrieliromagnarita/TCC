from flask import Flask;
from routes.cadastro import cadastro_bp
from routes.login import login_bp
from routes.admin import admin_bp
from routes.rotas import rotas_bp
from routes.historia import historia_bp
from routes.faq import faq_bp
from routes.home import home_bp
from routes.produto import produto_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.register_blueprint(cadastro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(rotas_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(historia_bp)
app.register_blueprint(faq_bp)
app.register_blueprint(home_bp)
app.register_blueprint(produto_bp)

if __name__ == "__main__":
    app.run(debug=True)
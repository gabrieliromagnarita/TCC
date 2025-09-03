from flask import Flask;
from routes.cadastro import cadastro_bp
from routes.login import login_bp
from routes.admin import admin_bp
from routes.rotas import rotas_bp
from routes.historia import historia_bp
from routes.faq import faq_bp
from routes.home import home_bp

app = Flask(__name__)

app.register_blueprint(cadastro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(rotas_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(historia_bp)
app.register_blueprint(faq_bp)
app.register_blueprint(home_bp)

if __name__ == "__main__":
    app.run(debug=True)
from flask import Blueprint, redirect

rotas_bp = Blueprint('rotas', __name__)

@rotas_bp.route('/')
def rotas():
    return redirect('/home-render')
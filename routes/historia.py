from flask import Blueprint, render_template

historia_bp = Blueprint('historia', __name__)

@historia_bp.route('/historia-render')
def historia():
    return render_template('historia.html')
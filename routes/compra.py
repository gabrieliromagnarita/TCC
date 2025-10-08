from flask import Blueprint, render_template, session, redirect, url_for

compra_bp = Blueprint('compra', __name__)

@compra_bp.route('/compra-render')
def compra():
    compra_data = session.get('compra')
    if not compra_data:
        return redirect(url_for('carrinho.carrinho'))
    
    produtos = compra_data.get('produtos', [])
    total = compra_data.get('total', 0.0)

    return render_template('compra.html', produtos=produtos, total=total)
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import uuid, datetime, qrcode, base64, barcode
from io import BytesIO
from barcode.writer import ImageWriter

compra_bp = Blueprint('compra', __name__)

@compra_bp.route('/compra-render')
def compra():
    compra_data = session.get('compra')
    if not compra_data:
        return redirect(url_for('carrinho.carrinho'))
    
    produtos = compra_data.get('produtos', [])
    total = compra_data.get('total', 0.0)

    return render_template('compra.html', produtos=produtos, total=total)

@compra_bp.route('/comprar', methods=['post'])
def comprar():
    tipo = request.form.get('tipo-pag')
    compra_data = session.get('compra')

    if not compra_data:
        return redirect(url_for('carrinho.carrinho'))
    
    produtos = compra_data.get('produtos', [])
    total = compra_data.get('total', 0,0)
    pedido_cod = str(uuid.uuid4())[:8]

    pag_info = None

    if tipo == "pix":
        chave = 'faceafaceloja@gmail.com'
        nome = "Face a Face Loja"
        cod = pedido_cod

        payload = payload(
            chave=chave,
            nome=nome,
            valor=total,
            cod=cod
        )

        qr_code = payload.export_pix_cod()
        
        qrcode_img = qrcode.make(qr_code)
        buffer = BytesIO()
        qrcode_img.save(buffer, format="png")
        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")


        pag_info = {"tipo":"pix", "pedido_cod": pedido_cod, "chave": chave, "qrcode":qr_code, "qrcode_img": img_b64}

    elif tipo == "boleto":
        vencimento = (datetime.date.today() + datetime.timedelta(days=3)).strftime("%d/%m/%Y")
        cod_barras = ''

        codigo = pag_info["cod_barras"].replace(" ","")
        barcode = barcode.get('code128', codigo, writer=ImageWriter())
        buffer = BytesIO()
        barcode.write(buffer)
        cod_barras_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        pag_info = {"tipo":"boleto", "pedido_cod": pedido_cod, "vencimento": vencimento, "cod_barras": cod_barras, "cod_barras_img": cod_barras_img}

    return render_template('compra.html', produtos=produtos, total=total, pag_info=pag_info)
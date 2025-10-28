from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import uuid, datetime, qrcode, base64, barcode
from io import BytesIO
from barcode.writer import ImageWriter
import mercadopago
from connect import mercado_pago_key
import os

compra_bp = Blueprint('compra', __name__)

chave_mp = mercadopago.SDK(mercado_pago_key)

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
    total = compra_data.get('total', 0.0)
    pedido_cod = str(uuid.uuid4())[:8]

    pag_info = None

    if tipo == "pix":
        chave = '.com'
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
        print("DEBUG - Mercado Pago Key:", mercado_pago_key[:10])
        vencimento = (datetime.date.today() + datetime.timedelta(days=3)).strftime("%d/%m/%Y")

        pagamento_data = {
            "transaction_amount": float(total),
            "description": "Compra na loja Face a Face",
            "payment_method_id": "bolbradesco",
            "payer": {
                "email": "test_user_123456@testuser.com", #session.get('user', {}).get('email'),
                "first_name": session.get('user', {}).get('nome'),
                "last_name": "Cliente",
                "identification":{
                    "type": "CPF",
                    "number": session.get('user', {}).get('cpf')
                },
                "address": {
                    "zip_code": "12345678",
                    "street_name": "Rua Teste",
                    "street_number": "123",
                    "neighborhood": "Centro",
                    "city": "São Paulo",
                    "federal_unit": "SP"
                }
            },
            "date_of_expiration": (datetime.date.today() + datetime.timedelta(days=3)).isoformat()
        }

        pagamento_resposta = chave_mp.payment().create(pagamento_data)
        if pagamento_resposta is None:
            print("Erro: pagamento_resposta é None")
            flash("Erro ao criar pagamento. Verifique os dados.", "error")
            return redirect(url_for('compra.compra'))
        
        pagamento = pagamento_resposta.get("response", {})
        if not pagamento:
            print("Erro: pagamento é None ou vazio", pagamento_resposta)
            flash("Erro ao criar pagamento. Verifique os dados.", "error")
            return redirect(url_for('compra.compra'))
        
        print("DEBUG - resposta completa do boleto:", pagamento_resposta)

    if pagamento.get("status") in ("pending",):
        boleto_url = pagamento.get("transaction_details", {}).get("external_resource_url")
        barcode_number = pagamento.get("barcode", {}).get("content")

        cod_barras_img = None
        if barcode_number:
            barcode_obj = barcode.get('code128', barcode_number, writer=ImageWriter())
            buffer = BytesIO()
            barcode_obj.write(buffer)
            cod_barras_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        pag_info = {
            "tipo":"boleto",
            "pedido_cod": pedido_cod,
            "vencimento": vencimento,
            "cod_barras": barcode_number,
            "cod_barras_img": cod_barras_img,
            "boleto_url": boleto_url,
        }
    else:
        render_template('compra.html')

    return render_template('compra.html', produtos=produtos, total=total, pag_info=pag_info)
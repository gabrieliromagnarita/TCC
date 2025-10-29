from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import uuid, datetime, qrcode, base64, barcode,mercadopago, random
from io import BytesIO
from barcode.writer import ImageWriter
from barcode import EAN13
import qrcode.constants
from connect import mercado_pago_key

compra_bp = Blueprint('compra', __name__)

chave_mp = mercadopago.SDK(mercado_pago_key)

request_options = mercadopago.config.RequestOptions()
request_options.custom_headers = {
    'x-idempotency-key': str(uuid.uuid4())
}

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
    
    total = compra_data.get('total', 0.0)
    produtos = compra_data.get('produtos', [])

    pag_info = None

    if tipo == "pix":
        payment_data = {
            "transaction_amount": float(total),
            "payment_method_id": "pix",
            "payer": {
                "email": session.get('user', {}).get('email'),
            }
        }

        payment_response = chave_mp.payment().create(payment_data, request_options)
        print("DEBUG - payment_response:", payment_response)
        pag_info = payment_response["response"]
        print("DEBUG - pag_info:", pag_info)

        poi = pag_info.get("point_of_interaction", {}) or pag_info.get("transaction_details") or {}
        print("DEBUG - poi:", poi)

        chave_pix = poi.get("qr_code")
        print("DEBUG - chave_pix:", chave_pix)
        qr_base64 = poi.get("qr_base64")
        print("DEBUG - qr_base64:", qr_base64)

        pag_info = {
            "tipo": "pix",
            "chave": chave_pix,
            "qr_code_img": qr_base64
        }
        print("DEBUG - pag info:", pag_info)

        return render_template('compra.html', produtos=produtos, total=total, pag_info=pag_info)

    elif tipo == "boleto":
        print("DEBUG - Mercado Pago Key:", mercado_pago_key[:10])
        payment_data = {
            "transaction_amount": float(total),
            "description": "Compra na loja Face a Face",
            "payment_method_id": "bolbradesco",
            "payer": {
                "email": session.get('user', {}).get('email'),
                "first_name": session.get('user', {}).get('nome'),
                "last_name": "Cliente",
                "identification": {
                    "type": "CPF",
                    "number": session.get('user', {}).get('cpf')
                },
                "address": {
                    "zip_code": "06233-200",
                    "street_name": "Av. das Nações Unidas",
                    "street_number": "3003",
                    "neighborhood": "Bonfim",
                    "city": "Osasco",
                    "federal_unit": "SP"
                }
            }
        }

        payment_response = chave_mp.payment().create(payment_data, request_options)
        pag_info = payment_response["response"]

        codigo_boleto = pag_info.get("barcode", {}).get("content")
        if (codigo_boleto == None):
            codigo_boleto = "123456789012"
        print("DEBUG - Codigo Boleto:", codigo_boleto)

        ean = barcode.get('EAN13', codigo_boleto, writer=ImageWriter())
        filename = ean.save(f'codigo_de_barras{codigo_boleto}')
        print(f'codigo de barras salvo como: {filename}')

        return render_template('compra.html', produtos=produtos, total=total, pag_info=pag_info, )
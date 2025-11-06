from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
import uuid, datetime, qrcode, base64, barcode,mercadopago, random, requests
from barcode.writer import ImageWriter
from barcode import EAN13
import qrcode.constants
from connect import mercado_pago_key, db
from xml.etree import ElementTree as ET

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

@compra_bp.route('/comprar_agora/<id>', methods=['GET'])
def comprar_agora(id):
    produto_ref = db.collection("produtos").document(id).get()
    if not produto_ref.exists:
        return "Produto não encontrado", 404
    
    produto = produto_ref.to_dict()
    produto["id"] = id
    produto["quantidade"] = 1

    compra_data = {
        "produtos": [produto],
        "total": float(produto["preco"])
    }

    session["compra"] = compra_data

    return redirect(url_for('compra.compra'))

@compra_bp.route('/calculo_frete', methods=['POST'])
def calculo_frete():
    print(">>> Rota calculo_frete foi chamada!")
    cep_destino = request.form.get('cep-compra')
    print(">>> CEP recebido:", cep_destino)
    if not cep_destino or not cep_destino.isdigit():
        return jsonify({"erro": "CEP inválido"}), 400
    
    cep_origem = "35430970"

    peso = "1"
    comprimento = "20"
    altura = "10"
    largura = "15"

    codigos_servicos = ["04510", "04014"]

    resultados = []

    for servico in codigos_servicos:
        url = (
            "https://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx"
            f"?nCdEmpresa=&sDsSenha=&nCdServico={servico}"
            f"&sCepOrigem={cep_origem}&sCepDestino={cep_destino}"
            f"&nVlPeso={peso}&nCdFormato=1&nVlComprimento={comprimento}"
            f"&nVlAltura={altura}&nVlLargura={largura}&nVlDiametro=0"
            "&sCdMaoPropria=N&nVlValorDeclarado=0&sCdAvisoRecebimento=N&StrRetorno=xml"
        )

        response = requests.get(url)
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print(response)
        resposta_xml = ET.fromstring(response.text)
        
        servico_nome = "PAC" if servico == "04510" else "SEDEX"
        valor = resposta_xml.find(".//Valor").text.replace(",",".")
        prazo = resposta_xml.find(".//PrazoEntrega").text
        
        resultados.append({
            "servico": servico_nome,
            "valor": float(valor),
            "prazo": prazo
        })
        print(resultados)

    if not resultados:
        return("ERRO")
        
    return jsonify(resultados)

@compra_bp.route('/comprar', methods=['POST'])
def comprar():
    tipo = request.form.get('tipo-pag')
    compra_data = session.get('compra')

    if not compra_data:
        return redirect(url_for('carrinho.carrinho'))
    
    total = float(request.form.get('total-final', 0.0))
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

        poi = pag_info.get("point_of_interaction", {}).get("transaction_data")

        chave_pix = poi.get("qr_code")
        qr_base64 = poi.get("qr_code_base64")
        print("DEBUG - transaction_data:", poi)

        pag_info = {
            "tipo": "pix",
            "chave": chave_pix,
            "qr_code_img": qr_base64
        }
        print("DEBUG - pag info:", pag_info)

        return render_template('compra.html', produtos=produtos, total=total, pag_info=pag_info)

    """ elif tipo == "boleto":
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

        return render_template('compra.html', produtos=produtos, total=total, pag_info=pag_info, ) """
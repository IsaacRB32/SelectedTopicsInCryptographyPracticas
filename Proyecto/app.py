from flask import Flask, request, jsonify
from flask_cors import CORS
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
import hashlib
import json

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/generate_keys', methods=['POST'])
def generate_keys():
    """
    Genera un par de llaves ECDSA usando la curva SECP256k1.
    La clave privada 'd' es un entero aleatorio.
    La clave pública 'Q' es el punto Q = d * G en la curva.
    Devuelve ambas en formato hexadecimal.
    """
    sk = SigningKey.generate(curve=SECP256k1)
    vk = sk.verifying_key
    return jsonify({
        'private_key': sk.to_string().hex(),   # d  (32 bytes = 64 hex chars)
        'public_key':  vk.to_string().hex()    # Qx || Qy (64 bytes = 128 hex chars)
    })


@app.route('/sign', methods=['POST'])
def sign():
    """
    Firma un JSON de transacción con la clave privada del cliente.

    Pasos ECDSA:
      1. Serializar el JSON con claves ordenadas (determinista) → mensaje m
      2. e = SHA-256(m) mod n
      3. k = valor determinístico (RFC 6979) a partir de d y e
      4. r = (k·G).x mod n
      5. s = k⁻¹ · (e + r·d) mod n
      6. Firma = (r || s) en bytes

    Body esperado:
      { "transaction": {...}, "private_key": "<hex>" }
    """
    data = request.get_json()
    if not data or 'transaction' not in data or 'private_key' not in data:
        return jsonify({'error': 'Faltan campos: transaction y private_key'}), 400

    transaction    = data['transaction']
    private_key_hex = data['private_key']

    # Serialización determinista: sort_keys garantiza el mismo orden siempre
    message       = json.dumps(transaction, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    message_bytes = message.encode('utf-8')

    try:
        sk  = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
        sig = sk.sign_deterministic(message_bytes, hashfunc=hashlib.sha256)

        return jsonify({
            'signature':      sig.hex(),                                        # r || s (64 bytes)
            'message_hash':   hashlib.sha256(message_bytes).hexdigest(),        # e antes de mod n
            'signed_message': message                                            # JSON que se firmó
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/verify', methods=['POST'])
def verify():
    """
    Verifica que la firma ECDSA corresponda al JSON recibido y a la clave pública del cliente.

    Pasos de verificación ECDSA:
      1. Reconstruir el mismo mensaje determinista m = JSON(transaction, sort_keys)
      2. e = SHA-256(m) mod n
      3. w = s⁻¹ mod n
      4. u1 = (e · w) mod n
      5. u2 = (r · w) mod n
      6. X  = u1·G + u2·Q
      7. Válido si X.x mod n == r

    Body esperado:
      { "transaction": {...}, "signature": "<hex>", "public_key": "<hex>" }
    """
    data = request.get_json()
    if not data or 'transaction' not in data or 'signature' not in data or 'public_key' not in data:
        return jsonify({'error': 'Faltan campos: transaction, signature, public_key'}), 400

    transaction    = data['transaction']
    signature_hex  = data['signature']
    public_key_hex = data['public_key']

    # Reconstruir exactamente el mismo mensaje que se firmó
    message       = json.dumps(transaction, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    message_bytes = message.encode('utf-8')
    message_hash  = hashlib.sha256(message_bytes).hexdigest()

    try:
        vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
        vk.verify(bytes.fromhex(signature_hex), message_bytes, hashfunc=hashlib.sha256)
        return jsonify({'valid': True,  'message_hash': message_hash})

    except BadSignatureError:
        return jsonify({'valid': False, 'message_hash': message_hash})

    except Exception as e:
        return jsonify({'valid': False, 'message_hash': message_hash, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)

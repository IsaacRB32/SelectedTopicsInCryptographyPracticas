# Importa librerias
import os
from ecdsa import SigningKey, SECP256k1

# Generar clave privada
sk = SigningKey.generate(curve=SECP256k1)

# Obtener clave publica
vk = sk.verifying_key

# Imprimir clave privada
#print("Privada:", sk.to_string().hex())
#print("Pública:", vk.to_string().hex())

# Crea un archivo con la llave privada
with open('llave_privada.txt', 'w') as f:
    f.write(sk.to_string().hex())
# Crea un archivo con la llave publica
with open('llave_publica.txt', 'w') as f:
    f.write(vk.to_string().hex())

print("Claves generadas y guardadas correctamente.")
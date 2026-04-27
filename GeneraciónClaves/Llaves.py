import os
from ecdsa import SigningKey, SECP256k1
import tkinter as tk

def generar_claves():
    # Generar clave privada
    sk = SigningKey.generate(curve=SECP256k1)

    # Obtener clave pública
    vk = sk.verifying_key

    # Guardar claves en archivos
    with open('llave_privada.txt', 'w') as f:
        f.write(sk.to_string().hex())

    with open('llave_publica.txt', 'w') as f:
        f.write(vk.to_string().hex())

    # Mostrar resultado en la interfaz
    resultado.set("Claves generadas y guardadas correctamente.")

# Crear ventana
ventana = tk.Tk()
ventana.title("Generador de Claves")

# Tamaño de la ventana (ancho x alto)
ventana.geometry("400x200")

# Variable para mostrar mensajes
resultado = tk.StringVar()
resultado.set("Presiona el botón para generar claves")

# Etiqueta
label = tk.Label(ventana, textvariable=resultado)
label.pack()

# Botón
boton = tk.Button(ventana, text="Generar Claves", command=generar_claves)
boton.pack()

# Ejecutar interfaz
ventana.mainloop()
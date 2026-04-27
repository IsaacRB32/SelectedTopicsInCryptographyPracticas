import hashlib
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from ecdsa import SigningKey, SECP256k1

# -- Parametros de la curva SECP256k1
curva = SECP256k1
n = curva.order
G = curva.generator

# -- Paleta de colores (misma que el verificador)
BG = "#0f172a"
CARD = "#1e293b"
BORDE = "#334155"
AZUL = "#3b82f6"
AZUL_HOVER = "#2563eb"
TEXTO = "#e2e8f0"
TEXTO_DIM = "#94a3b8"
VERDE = "#22c55e"
AMARILLO = "#f59e0b"


# -- Helpers de UI (los mismos que en el verificador)

def hacer_hover(boton, color_normal, color_hover):
    boton.bind("<Enter>", lambda e: boton.config(bg=color_hover))
    boton.bind("<Leave>", lambda e: boton.config(bg=color_normal))

def separador(padre):
    tk.Frame(padre, height=1, bg=BORDE).pack(fill="x", padx=20, pady=4)

def etiqueta_seccion(padre, numero, texto):
    fila = tk.Frame(padre, bg=CARD)
    fila.pack(fill="x", padx=20, pady=(14, 4))
    tk.Label(fila, text=str(numero), bg=AZUL, fg="white",
             font=("Segoe UI", 9, "bold"), width=2, height=1,
             padx=4, pady=2).pack(side=tk.LEFT, padx=(0, 8))
    tk.Label(fila, text=texto, bg=CARD, fg=TEXTO,
             font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

def fila_entrada(padre, var_entry, cmd_boton):
    fila = tk.Frame(padre, bg=CARD)
    fila.pack(fill="x", padx=20, pady=(0, 4))
    entry = tk.Entry(fila, textvariable=var_entry, bg=BG, fg=TEXTO,
                     insertbackground=TEXTO, relief="flat",
                     font=("Segoe UI", 9), bd=0)
    entry.pack(side=tk.LEFT, fill="x", expand=True, ipady=6, padx=(4, 0))
    btn = tk.Button(fila, text="Explorar...", command=cmd_boton,
                    bg=CARD, fg=AZUL, activebackground=BORDE,
                    activeforeground=AZUL, relief="flat",
                    font=("Segoe UI", 9), cursor="hand2", bd=0, padx=10, pady=5)
    btn.pack(side=tk.LEFT, padx=(6, 0))
    hacer_hover(btn, CARD, BORDE)
    return entry


# -- Funcion principal de firma

def firmar():
    # Leer llave privada
    ruta_privada = var_privada.get().strip()
    if not ruta_privada:
        messagebox.showerror("Error", "Selecciona el archivo de llave privada.")
        return
    try:
        with open(ruta_privada, 'r') as f:
            llave_privada_hex = f.read().strip()
        sk = SigningKey.from_string(bytes.fromhex(llave_privada_hex), curve=SECP256k1)
        d  = int.from_bytes(bytes.fromhex(llave_privada_hex), byteorder='big')
        # La llave publica Q = d * G
        Q  = sk.verifying_key.pubkey.point
    except Exception as e:
        messagebox.showerror("Error", f"Llave privada invalida:\n{e}")
        return

    # Leer mensaje
    ruta_msg = var_mensaje.get().strip()
    if not ruta_msg:
        messagebox.showerror("Error", "Selecciona el archivo del mensaje a firmar.")
        return
    try:
        with open(ruta_msg, 'r') as f:
            mensaje = f.read().strip()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el mensaje:\n{e}")
        return

    # Pasos de firma ECDSA 

    # Paso 1: e = SHA-256(mensaje) convertido a entero mod n
    hash_bytes = hashlib.sha256(mensaje.encode('utf-8')).digest()
    e = int.from_bytes(hash_bytes, byteorder='big') % n

    # Paso 2 y 3: la libreria ecdsa genera k aleatorio y calcula
    #   r = (k*G).x mod n
    #   s = k^-1 * (e + r*d) mod n
    # Usamos sign_deterministic para que k sea reproducible (RFC 6979)
    firma_bytes = sk.sign_deterministic(
        mensaje.encode('utf-8'),
        hashfunc=hashlib.sha256
    )

    # La firma es 64 bytes: primeros 32 = r, ultimos 32 = s
    r = int.from_bytes(firma_bytes[:32], byteorder='big')
    s = int.from_bytes(firma_bytes[32:], byteorder='big')
    firma_hex = firma_bytes.hex()   # 128 caracteres

    # Guardar firma en archivo junto al mensaje
    dir_msg   = os.path.dirname(ruta_msg)
    ruta_firma = os.path.join(dir_msg, "firma.txt")
    with open(ruta_firma, 'w') as f:
        f.write(firma_hex)

    # -- Mostrar resultados
    area_resultado.config(state=tk.NORMAL)
    area_resultado.delete("1.0", tk.END)

    def linea(texto, tag=None):
        area_resultado.insert(tk.END, texto + "\n", tag if tag else "")

    linea("  LLAVE PRIVADA", "titulo")
    linea(f"  d  = {hex(d)}")
    linea("")
    linea("  LLAVE PUBLICA  Q = d * G", "titulo")
    linea(f"  Qx = {hex(Q.x())}")
    linea(f"  Qy = {hex(Q.y())}")
    linea("")
    linea("  MENSAJE", "titulo")
    linea(f"  {mensaje[:200]}{'...' if len(mensaje) > 200 else ''}")
    linea("")
    linea("  PASOS DE FIRMA ECDSA", "titulo")
    linea(f"  Paso 1  e  = SHA-256(m) mod n")
    linea(f"          e  = {hex(e)}")
    linea(f"  Paso 2  k  = valor aleatorio deterministico (RFC 6979)")
    linea(f"  Paso 3  r  = (k*G).x mod n")
    linea(f"          r  = {hex(r)}")
    linea(f"  Paso 4  s  = k^-1 * (e + r*d) mod n")
    linea(f"          s  = {hex(s)}")
    linea("")
    linea("  FIRMA GENERADA  (r || s en hex, 128 chars)", "titulo")
    linea(f"  {firma_hex}", "firma")
    linea("")
    linea(f"  Guardada en: {ruta_firma}", "dim")

    area_resultado.config(state=tk.DISABLED)

    etiqueta_resultado.config(text="  ✔  Firma generada y guardada", fg=VERDE, bg=CARD)

    # Copiar firma al portapapeles para facilitar el pegado en el verificador
    ventana.clipboard_clear()
    ventana.clipboard_append(firma_hex)


# -- Funciones de explorador de archivos

def buscar_privada():
    ruta = filedialog.askopenfilename(
        title="Selecciona el archivo de llave privada",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")]
    )
    if ruta:
        var_privada.set(ruta)

def buscar_mensaje():
    ruta = filedialog.askopenfilename(
        title="Selecciona el archivo del mensaje a firmar",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")]
    )
    if ruta:
        var_mensaje.set(ruta)


# -- Ventana principal

ventana = tk.Tk()
ventana.title("Firmador ECDSA")
ventana.configure(bg=BG)
ventana.resizable(False, False)

var_privada = tk.StringVar()
var_mensaje = tk.StringVar()

# Header
header = tk.Frame(ventana, bg=CARD, pady=16)
header.pack(fill="x")
tk.Label(header, text="Firma de Documento Digital",
         bg=CARD, fg=TEXTO, font=("Segoe UI", 15, "bold")).pack()
tk.Label(header, text="ECDSA  •  Curva SECP256k1  •  SHA-256",
         bg=CARD, fg=TEXTO_DIM, font=("Segoe UI", 9)).pack(pady=(2, 0))

separador(ventana)

# Tarjeta de inputs
card = tk.Frame(ventana, bg=CARD, pady=10)
card.pack(fill="x", padx=16, pady=8)

# Seccion 1: llave privada
etiqueta_seccion(card, "1", "Llave privada del firmante (.txt)")
fila_entrada(card, var_privada, buscar_privada)

separador(card)

# Seccion 2: mensaje
etiqueta_seccion(card, "2", "Archivo del mensaje a firmar (.txt)")
fila_entrada(card, var_mensaje, buscar_mensaje)

# Boton firmar
btn_firmar = tk.Button(ventana, text="  Firmar documento  ",
                       command=firmar,
                       bg=AZUL, fg="white", activebackground=AZUL_HOVER,
                       activeforeground="white",
                       font=("Segoe UI", 11, "bold"),
                       relief="flat", cursor="hand2",
                       pady=10, padx=20, bd=0)
btn_firmar.pack(pady=12)
hacer_hover(btn_firmar, AZUL, AZUL_HOVER)

# Etiqueta resultado rapido
etiqueta_resultado = tk.Label(ventana, text="",
                              bg=CARD, fg=TEXTO,
                              font=("Segoe UI", 12, "bold"),
                              pady=8, padx=16)
etiqueta_resultado.pack(fill="x", padx=16)

# Area de log
tk.Label(ventana, text="Detalle del proceso",
         bg=BG, fg=TEXTO_DIM,
         font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(8, 2))

area_resultado = scrolledtext.ScrolledText(ventana, height=18, width=84,
                                           bg="#0d1117", fg="#c9d1d9",
                                           insertbackground=TEXTO,
                                           relief="flat", bd=0,
                                           font=("Courier New", 9),
                                           state=tk.DISABLED)
area_resultado.pack(padx=16, pady=(0, 16))

area_resultado.tag_config("titulo", foreground=AZUL,     font=("Courier New", 9, "bold"))
area_resultado.tag_config("firma",  foreground=AMARILLO, font=("Courier New", 9, "bold"))
area_resultado.tag_config("dim",    foreground=TEXTO_DIM)

ventana.mainloop()

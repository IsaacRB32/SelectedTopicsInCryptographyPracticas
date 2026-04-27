import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from ecdsa import VerifyingKey, SECP256k1

# -- Parametros de la curva SECP256k1
curva = SECP256k1
n     = curva.order
G     = curva.generator

# -- Paleta de colores
BG          = "#0f172a"   # fondo principal  (azul muy oscuro)
CARD        = "#1e293b"   # fondo de tarjetas
BORDE       = "#334155"   # bordes sutiles
AZUL        = "#3b82f6"   # acento principal
AZUL_HOVER  = "#2563eb"
TEXTO       = "#e2e8f0"   # texto principal
TEXTO_DIM   = "#94a3b8"   # texto secundario
VERDE       = "#22c55e"
ROJO        = "#ef4444"
MONO        = "#0f172a"   # fondo del area de log


# ── Helpers de UI ─────────────────────────────────────────────────────────────

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
    entry.pack(side=tk.LEFT, fill="x", expand=True,
               ipady=6, padx=(4, 0))

    # linea inferior como borde
    tk.Frame(fila, height=1, bg=BORDE).place(relx=0, rely=1, relwidth=1)

    btn = tk.Button(fila, text="Explorar…", command=cmd_boton,
                    bg=CARD, fg=AZUL, activebackground=BORDE,
                    activeforeground=AZUL, relief="flat",
                    font=("Segoe UI", 9), cursor="hand2",
                    bd=0, padx=10, pady=5)
    btn.pack(side=tk.LEFT, padx=(6, 0))
    hacer_hover(btn, CARD, BORDE)
    return entry


# ── Funcion principal de verificacion ─────────────────────────────────────────
def verificar():
    # Leer llave publica
    ruta_publica = var_llave.get().strip()
    if not ruta_publica:
        messagebox.showerror("Error", "Selecciona el archivo de llave publica.")
        return
    try:
        with open(ruta_publica, 'r') as f:
            llave_publica_hex = f.read().strip()
        vk = VerifyingKey.from_string(bytes.fromhex(llave_publica_hex), curve=SECP256k1)
        Q  = vk.pubkey.point
    except Exception as e:
        messagebox.showerror("Error", f"Llave publica invalida:\n{e}")
        return

    # Leer mensaje
    ruta_msg = var_mensaje.get().strip()
    if not ruta_msg:
        messagebox.showerror("Error", "Selecciona el archivo del mensaje.")
        return
    try:
        with open(ruta_msg, 'r') as f:
            mensaje = f.read().strip()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el mensaje:\n{e}")
        return

    # Leer firma
    firma_hex = entrada_firma.get("1.0", tk.END).strip()
    if len(firma_hex) != 128:
        messagebox.showerror("Error", "La firma debe tener exactamente 128 caracteres hexadecimales.")
        return
    try:
        r = int(firma_hex[:64], 16)
        s = int(firma_hex[64:], 16)
    except ValueError:
        messagebox.showerror("Error", "La firma contiene caracteres no hexadecimales.")
        return

    # Paso 1: e = SHA-256(mensaje) mod n
    hash_bytes = hashlib.sha256(mensaje.encode('utf-8')).digest()
    e = int.from_bytes(hash_bytes, byteorder='big') % n

    # Paso 2: w = s^-1 mod n
    w = pow(s, -1, n)

    # Paso 3: u1 = (e * w) mod n
    u1 = (e * w) % n

    # Paso 4: u2 = (r * w) mod n
    u2 = (r * w) % n

    # Paso 5: X = u1*G + u2*Q
    X = u1 * G + u2 * Q

    # Paso 6: firma valida si Xx mod n == r
    Xx_mod_n = X.x() % n
    es_valida = (Xx_mod_n == r)

    # -- Mostrar resultados
    area_resultado.config(state=tk.NORMAL)
    area_resultado.delete("1.0", tk.END)

    def linea(texto, tag=None):
        if tag:
            area_resultado.insert(tk.END, texto + "\n", tag)
        else:
            area_resultado.insert(tk.END, texto + "\n")

    linea("  LLAVE PUBLICA", "titulo")
    linea(f"  Qx = {hex(Q.x())}")
    linea(f"  Qy = {hex(Q.y())}")
    linea("")
    linea("  MENSAJE", "titulo")
    linea(f"  {mensaje[:200]}{'...' if len(mensaje) > 200 else ''}")
    linea("")
    linea("  FIRMA RECIBIDA", "titulo")
    linea(f"  r = {hex(r)}")
    linea(f"  s = {hex(s)}")
    linea("")
    linea("  PASOS DE VERIFICACION ECDSA", "titulo")
    linea(f"  Paso 1  e  = SHA-256(m) mod n")
    linea(f"          e  = {hex(e)}")
    linea(f"  Paso 2  w  = s^-1 mod n")
    linea(f"          w  = {hex(w)}")
    linea(f"  Paso 3  u1 = (e*w) mod n")
    linea(f"          u1 = {hex(u1)}")
    linea(f"  Paso 4  u2 = (r*w) mod n")
    linea(f"          u2 = {hex(u2)}")
    linea(f"  Paso 5  X  = u1*G + u2*Q")
    linea(f"          Xx = {hex(X.x())}")
    linea(f"  Paso 6  Xx mod n == r ?")
    linea(f"          Xx mod n = {hex(Xx_mod_n)}")
    linea(f"          r        = {hex(r)}")
    linea("")

    if es_valida:
        linea("  FIRMA VALIDA — El mensaje es autentico.", "valida")
        etiqueta_resultado.config(text="  ✔  FIRMA VALIDA", fg=VERDE, bg=CARD)
    else:
        linea("  FIRMA INVALIDA — El mensaje fue alterado.", "invalida")
        etiqueta_resultado.config(text="  ✘  FIRMA INVALIDA", fg=ROJO, bg=CARD)

    area_resultado.config(state=tk.DISABLED)


# ── Funciones de explorador de archivos ───────────────────────────────────────
def buscar_llave():
    ruta = filedialog.askopenfilename(
        title="Selecciona el archivo de llave publica",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")]
    )
    if ruta:
        var_llave.set(ruta)

def buscar_mensaje():
    ruta = filedialog.askopenfilename(
        title="Selecciona el archivo del mensaje firmado",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos", "*.*")]
    )
    if ruta:
        var_mensaje.set(ruta)


# ── Ventana principal ──────────────────────────────────────────────────────────
ventana = tk.Tk()
ventana.title("Verificador ECDSA")
ventana.configure(bg=BG)
ventana.resizable(False, False)

var_llave   = tk.StringVar()
var_mensaje = tk.StringVar()

# -- Header
header = tk.Frame(ventana, bg=CARD, pady=16)
header.pack(fill="x")
tk.Label(header, text="Verificador de Firma Digital",
         bg=CARD, fg=TEXTO, font=("Segoe UI", 15, "bold")).pack()
tk.Label(header, text="ECDSA  •  Curva SECP256k1  •  SHA-256",
         bg=CARD, fg=TEXTO_DIM, font=("Segoe UI", 9)).pack(pady=(2, 0))

separador(ventana)

# -- Tarjeta de inputs
card = tk.Frame(ventana, bg=CARD, pady=10)
card.pack(fill="x", padx=16, pady=8)

# Seccion 1: llave publica
etiqueta_seccion(card, "1", "Llave publica del emisor (.txt)")
entrada_llave = fila_entrada(card, var_llave, buscar_llave)

separador(card)

# Seccion 2: mensaje
etiqueta_seccion(card, "2", "Archivo del mensaje firmado (.txt)")
entrada_mensaje = fila_entrada(card, var_mensaje, buscar_mensaje)

separador(card)

# Seccion 3: firma
etiqueta_seccion(card, "3", "Firma hexadecimal  (128 chars: r || s)")
entrada_firma = tk.Text(card, height=3, bg=BG, fg=TEXTO,
                        insertbackground=TEXTO, relief="flat",
                        font=("Courier New", 9), wrap=tk.WORD, bd=0)
entrada_firma.pack(fill="x", padx=20, pady=(0, 10), ipady=6)

# -- Boton verificar
btn_verificar = tk.Button(ventana, text="  Verificar firma  ",
                          command=verificar,
                          bg=AZUL, fg="white", activebackground=AZUL_HOVER,
                          activeforeground="white",
                          font=("Segoe UI", 11, "bold"),
                          relief="flat", cursor="hand2",
                          pady=10, padx=20, bd=0)
btn_verificar.pack(pady=12)
hacer_hover(btn_verificar, AZUL, AZUL_HOVER)

# -- Etiqueta resultado rapido
etiqueta_resultado = tk.Label(ventana, text="",
                              bg=CARD, fg=TEXTO,
                              font=("Segoe UI", 12, "bold"),
                              pady=8, padx=16)
etiqueta_resultado.pack(fill="x", padx=16)

# -- Area de log detallado
tk.Label(ventana, text="Detalle del proceso",
         bg=BG, fg=TEXTO_DIM,
         font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=20, pady=(8, 2))

area_resultado = scrolledtext.ScrolledText(ventana, height=16, width=84,
                                           bg="#0d1117", fg="#c9d1d9",
                                           insertbackground=TEXTO,
                                           relief="flat", bd=0,
                                           font=("Courier New", 9),
                                           state=tk.DISABLED)
area_resultado.pack(padx=16, pady=(0, 16))

# Tags de color en el log
area_resultado.tag_config("titulo",   foreground=AZUL,  font=("Courier New", 9, "bold"))
area_resultado.tag_config("valida",   foreground=VERDE, font=("Courier New", 9, "bold"))
area_resultado.tag_config("invalida", foreground=ROJO,  font=("Courier New", 9, "bold"))

ventana.mainloop()

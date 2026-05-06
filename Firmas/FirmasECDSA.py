import flet as ft
from ecdsa import SigningKey, VerifyingKey, NIST256p
from ecdsa.ellipticcurve import Point
import hashlib
import base64
import os

def main(page: ft.Page):
    page.title = "Sistema de Integridad ECDSA"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 700
    page.window_height = 600
    page.scroll = ft.ScrollMode.AUTO

    ## VARIABLES DE ESTADO
    txt_nombre_gen = ft.TextField(label="Tu Nombre", hint_text="Ej: Alicia")
    
    txt_emisor_firma = ft.TextField(label="Nombre del Emisor (Quien firma)", hint_text="Nombre que aparecerá en el documento")
    ruta_privada = ft.Text("Llave privada no seleccionada", color=ft.colors.RED)
    ruta_decalogo = ft.Text("Archivo (.txt) no seleccionado", color=ft.colors.RED)
    
    ruta_publica = ft.Text("Llave pública no seleccionada", color=ft.colors.RED)
    ruta_firmado = ft.Text("Archivo firmado no seleccionado", color=ft.colors.RED)
    status_verif = ft.Text("", weight="bold", size=20)
    
    SEPARADOR = "\n\n--- SELLO DIGITAL ECDSA (NO MODIFICAR ESTA LÍNEA NI LO SIGUIENTE) ---\n"

    ## MANEJADORES DE ARCHIVOS
    def on_priv_res(e):
        if e.files:
            ruta_privada.value = e.files[0].path
            ruta_privada.color = ft.colors.GREEN
            page.update()

    def on_decalogo_res(e):
        if e.files:
            ruta_decalogo.value = e.files[0].path
            ruta_decalogo.color = ft.colors.GREEN
            page.update()

    def on_pub_res(e):
        if e.files:
            ruta_publica.value = e.files[0].path
            ruta_publica.color = ft.colors.GREEN
            page.update()

    def on_firmado_res(e):
        if e.files:
            ruta_firmado.value = e.files[0].path
            ruta_firmado.color = ft.colors.GREEN
            page.update()

    fp_priv = ft.FilePicker(on_result=on_priv_res)
    fp_dec = ft.FilePicker(on_result=on_decalogo_res)
    fp_pub = ft.FilePicker(on_result=on_pub_res)
    fp_fmd = ft.FilePicker(on_result=on_firmado_res)
    page.overlay.extend([fp_priv, fp_dec, fp_pub, fp_fmd])

    # --- LÓGICA 1: GENERACIÓN ---
    def generar_llaves_click(e):
        nombre = txt_nombre_gen.value.strip()
        if not nombre:
            txt_nombre_gen.error_text = "Se requiere un nombre"; page.update(); return
        
        sk = SigningKey.generate(curve=NIST256p)
        d = sk.privkey.secret_multiplier
        ##Equivalente a Q = d x G

        Q = sk.verifying_key
        
        with open(f"{nombre}_privada.txt", "w") as f: f.write(str(d))
        with open(f"{nombre}_publica.txt", "w") as f: f.write(f"X: {Q.pubkey.point.x()}\nY: {Q.pubkey.point.y()}")
        page.snack_bar = ft.SnackBar(ft.Text(f"Llaves de {nombre} creadas.")); page.snack_bar.open = True; page.update()

    # --- LÓGICA 2: FIRMA (CON NOMBRE DINÁMICO) ---
    def on_firmar_click(e):
        nombre = txt_emisor_firma.value.strip()
        if not nombre:
            txt_emisor_firma.error_text = "Escribe quién firma el documento"; page.update(); return
        if "no seleccionada" in ruta_privada.value or "no seleccionado" in ruta_decalogo.value:
            page.snack_bar = ft.SnackBar(ft.Text("Faltan archivos")); page.snack_bar.open = True; page.update(); return
            
        try:
            with open(ruta_privada.value, 'r') as f: d_val = int(f.read().strip())
            with open(ruta_decalogo.value, 'r', encoding='utf-8') as f: texto_base = f.read().strip()

            mensaje_completo = f"EMISOR: {nombre}\n\n{texto_base}"
            ##  Esta línea dice: Usa esta curva y mi secreto d para prepararte para firmar
            sk = SigningKey.from_secret_exponent(d_val, curve=NIST256p)

            mensaje_en_bytes =mensaje_completo.encode('utf-8')
            firma_b64 = base64.b64encode(sk.sign(mensaje_en_bytes, hashfunc=hashlib.sha256)).decode('utf-8')

            # --- LÓGICA DE NOMBRE DINÁMICO ---
            archivo_origen = os.path.basename(ruta_decalogo.value)
            nombre_base = os.path.splitext(archivo_origen)[0]
            nombre_final = f"{nombre_base}_Firmado_por_{nombre}.txt"

            with open(nombre_final, "w", encoding="utf-8") as f:
                f.write(mensaje_completo)
                f.write(SEPARADOR)
                f.write(firma_b64)

            page.snack_bar = ft.SnackBar(ft.Text(f"Archivo creado: {nombre_final}")); page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}")); page.snack_bar.open = True
        page.update()

    # --- LÓGICA 3: VERIFICACIÓN ---
    def verificar_click(e):
        if "no seleccionada" in ruta_publica.value or "no seleccionado" in ruta_firmado.value:
            status_verif.value = "Faltan archivos"; page.update(); return
        try:
            with open(ruta_publica.value, 'r') as f:
                ## Reconstrucción de la Clave Pública Q
                lines = f.readlines()
                x = int(lines[0].split(":")[1].strip())
                y = int(lines[1].split(":")[1].strip())

            vk = VerifyingKey.from_public_point(Point(NIST256p.curve, x, y), curve=NIST256p)

            with open(ruta_firmado.value, 'r', encoding='utf-8') as f: contenido = f.read()
            
            partes = contenido.split(SEPARADOR)

            mensaje_leido = partes[0]
            firma_leida_b64 = partes[1].strip()
            
            if vk.verify(base64.b64decode(firma_leida_b64), mensaje_leido.encode('utf-8'), hashfunc=hashlib.sha256):
                status_verif.value = "FIRMA VÁLIDA: Documento Íntegro"; status_verif.color = ft.colors.GREEN
            else:
                status_verif.value = "FIRMA INVÁLIDA: ¡Manipulado!"; status_verif.color = ft.colors.RED
        except:
            status_verif.value = "ERROR: Verificación fallida"; status_verif.color = ft.colors.RED
        page.update()

    # --- NAVEGACIÓN ---
    def navegar(p):
        v_menu.visible = v_gen.visible = v_firm.visible = v_ver.visible = False
        p.visible = True; page.update()

    v_gen = ft.Column([
        ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: navegar(v_menu)), ft.Text("1. Generar Identidad", size=20, weight="bold")]),
        txt_nombre_gen,
        ft.ElevatedButton("Generar y Guardar Llaves (.txt)", icon=ft.icons.KEY, on_click=generar_llaves_click)
    ], visible=False)

    v_firm = ft.Column([
        ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: navegar(v_menu)), ft.Text("2. Firmar Documento", size=20, weight="bold")]),
        txt_emisor_firma,
        ft.Row([ft.ElevatedButton("Subir Mi Llave Privada", on_click=lambda _: fp_priv.pick_files()), ruta_privada]),
        ft.Row([ft.ElevatedButton("Subir Documento (.txt)", on_click=lambda _: fp_dec.pick_files()), ruta_decalogo]),
        ft.ElevatedButton("Firmar y Unir Archivo", icon=ft.icons.DRAW, on_click=on_firmar_click),
    ], visible=False)

    v_ver = ft.Column([
        ft.Row([ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: navegar(v_menu)), ft.Text("3. Verificar Integridad", size=20, weight="bold")]),
        ft.Row([ft.ElevatedButton("Subir Llave Pública del Emisor", on_click=lambda _: fp_pub.pick_files()), ruta_publica]),
        ft.Row([ft.ElevatedButton("Subir Archivo Firmado", on_click=lambda _: fp_fmd.pick_files()), ruta_firmado]),
        ft.ElevatedButton("Validar Autenticidad", icon=ft.icons.CHECK_CIRCLE, on_click=verificar_click),
        status_verif
    ], visible=False)

    v_menu = ft.Column([
        ft.Text("Firma Digital ECDSA - Integridad", size=32, weight="bold", color=ft.colors.BLUE_800),
        ft.Row([
            ft.Container(ft.Text("Generar", color="white", weight="bold"), bgcolor=ft.colors.BLUE_700, width=150, height=120, border_radius=15, alignment=ft.Alignment(0,0), on_click=lambda _: navegar(v_gen)),
            ft.Container(ft.Text("Firmar", color="white", weight="bold"), bgcolor=ft.colors.BLUE_800, width=150, height=120, border_radius=15, alignment=ft.Alignment(0,0), on_click=lambda _: navegar(v_firm)),
            ft.Container(ft.Text("Verificar", color="white", weight="bold"), bgcolor=ft.colors.BLUE_900, width=150, height=120, border_radius=15, alignment=ft.Alignment(0,0), on_click=lambda _: navegar(v_ver)),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.add(v_menu, v_gen, v_firm, v_ver)

if __name__ == "__main__":
    ft.app(target=main)
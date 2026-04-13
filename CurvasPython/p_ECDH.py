import flet as ft
import random

# --------- UTILIDADES ---------
def inverso(n, p):
    return pow(n, -1, p)


def validar_curva(a, b, p):
    delta = (4 * (a ** 3) + 27 * (b ** 2)) % p
    return delta != 0, delta


def sqrt_mod(n, p):
    return [y for y in range(p) if (y*y) % p == n]


def sumar_puntos(P, Q, a, p):
    if P is None:
        return Q, None
    if Q is None:
        return P, None
    
    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and y1 == y2:
        return doblar_punto(P, a, p)
    
    if x1 == x2:
        return None, None

    num = (y2 - y1) % p
    den = (x2 - x1) % p

    lam = (num * inverso(den, p)) % p

    x3 = (lam**2 - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p

    return (x3, y3), lam


def doblar_punto(P, a, p):
    if P is None:
        return None, None
    
    x1, y1 = P

    num = (3*(x1**2) + a) % p
    den = (2*y1) % p

    if den == 0:
        return None, None

    lam = (num * inverso(den, p)) % p

    x3 = (lam**2 - 2*x1) % p
    y3 = (lam*(x1 - x3) - y1) % p

    return (x3, y3), lam


def multiplicacion_escalar(P, n, a, p):
    resultado = None
    actual = P
    pasos = []

    while n > 0:
        if n % 2 == 1:
            if resultado is None:
                resultado = actual
            else:
                resultado, _ = sumar_puntos(resultado, actual, a, p)
            pasos.append(f"Sumar: {resultado}")

        actual, _ = doblar_punto(actual, a, p)
        pasos.append(f"Doblar: {actual}")

        n //= 2

    return resultado, pasos


def obtener_todos_puntos(a, b, p):
    puntos = []
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        ys = sqrt_mod(rhs, p)
        for y in ys:
            puntos.append((x, y))
    
    puntos.append(None)
    return puntos


def punto_to_str(punto):
    if punto is None:
        return "INF"
    return f"({punto[0]},{punto[1]})"


def generar_tabla_sumas(puntos, a, p):
    tabla = []
    header = [" "] + [punto_to_str(pt) for pt in puntos]
    tabla.append(header)
    
    for pi in puntos:
        fila = [punto_to_str(pi)]
        for pj in puntos:
            punto_resultado, _ = sumar_puntos(pi, pj, a, p)
            fila.append(punto_to_str(punto_resultado))
        tabla.append(fila)
    
    return tabla


def generar_tabla_multiplicacion(puntos_afines, a, p, orden):
    tabla = []
    header = [" "] + [f"{k}P" for k in range(1, orden + 1)]
    tabla.append(header)
    
    for punto in puntos_afines:
        fila = [punto_to_str(punto)]
        actual = punto
        
        for k in range(1, orden + 1):
            fila.append(punto_to_str(actual))
            actual, _ = sumar_puntos(actual, punto, a, p)
            
        tabla.append(fila)
    
    return tabla


def obtener_generadores(puntos_afines, a, p, orden):
    generadores = []
    for punto in puntos_afines:
        visitados = set()
        actual = punto
        es_generador = True
        
        for k in range(1, orden + 1):
            str_punto = punto_to_str(actual)
            if str_punto in visitados and k < orden:
                es_generador = False
                break
            visitados.add(str_punto)
            actual, _ = sumar_puntos(actual, punto, a, p)
        
        if es_generador and len(visitados) == orden:
            generadores.append(punto)
    return generadores


def tabla_a_texto(tabla):
    ancho_cols = [max(len(str(tabla[i][j])) for i in range(len(tabla))) for j in range(len(tabla[0]))]
    
    texto = ""
    for fila in tabla:
        for j, celda in enumerate(fila):
            texto += str(celda).ljust(ancho_cols[j] + 2)
        texto += "\n"
    
    return texto


# --------- APP ---------
def main(page: ft.Page):
    page.title = "Curvas Elipticas + ECDH"
    page.scroll = "auto"

    # ========== SECCION DE CURVA ==========
    curve_title = ft.Text("Curva: y2 = x3 + ax + b mod p", size=20, weight="bold")
    a_input = ft.TextField(label="a", width=80)
    b_input = ft.TextField(label="b", width=80)
    p_input = ft.TextField(label="p", width=80)
    validate_btn = ft.ElevatedButton("Validar curva + puntos")
    curve_output = ft.Column()

    # ========== SECCION SUMA ==========
    sum_title = ft.Text("Suma de puntos (P + Q)", size=18, weight="bold")
    p1_x = ft.TextField(label="x1", width=80)
    p1_y = ft.TextField(label="y1", width=80)
    p2_x = ft.TextField(label="x2", width=80)
    p2_y = ft.TextField(label="y2", width=80)
    sum_btn = ft.ElevatedButton("Sumar")
    sum_output = ft.Column()

    # ========== SECCION DOBLADO ==========
    dbl_title = ft.Text("Doblado de punto (2P)", size=18, weight="bold")
    dbl_x = ft.TextField(label="x", width=80)
    dbl_y = ft.TextField(label="y", width=80)
    dbl_btn = ft.ElevatedButton("Doblar")
    dbl_output = ft.Column()

    # ========== SECCION MULTIPLICACION ESCALAR ==========
    mul_title = ft.Text("Multiplicacion escalar (k*P)", size=18, weight="bold")
    mul_x = ft.TextField(label="x", width=80)
    mul_y = ft.TextField(label="y", width=80)
    mul_k = ft.TextField(label="k (escalar)", width=100)
    mul_btn = ft.ElevatedButton("Multiplicar")
    mul_output = ft.Column()

    # ========== SECCION AVANZADA: TABLAS ==========
    tabla_sumas_title = ft.Text("Tabla de Sumas (P + Q)", size=18, weight="bold")
    tabla_sumas_btn = ft.ElevatedButton("Generar Tabla de Sumas")
    tabla_sumas_output = ft.Column()

    tabla_mul_title = ft.Text("Tabla de Multiplicacion Escalar (kP)", size=18, weight="bold")
    tabla_mul_btn = ft.ElevatedButton("Generar Tabla de Multiplicacion")
    tabla_mul_output = ft.Column()

    # ========== SECCION GENERADORES ==========
    gen_title = ft.Text("Identificar Generadores", size=18, weight="bold")
    gen_btn = ft.ElevatedButton("Buscar Puntos Generadores")
    gen_output = ft.Column()

    # ========== SECCION ECDH ==========
    ecdh_title = ft.Text("ECDH - Intercambio de Claves Diffie-Hellman", size=20, weight="bold")

    _tf_ecdh = dict(width=130, text_size=14, dense=True)
    ecdh_gx = ft.TextField(label="Gx (generador)", value="3", **_tf_ecdh)
    ecdh_gy = ft.TextField(label="Gy (generador)", value="6", **_tf_ecdh)
    ecdh_ka = ft.TextField(label="ka (Alice)", value="", hint_text="vacio=aleatorio", **_tf_ecdh)
    ecdh_kb = ft.TextField(label="kb (Bob)", value="", hint_text="vacio=aleatorio", **_tf_ecdh)

    nota_condiciones = ft.Container(
        content=ft.Column([
            ft.Text("  Condiciones para las claves privadas (ka, kb):", size=13, weight="bold", color="#e65100"),
            ft.Text("  * Deben ser enteros positivos: 1 < ka, kb < p", size=12, color="#bf360c"),
            ft.Text("  * ka y kb deben ser menores que el orden del subgrupo generado por G", size=12, color="#bf360c"),
            ft.Text("  * G debe ser un punto valido sobre la curva verificada arriba", size=12, color="#bf360c"),
            ft.Text("  * Si se dejan vacios, se generan de forma aleatoria entre 2 y 20", size=12, color="#666666", italic=True),
        ], spacing=2),
        bgcolor="#fff3e0",
        border=ft.border.all(1, "#ff9800"),
        border_radius=8,
        padding=10,
    )

    ecdh_btn = ft.ElevatedButton("Ejecutar ECDH")
    ecdh_output = ft.Column()

    # ========== ESTADOS ==========
    curve_valid = False
    validated_params = None
    puntos_curva = []

    # ========== VALIDACIONES ==========
    def verificar_curva_operacion(operacion_output):
        try:
            a_act = int(a_input.value)
            b_act = int(b_input.value)
            p_act = int(p_input.value)
        except ValueError:
            operacion_output.controls.append(ft.Text("Error: Los valores deben ser enteros."))
            page.update()
            return None

        if not curve_valid or validated_params is None or validated_params != (a_act, b_act, p_act):
            operacion_output.controls.append(ft.Text("La curva no ha sido validada o cambio. Presiona 'Validar'."))
            page.update()
            return None
        return (a_act, b_act, p_act)

    def validar_curva_action(e):
        nonlocal curve_valid, validated_params, puntos_curva
        curve_output.controls.clear()

        for campo in [p1_x, p1_y, p2_x, p2_y, dbl_x, dbl_y, mul_x, mul_y, mul_k]:
            campo.value = ""
        
        for salida in [sum_output, dbl_output, mul_output, 
                    tabla_sumas_output, tabla_mul_output, gen_output, ecdh_output]:
            salida.controls.clear()

        # Reset ECDH visual
        alice_priv.value = "ka = ?"
        alice_pub.value = "ka*G = ?"
        alice_secret.value = "S = ___"
        bob_priv.value = "kb = ?"
        bob_pub.value = "kb*G = ?"
        bob_secret.value = "S = ___"
        flecha_alice_label.value = "valor\ncompartido"
        flecha_bob_label.value = "valor\ncompartido"
        ecdh_resultado.value = ""

        try:
            a, b, p = int(a_input.value), int(b_input.value), int(p_input.value)
        except ValueError:
            curve_output.controls.append(ft.Text("Error: Valores deben ser enteros.", color="red"))
            seccion_operaciones.visible = False
            page.update()
            return

        valida, delta = validar_curva(a, b, p)
        curve_output.controls.append(ft.Text(f"Delta = {delta} mod {p}"))
        
        if not valida:
            curve_output.controls.append(ft.Text("Curva NO valida (discriminante cero).", color="red"))
            curve_valid = False
            seccion_operaciones.visible = False
            page.update()
            return

        curve_valid = True
        seccion_operaciones.visible = True
        validated_params = (a, b, p)
        
        puntos_curva = obtener_todos_puntos(a, b, p)
        puntos_afines = [pt for pt in puntos_curva if pt is not None]
        orden = len(puntos_curva)
        lista_puntos_str = ", ".join([punto_to_str(pt) for pt in puntos_curva])
        
        curve_output.controls.append(ft.Text("Curva valida", color="green"))
        curve_output.controls.append(ft.Text(f"Puntos en E: {lista_puntos_str}", size=10))
        curve_output.controls.append(ft.Text(f"Orden |E| = {orden}", weight="bold", color="blue"))
        page.update()

    # ========== ECDH: PERSONA ICONO ==========
    def persona_icon(color_circulo, color_cuerpo):
        return ft.Column([
            ft.Container(width=40, height=40, bgcolor=color_circulo, border_radius=20),
            ft.Container(
                width=70, height=35, bgcolor=color_cuerpo,
                border_radius=ft.BorderRadius(35, 35, 0, 0),
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)

    # ========== ECDH: ELEMENTOS VISUALES ==========
    ecdh_resultado = ft.Text("", size=18, weight="bold", color="#333333")

    alice_nombre = ft.Text("Alicia", size=18, color="#e91e63", weight="bold")
    alice_priv = ft.Text("ka = ?", size=14, color="#e91e63")
    alice_pub = ft.Text("ka*G = ?", size=14, color="#e91e63")
    alice_secret = ft.Text("S = ___", size=20, color="#e91e63", weight="bold")

    bob_nombre = ft.Text("Bob", size=18, color="#0d47a1", weight="bold")
    bob_priv = ft.Text("kb = ?", size=14, color="#0d47a1")
    bob_pub = ft.Text("kb*G = ?", size=14, color="#0d47a1")
    bob_secret = ft.Text("S = ___", size=20, color="#0d47a1", weight="bold")

    flecha_alice_label = ft.Text("valor\ncompartido", size=12, color="#e91e63",
                                  weight="bold", text_align=ft.TextAlign.CENTER)
    flecha_bob_label = ft.Text("valor\ncompartido", size=12, color="#00bcd4",
                                weight="bold", text_align=ft.TextAlign.CENTER)

    nube = ft.Container(
        content=ft.Stack([
            ft.Container(
                width=300, height=140,
                bgcolor="#e8eaf6",
                border_radius=70,
                border=ft.border.all(3, "#3f51b5"),
            ),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ARROW_FORWARD, color="#e91e63", size=20),
                    flecha_alice_label,
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                left=20, top=15, width=150, height=50,
            ),
            ft.Container(
                content=ft.Row([
                    flecha_bob_label,
                    ft.Icon(ft.Icons.ARROW_BACK, color="#00bcd4", size=20),
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                right=20, bottom=15, width=150, height=50,
            ),
        ]),
        width=300, height=140,
    )

    alice_col = ft.Column([
        persona_icon("#f48fb1", "#f06292"),
        alice_nombre,
        alice_priv,
        alice_pub,
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

    bob_col = ft.Column([
        persona_icon("#5c6bc0", "#283593"),
        bob_nombre,
        bob_priv,
        bob_pub,
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)

    # ========== CONTENEDOR DE OPERACIONES (Inicialmente oculto) ==========
    seccion_operaciones = ft.Column(
        visible=False, 
        controls=[
            sum_title, ft.Row([p1_x, p1_y]), ft.Row([p2_x, p2_y]), sum_btn, sum_output, ft.Divider(),
            dbl_title, ft.Row([dbl_x, dbl_y]), dbl_btn, dbl_output, ft.Divider(),
            mul_title, ft.Row([mul_x, mul_y]), mul_k, mul_btn, mul_output, ft.Divider(),
            tabla_sumas_title, tabla_sumas_btn, tabla_sumas_output, ft.Divider(),
            tabla_mul_title, tabla_mul_btn, tabla_mul_output, ft.Divider(),
            gen_title, gen_btn, gen_output,
            ft.Divider(height=3, color="#3f51b5"),
            # ===== ECDH =====
            ecdh_title,
            ft.Row([ecdh_gx, ecdh_gy], spacing=10),
            ft.Row([ecdh_ka, ecdh_kb], spacing=10),
            nota_condiciones,
            ecdh_btn,
            ft.Container(height=10),
            ft.Row([
                alice_col,
                nube,
                bob_col,
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
               vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Container(height=10),
            ft.Row([
                alice_secret,
                bob_secret,
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Container(height=5),
            ecdh_resultado,
            ft.Container(height=10),
            ecdh_output,
        ]
    )

    # ========== EVENTOS ==========
    def sumar_action(e):
        sum_output.controls.clear()
        params = verificar_curva_operacion(sum_output)
        if not params: return
        a, b, p = params

        try:
            P = (int(p1_x.value), int(p1_y.value))
            Q = (int(p2_x.value), int(p2_y.value))
            R, lam = sumar_puntos(P, Q, a, p)
            
            if lam is not None: sum_output.controls.append(ft.Text(f"lam = {lam}"))
            sum_output.controls.append(ft.Text(f"P + Q = {punto_to_str(R)}"))
        except Exception as ex:
            sum_output.controls.append(ft.Text(f"Error: {ex}", color="red"))
        page.update()

    def doblar_action(e):
        dbl_output.controls.clear()
        params = verificar_curva_operacion(dbl_output)
        if not params: return
        a, b, p = params

        try:
            P = (int(dbl_x.value), int(dbl_y.value))
            R, lam = doblar_punto(P, a, p)
            
            if lam is not None: dbl_output.controls.append(ft.Text(f"lam = {lam}"))
            dbl_output.controls.append(ft.Text(f"2P = {punto_to_str(R)}"))
        except Exception as ex:
            dbl_output.controls.append(ft.Text(f"Error: {ex}", color="red"))
        page.update()

    def multiplicar_action(e):
        mul_output.controls.clear()
        params = verificar_curva_operacion(mul_output)
        if not params: return
        a, b, p = params

        try:
            P = (int(mul_x.value), int(mul_y.value))
            k = int(mul_k.value)
            R, pasos = multiplicacion_escalar(P, k, a, p)
            mul_output.controls.append(ft.Text(f"{k}P = {punto_to_str(R)}", size=18))
        except Exception as ex:
            mul_output.controls.append(ft.Text(f"Error: {ex}", color="red"))
        page.update()

    def generar_tabla_sumas_action(e):
        tabla_sumas_output.controls.clear()
        params = verificar_curva_operacion(tabla_sumas_output)
        if not params: return
        a, b, p = params

        try:
            tabla = generar_tabla_sumas(puntos_curva, a, p)
            texto = tabla_a_texto(tabla)
            tabla_sumas_output.controls.append(ft.Text(texto, font_family="monospace", size=10))
        except Exception as ex:
            tabla_sumas_output.controls.append(ft.Text(f"Error: {ex}", color="red"))
        page.update()

    def generar_tabla_mul_action(e):
        tabla_mul_output.controls.clear()
        params = verificar_curva_operacion(tabla_mul_output)
        if not params: return
        a, b, p = params
        
        puntos_afines = [pt for pt in puntos_curva if pt is not None]

        try:
            tabla = generar_tabla_multiplicacion(puntos_afines, a, p, len(puntos_curva))
            texto = tabla_a_texto(tabla)
            tabla_mul_output.controls.append(ft.Text(texto, font_family="monospace", size=10))
        except Exception as ex:
            tabla_mul_output.controls.append(ft.Text(f"Error: {ex}", color="red"))
        page.update()

    def identificar_generadores_action(e):
        gen_output.controls.clear()
        params = verificar_curva_operacion(gen_output)
        if not params: return
        a, b, p = params

        puntos_afines = [pt for pt in puntos_curva if pt is not None]
        orden = len(puntos_curva)

        gens = obtener_generadores(puntos_afines, a, p, orden)

        if gens:
            txt = f"Se encontraron {len(gens)} generadores:\n"
            txt += ", ".join([punto_to_str(g) for g in gens])
            gen_output.controls.append(ft.Text(txt, color="blue", weight="bold"))
        else:
            gen_output.controls.append(ft.Text("No se encontraron generadores (el grupo podria no ser ciclico).", color="orange"))
        page.update()

    # ========== ECDH: ACCION ==========
    def ejecutar_ecdh(e):
        ecdh_output.controls.clear()
        params = verificar_curva_operacion(ecdh_output)
        if not params:
            return
        ca, cb, cp = params

        try:
            gx = int(ecdh_gx.value)
            gy = int(ecdh_gy.value)
            G = (gx, gy)
        except ValueError:
            ecdh_resultado.value = "G debe ser un punto con coordenadas enteras."
            ecdh_resultado.color = "#c62828"
            page.update()
            return

        # Verificar que G esta en la curva
        lhs = (G[1] ** 2) % cp
        rhs = (G[0] ** 3 + ca * G[0] + cb) % cp
        if lhs != rhs:
            ecdh_resultado.value = f"G = {punto_to_str(G)} no pertenece a la curva."
            ecdh_resultado.color = "#c62828"
            page.update()
            return

        # Leer o generar claves privadas
        ka_text = ecdh_ka.value.strip()
        kb_text = ecdh_kb.value.strip()

        try:
            a_priv = int(ka_text) if ka_text else random.randint(2, 20)
            b_priv = int(kb_text) if kb_text else random.randint(2, 20)
        except ValueError:
            ecdh_resultado.value = "Las claves privadas deben ser enteros."
            ecdh_resultado.color = "#c62828"
            page.update()
            return

        if a_priv < 2 or a_priv >= cp:
            ecdh_resultado.value = f"ka = {a_priv} no valido. Debe cumplir: 1 < ka < p ({cp})"
            ecdh_resultado.color = "#c62828"
            page.update()
            return
        if b_priv < 2 or b_priv >= cp:
            ecdh_resultado.value = f"kb = {b_priv} no valido. Debe cumplir: 1 < kb < p ({cp})"
            ecdh_resultado.color = "#c62828"
            page.update()
            return

        # Claves publicas
        A_pub, _ = multiplicacion_escalar(G, a_priv, ca, cp)
        B_pub, _ = multiplicacion_escalar(G, b_priv, ca, cp)

        # Secretos compartidos
        S1, _ = multiplicacion_escalar(B_pub, a_priv, ca, cp)
        S2, _ = multiplicacion_escalar(A_pub, b_priv, ca, cp)

        # Actualizar diagrama visual
        alice_priv.value = f"ka = {a_priv}"
        alice_pub.value = f"ka*G = {punto_to_str(A_pub)}"
        bob_priv.value = f"kb = {b_priv}"
        bob_pub.value = f"kb*G = {punto_to_str(B_pub)}"

        flecha_alice_label.value = f"A = {punto_to_str(A_pub)}"
        flecha_bob_label.value = f"B = {punto_to_str(B_pub)}"

        alice_secret.value = f"S = {punto_to_str(S1)}"
        bob_secret.value = f"S = {punto_to_str(S2)}"

        coincide = S1 == S2

        if coincide:
            ecdh_resultado.value = "Intercambio exitoso! Ambos calcularon el mismo secreto."
            ecdh_resultado.color = "#2e7d32"
        else:
            ecdh_resultado.value = "Error en el intercambio."
            ecdh_resultado.color = "#c62828"

        # Detalle del proceso
        color_res = "#66bb6a" if coincide else "#ef5350"
        detalle = ft.Container(
            content=ft.Column([
                ft.Text("Detalle del proceso ECDH", size=16, weight="bold", color="#64b5f6"),
                ft.Divider(height=1, color="#555555"),
                ft.Text(f"Curva: y2 = x3 + {ca}x + {cb}  (mod {cp})", size=13, font_family="monospace", color="#e0e0e0"),
                ft.Text(f"Generador: G = {punto_to_str(G)}", size=13, font_family="monospace", color="#e0e0e0"),
                ft.Divider(height=1, color="#555555"),
                ft.Text("Alice:", size=14, weight="bold", color="#f48fb1"),
                ft.Text(f"   Clave privada:  ka = {a_priv}", size=13, font_family="monospace", color="#e0e0e0"),
                ft.Text(f"   Clave publica:  A = ka*G = {a_priv}*{punto_to_str(G)} = {punto_to_str(A_pub)}", size=13, font_family="monospace", color="#e0e0e0"),
                ft.Text(f"   Secreto:  S = ka*B = {a_priv}*{punto_to_str(B_pub)} = {punto_to_str(S1)}", size=13, font_family="monospace", color="#e0e0e0"),
                ft.Divider(height=1, color="#555555"),
                ft.Text("Bob:", size=14, weight="bold", color="#64b5f6"),
                ft.Text(f"   Clave privada:  kb = {b_priv}", size=13, font_family="monospace", color="#e0e0e0"),
                ft.Text(f"   Clave publica:  B = kb*G = {b_priv}*{punto_to_str(G)} = {punto_to_str(B_pub)}", size=13, font_family="monospace", color="#e0e0e0"),
                ft.Text(f"   Secreto:  S = kb*A = {b_priv}*{punto_to_str(A_pub)} = {punto_to_str(S2)}", size=13, font_family="monospace", color="#e0e0e0"),
                ft.Divider(height=1, color="#555555"),
                ft.Text(f"Secreto compartido = {punto_to_str(S1)}", size=15, weight="bold", color=color_res),
                ft.Text("   ka*(kb*G) = kb*(ka*G) = ka*kb*G", size=12, italic=True, color="#bdbdbd"),
            ], spacing=4),
            bgcolor="#2a2a3d",
            border=ft.border.all(2, "#3f51b5"),
            border_radius=10,
            padding=15,
        )
        ecdh_output.controls.append(detalle)
        page.update()

    validate_btn.on_click = validar_curva_action
    sum_btn.on_click = sumar_action
    dbl_btn.on_click = doblar_action
    mul_btn.on_click = multiplicar_action
    tabla_sumas_btn.on_click = generar_tabla_sumas_action
    tabla_mul_btn.on_click = generar_tabla_mul_action
    gen_btn.on_click = identificar_generadores_action
    ecdh_btn.on_click = ejecutar_ecdh

    # ========== ARMADO ==========
    page.add(
        ft.Column([
            curve_title, 
            ft.Row([a_input, b_input, p_input]), 
            validate_btn, 
            curve_output, 
            ft.Divider(),
            seccion_operaciones,
        ])
    )

ft.app(target=main)
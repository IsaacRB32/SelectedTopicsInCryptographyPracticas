import flet as ft

# --------- UTILIDADES ---------
def inverso(n, p):
    return pow(n, -1, p)


def validar_curva(a, b, p):
    delta = (4 * (a ** 3) + 27 * (b ** 2)) % p
    return delta != 0, delta


def sqrt_mod(n, p):
    return [y for y in range(p) if (y*y) % p == n]


def sumar_puntos(P, Q, a, p):
    """Siempre retorna (Punto_Resultante, Lambda). Si es infinito, retorna None en el respectivo campo."""
    if P is None:  # P es punto infinito
        return Q, None
    if Q is None:  # Q es punto infinito
        return P, None
    
    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and y1 == y2:
        return doblar_punto(P, a, p)
    
    if x1 == x2:  # Puntos opuestos resultan en infinito
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

    if den == 0: # Tangente vertical resulta en infinito
        return None, None

    lam = (num * inverso(den, p)) % p

    x3 = (lam**2 - 2*x1) % p
    y3 = (lam*(x1 - x3) - y1) % p

    return (x3, y3), lam


def multiplicacion_escalar(P, n, a, p):
    resultado = None  # punto infinito
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
    
    puntos.append(None)  # Agregar punto infinito
    return puntos


def punto_to_str(punto):
    if punto is None:
        return "∞"
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
            # Suma acumulativa limpia: kP + P = (k+1)P
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
            actual, _ = sumar_puntos(actual, punto, a, p) # [cite: 2, 10]
        
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
    page.title = "Curvas Elípticas Avanzado"
    page.scroll = "auto"

    # ========== SECCIÓN DE CURVA ==========
    curve_title = ft.Text("Curva: y² = x³ + ax + b mod p", size=20, weight="bold")
    a_input = ft.TextField(label="a", width=80)
    b_input = ft.TextField(label="b", width=80)
    p_input = ft.TextField(label="p", width=80)
    validate_btn = ft.ElevatedButton("Validar curva + puntos")
    curve_output = ft.Column()

    # ========== SECCIÓN SUMA ==========
    sum_title = ft.Text("Suma de puntos (P + Q)", size=18, weight="bold")
    p1_x = ft.TextField(label="x₁", width=80)
    p1_y = ft.TextField(label="y₁", width=80)
    p2_x = ft.TextField(label="x₂", width=80)
    p2_y = ft.TextField(label="y₂", width=80)
    sum_btn = ft.ElevatedButton("Sumar")
    sum_output = ft.Column()

    # ========== SECCIÓN DOBLADO ==========
    dbl_title = ft.Text("Doblado de punto (2P)", size=18, weight="bold")
    dbl_x = ft.TextField(label="x", width=80)
    dbl_y = ft.TextField(label="y", width=80)
    dbl_btn = ft.ElevatedButton("Doblar")
    dbl_output = ft.Column()

    # ========== SECCIÓN MULTIPLICACIÓN ESCALAR ==========
    mul_title = ft.Text("Multiplicación escalar (k·P)", size=18, weight="bold")
    mul_x = ft.TextField(label="x", width=80)
    mul_y = ft.TextField(label="y", width=80)
    mul_k = ft.TextField(label="k (escalar)", width=100)
    mul_btn = ft.ElevatedButton("Multiplicar")
    mul_output = ft.Column()

    # ========== SECCIÓN AVANZADA: TABLAS ==========
    tabla_sumas_title = ft.Text("Tabla de Sumas (P + Q)", size=18, weight="bold")
    tabla_sumas_btn = ft.ElevatedButton("Generar Tabla de Sumas")
    tabla_sumas_output = ft.Column()

    tabla_mul_title = ft.Text("Tabla de Multiplicación Escalar (kP)", size=18, weight="bold")
    tabla_mul_btn = ft.ElevatedButton("Generar Tabla de Multiplicación")
    tabla_mul_output = ft.Column()

    # ========== SECCIÓN GENERADORES ==========
    gen_title = ft.Text("Identificar Generadores", size=18, weight="bold")
    gen_btn = ft.ElevatedButton("Buscar Puntos Generadores")
    gen_output = ft.Column()

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
            operacion_output.controls.append(ft.Text("La curva no ha sido validada o cambió. Presiona 'Validar'."))
            page.update()
            return None
        return (a_act, b_act, p_act)

    def validar_curva_action(e):
        nonlocal curve_valid, validated_params, puntos_curva
        curve_output.controls.clear()

        # Limpiar campos de entrada de todas las secciones
        for campo in [p1_x, p1_y, p2_x, p2_y, dbl_x, dbl_y, mul_x, mul_y, mul_k]:
            campo.value = ""
        
        # Limpiar contenedores de salida de resultados
        for salida in [sum_output, dbl_output, mul_output, 
                    tabla_sumas_output, tabla_mul_output, gen_output]:
            salida.controls.clear()
        try:
            a, b, p = int(a_input.value), int(b_input.value), int(p_input.value)
        except ValueError:
            curve_output.controls.append(ft.Text("Error: Valores deben ser enteros.", color="red"))
            seccion_operaciones.visible = False
            page.update()
            return

        valida, delta = validar_curva(a, b, p)
        curve_output.controls.append(ft.Text(f"Δ = {delta} mod {p}"))
        
        if not valida:
            curve_output.controls.append(ft.Text("Curva NO válida (discriminante cero).", color="red"))
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
        
        curve_output.controls.append(ft.Text("Curva válida", color="green"))
        curve_output.controls.append(ft.Text(f"Puntos en E: {lista_puntos_str}", size=10))
        curve_output.controls.append(ft.Text(f"Orden |E| = {orden}", weight="bold", color="blue"))
        page.update()
        
    # ========== CONTENEDOR DE OPERACIONES (Inicialmente oculto) ==========
    seccion_operaciones = ft.Column(
        visible=False, 
        controls=[
            sum_title, ft.Row([p1_x, p1_y]), ft.Row([p2_x, p2_y]), sum_btn, sum_output, ft.Divider(),
            dbl_title, ft.Row([dbl_x, dbl_y]), dbl_btn, dbl_output, ft.Divider(),
            mul_title, ft.Row([mul_x, mul_y]), mul_k, mul_btn, mul_output, ft.Divider(),
            tabla_sumas_title, tabla_sumas_btn, tabla_sumas_output, ft.Divider(),
            tabla_mul_title, tabla_mul_btn, tabla_mul_output,
            gen_title, gen_btn, gen_output,
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
            
            if lam is not None: sum_output.controls.append(ft.Text(f"λ = {lam}"))
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
            
            if lam is not None: dbl_output.controls.append(ft.Text(f"λ = {lam}"))
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
        orden = len(puntos_curva) # 

        gens = obtener_generadores(puntos_afines, a, p, orden)

        if gens:
            txt = f"Se encontraron {len(gens)} generadores:\n"
            txt += ", ".join([punto_to_str(g) for g in gens])
            gen_output.controls.append(ft.Text(txt, color="blue", weight="bold"))
        else:
            gen_output.controls.append(ft.Text("No se encontraron generadores (el grupo podría no ser cíclico).", color="orange"))
        page.update()

    validate_btn.on_click = validar_curva_action
    sum_btn.on_click = sumar_action
    dbl_btn.on_click = doblar_action
    mul_btn.on_click = multiplicar_action
    tabla_sumas_btn.on_click = generar_tabla_sumas_action
    tabla_mul_btn.on_click = generar_tabla_mul_action
    gen_btn.on_click = identificar_generadores_action

    # ========== ARMADO ==========
    page.add(
        ft.Column([
            curve_title, 
            ft.Row([a_input, b_input, p_input]), 
            validate_btn, 
            curve_output, 
            ft.Divider(),
            seccion_operaciones # Aquí está todo lo demás agrupado
        ])
    )

ft.app(target=main)
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
    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and y1 == y2:
        return doblar_punto(P, a, p)

    num = (y2 - y1) % p
    den = (x2 - x1) % p

    lam = (num * inverso(den, p)) % p

    x3 = (lam**2 - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p

    return (x3, y3), lam


def doblar_punto(P, a, p):
    x1, y1 = P

    num = (3*(x1**2) + a) % p
    den = (2*y1) % p

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


# --------- APP ---------
def main(page: ft.Page):
    page.title = "Curvas Elípticas"
    page.scroll = "auto"

    # ========== SECCIÓN DE CURVA ==========
    curve_title = ft.Text("Curva: y² = x³ + ax + b mod p", size=20, weight="bold")
    a_input = ft.TextField(label="a", width=80)
    b_input = ft.TextField(label="b", width=80)
    p_input = ft.TextField(label="p", width=80)
    validate_btn = ft.ElevatedButton("Validar curva + puntos")

    # Área para mostrar los resultados de validación y lista de puntos
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

    # ========== VARIABLES DE ESTADO DE LA CURVA ==========
    curve_valid = False
    validated_params = None  # (a, b, p)

    # ========== FUNCIONES DE VALIDACIÓN ==========
    def validar_curva_action(e):
        nonlocal curve_valid, validated_params
        curve_output.controls.clear()

        try:
            a = int(a_input.value)
            b = int(b_input.value)
            p = int(p_input.value)
        except ValueError:
            curve_output.controls.append(ft.Text("Error: Los valores de a, b, p deben ser números enteros."))
            curve_valid = False
            validated_params = None
            page.update()
            return

        valida, delta = validar_curva(a, b, p)
        curve_output.controls.append(ft.Text(f"Δ = {delta}"))

        if not valida:
            curve_output.controls.append(ft.Text("Curva NO válida (discriminante cero)."))
            curve_valid = False
            validated_params = None
            page.update()
            return

        curve_valid = True
        validated_params = (a, b, p)
        curve_output.controls.append(ft.Text("Curva válida"))

        # Listar puntos
        puntos = []
        for x in range(p):
            rhs = (x**3 + a*x + b) % p
            ys = sqrt_mod(rhs, p)
            for y in ys:
                puntos.append((x, y))

        curve_output.controls.append(ft.Text("\nPuntos (sin incluir el punto infinito):"))
        # Mostrar en filas de hasta 10 puntos para mejor visualización
        puntos_str = ", ".join([f"({x},{y})" for x, y in puntos])
        curve_output.controls.append(ft.Text(puntos_str))
        curve_output.controls.append(ft.Text(f"|E| = {len(puntos)+1} (incluyendo el punto infinito)"))
        page.update()

    # ========== FUNCIÓN AUXILIAR PARA VERIFICAR CURVA ANTES DE OPERACIONES ==========
    def verificar_curva_operacion(operacion_output):
        try:
            a_act = int(a_input.value)
            b_act = int(b_input.value)
            p_act = int(p_input.value)
        except ValueError:
            operacion_output.controls.append(ft.Text("Error: Los valores de a, b, p deben ser números enteros."))
            page.update()
            return None

        if not curve_valid or validated_params is None:
            operacion_output.controls.append(ft.Text("La curva no ha sido validada o no es válida. Presiona 'Validar curva + puntos'."))
            page.update()
            return None

        a_val, b_val, p_val = validated_params
        if a_act != a_val or b_act != b_val or p_act != p_val:
            operacion_output.controls.append(ft.Text("Los parámetros de la curva han cambiado. Vuelve a validar la curva."))
            page.update()
            return None

        return (a_act, b_act, p_act)

    # ========== FUNCIÓN SUMA ==========
    def sumar_action(e):
        sum_output.controls.clear()

        params = verificar_curva_operacion(sum_output)
        if params is None:
            return

        a, b, p = params

        try:
            P = (int(p1_x.value), int(p1_y.value))
            Q = (int(p2_x.value), int(p2_y.value))
        except ValueError:
            sum_output.controls.append(ft.Text("Error: Verifica que las coordenadas de los puntos sean números enteros."))
            page.update()
            return

        try:
            R, lam = sumar_puntos(P, Q, a, p)
            sum_output.controls.append(ft.Text(f"λ = {lam}"))
            sum_output.controls.append(ft.Text(f"P + Q = {R}"))
        except Exception as ex:
            sum_output.controls.append(ft.Text(f"Error en la suma: {ex}"))
        page.update()

    # ========== FUNCIÓN DOBLADO ==========
    def doblar_action(e):
        dbl_output.controls.clear()

        params = verificar_curva_operacion(dbl_output)
        if params is None:
            return

        a, b, p = params

        try:
            P = (int(dbl_x.value), int(dbl_y.value))
        except ValueError:
            dbl_output.controls.append(ft.Text("Error: Verifica que las coordenadas del punto sean números enteros."))
            page.update()
            return

        try:
            R, lam = doblar_punto(P, a, p)
            dbl_output.controls.append(ft.Text(f"λ = {lam}"))
            dbl_output.controls.append(ft.Text(f"2P = {R}"))
        except Exception as ex:
            dbl_output.controls.append(ft.Text(f"Error en el doblado: {ex}"))
        page.update()

    # ========== FUNCIÓN MULTIPLICACIÓN ==========
    def multiplicar_action(e):
        mul_output.controls.clear()

        params = verificar_curva_operacion(mul_output)
        if params is None:
            return

        a, b, p = params

        try:
            P = (int(mul_x.value), int(mul_y.value))
            k = int(mul_k.value)
        except ValueError:
            mul_output.controls.append(ft.Text("Error: Verifica que las coordenadas del punto y el escalar sean números enteros."))
            page.update()
            return

        try:
            R, pasos = multiplicacion_escalar(P, k, a, p)
            mul_output.controls.append(ft.Text(f"{k}P = {R}", size=18))
            mul_output.controls.append(ft.Text("Pasos:"))
            # Mostrar pasos en un Column para mejor organización
            pasos_col = ft.Column([ft.Text(paso) for paso in pasos])
            mul_output.controls.append(pasos_col)
        except Exception as ex:
            mul_output.controls.append(ft.Text(f"Error en la multiplicación: {ex}"))
        page.update()

    # Asignar eventos a los botones
    validate_btn.on_click = validar_curva_action
    sum_btn.on_click = sumar_action
    dbl_btn.on_click = doblar_action
    mul_btn.on_click = multiplicar_action

    # ========== ARMADO DE LA INTERFAZ ==========
    page.add(
        ft.Column([
            curve_title,
            ft.Row([a_input, b_input, p_input]),
            validate_btn,
            curve_output,
            ft.Divider(),

            sum_title,
            ft.Row([p1_x, p1_y], alignment="start"),
            ft.Row([p2_x, p2_y], alignment="start"),
            sum_btn,
            sum_output,
            ft.Divider(),

            dbl_title,
            ft.Row([dbl_x, dbl_y], alignment="start"),
            dbl_btn,
            dbl_output,
            ft.Divider(),

            mul_title,
            ft.Row([mul_x, mul_y], alignment="start"),
            mul_k,
            mul_btn,
            mul_output,
        ])
    )


ft.app(target=main)
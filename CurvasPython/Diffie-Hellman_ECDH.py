import flet as ft

# --------- UTILIDADES (de p_avanzado.py) ---------
def inverso(n, p):
    return pow(n, -1, p)


def validar_curva(a, b, p):
    delta = (4 * (a ** 3) + 27 * (b ** 2)) % p
    return delta != 0, delta


def sqrt_mod(n, p):
    return [y for y in range(p) if (y * y) % p == n]


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

    x3 = (lam ** 2 - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p

    return (x3, y3), lam


def doblar_punto(P, a, p):
    if P is None:
        return None, None

    x1, y1 = P
    num = (3 * (x1 ** 2) + a) % p
    den = (2 * y1) % p

    if den == 0:
        return None, None

    lam = (num * inverso(den, p)) % p
    x3 = (lam ** 2 - 2 * x1) % p
    y3 = (lam * (x1 - x3) - y1) % p

    return (x3, y3), lam


def multiplicacion_escalar(P, n, a, p):
    resultado = None
    actual = P

    while n > 0:
        if n % 2 == 1:
            if resultado is None:
                resultado = actual
            else:
                resultado, _ = sumar_puntos(resultado, actual, a, p)
        actual, _ = doblar_punto(actual, a, p)
        n //= 2

    return resultado


def obtener_todos_puntos(a, b, p):
    puntos = []
    for x in range(p):
        rhs = (x ** 3 + a * x + b) % p
        ys = sqrt_mod(rhs, p)
        for y in ys:
            puntos.append((x, y))
    puntos.append(None)
    return puntos


def punto_to_str(punto):
    if punto is None:
        return "∞"
    return f"({punto[0]}, {punto[1]})"


# --------- PROTOCOLO ECDH N PERSONAS ---------
# Para n personas, el secreto compartido requiere n-1 rondas de intercambio.
# Ejemplo con 3 personas (Alice=0, Bob=1, Carol=2):
#
# Ronda 0 (claves públicas individuales):
#   A_pub = k_A * G
#   B_pub = k_B * G
#   C_pub = k_C * G
#
# Ronda 1 (productos dobles):
#   AB = k_A * (k_B * G) = k_A * k_B * G
#   BC = k_B * (k_C * G) = k_B * k_C * G
#   CA = k_C * (k_A * G) = k_C * k_A * G
#
# Secreto final (todos deben llegar al mismo punto):
#   Alice:  k_A * BC = k_A * k_B * k_C * G
#   Bob:    k_B * CA = k_A * k_B * k_C * G
#   Carol:  k_C * AB = k_A * k_B * k_C * G

def ecdh_n_personas(claves, G, a, p):
    """
    Ejecuta el protocolo ECDH para n personas.
    claves: lista de enteros [k0, k1, ..., k_{n-1}]
    G: punto generador
    Devuelve: lista de rondas, cada ronda es una lista de puntos (uno por persona)
              y el secreto final (debe ser el mismo para todos).
    """
    n = len(claves)
    rondas = []

    # Ronda 0: cada persona calcula k_i * G
    puntos_actuales = []
    for i in range(n):
        pt = multiplicacion_escalar(G, claves[i], a, p)
        puntos_actuales.append(pt)
    rondas.append(list(puntos_actuales))

    # Rondas 1 .. n-2: cada persona toma el punto de la persona anterior (en ciclo)
    # y lo multiplica por su propia clave
    for ronda in range(1, n - 1):
        nuevos_puntos = []
        for i in range(n):
            # Persona i toma el punto de la persona anterior en el ciclo
            # El índice del punto a tomar: (i - ronda) % n de la ronda anterior
            idx_anterior = (i - 1) % n
            pt_recibido = puntos_actuales[idx_anterior]
            nuevo = multiplicacion_escalar(pt_recibido, claves[i], a, p)
            nuevos_puntos.append(nuevo)
        puntos_actuales = nuevos_puntos
        rondas.append(list(puntos_actuales))

    # Ronda final: cada persona calcula el secreto compartido
    secretos = []
    for i in range(n):
        idx_anterior = (i - 1) % n
        pt_recibido = puntos_actuales[idx_anterior]
        secreto = multiplicacion_escalar(pt_recibido, claves[i], a, p)
        secretos.append(secreto)

    return rondas, secretos


# --------- APP ---------
def main(page: ft.Page):
    page.title = "ECDH — Diffie-Hellman con Curvas Elípticas"
    page.scroll = "auto"
    page.padding = 20

    # ===== ESTADO =====
    state = {
        "curve_valid": False,
        "a": 0, "b": 0, "p": 0,
        "puntos": [],
        "n_personas": 3,
    }

    # ===== CURVA =====
    curve_title = ft.Text("1. Parámetros de la Curva: y² = x³ + ax + b (mod p)", size=20, weight="bold")
    a_input = ft.TextField(label="a", width=80, value="2")
    b_input = ft.TextField(label="b", width=80, value="2")
    p_input = ft.TextField(label="p (primo)", width=120, value="17")
    validate_btn = ft.ElevatedButton("Validar Curva", icon=ft.Icons.CHECK_CIRCLE)
    curve_output = ft.Column()

    # ===== PUNTO GENERADOR =====
    gen_title = ft.Text("2. Punto Generador G", size=18, weight="bold")
    gx_input = ft.TextField(label="Gx", width=100, value="5")
    gy_input = ft.TextField(label="Gy", width=100, value="1")
    gen_output = ft.Column()

    # ===== NÚMERO DE PERSONAS =====
    personas_title = ft.Text("3. Personas", size=18, weight="bold")
    n_personas_input = ft.TextField(label="Número de personas (n ≥ 2)", width=200, value="3")

    # ===== CLAVES PRIVADAS =====
    claves_title = ft.Text("4. Claves Privadas", size=18, weight="bold")
    claves_container = ft.Column()
    claves_inputs = []  # se llenan dinámicamente

    # ===== BOTÓN EJECUTAR =====
    run_btn = ft.ElevatedButton(
        "Ejecutar Protocolo ECDH",
        icon=ft.Icons.LOCK,
        style=ft.ButtonStyle(bgcolor=ft.Colors.INDIGO_700, color=ft.Colors.WHITE),
        height=50,
    )
    resultado_output = ft.Column()

    # ===== NOMBRES PREDETERMINADOS =====
    NOMBRES = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi"]

    def color_persona(i):
        colores = [
            ft.Colors.BLUE_700,
            ft.Colors.GREEN_700,
            ft.Colors.RED_700,
            ft.Colors.ORANGE_700,
            ft.Colors.PURPLE_700,
            ft.Colors.TEAL_700,
            ft.Colors.PINK_700,
            ft.Colors.BROWN_700,
        ]
        return colores[i % len(colores)]

    def nombre(i):
        return NOMBRES[i] if i < len(NOMBRES) else f"Persona {i + 1}"

    def actualizar_claves(e=None):
        claves_inputs.clear()
        claves_container.controls.clear()
        try:
            n = int(n_personas_input.value)
            if n < 2:
                n = 2
        except ValueError:
            n = 3

        state["n_personas"] = n

        for i in range(n):
            tf = ft.TextField(
                label=f"Clave privada de {nombre(i)} (k{i})",
                width=280,
                value=str(i + 2),
            )
            claves_inputs.append(tf)
            claves_container.controls.append(
                ft.Row([
                    ft.Container(
                        content=ft.Text(nombre(i), weight="bold", color=ft.Colors.WHITE),
                        bgcolor=color_persona(i),
                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                        border_radius=6,
                        width=80,
                    ),
                    tf,
                ])
            )
        page.update()

    n_personas_input.on_change = actualizar_claves

    def validar_curva_action(e):
        curve_output.controls.clear()
        gen_output.controls.clear()
        resultado_output.controls.clear()
        state["curve_valid"] = False

        try:
            a = int(a_input.value)
            b = int(b_input.value)
            p = int(p_input.value)
        except ValueError:
            curve_output.controls.append(ft.Text("Error: a, b, p deben ser enteros.", color=ft.Colors.RED))
            page.update()
            return

        valida, delta = validar_curva(a, b, p)
        curve_output.controls.append(ft.Text(f"Δ = 4·{a}³ + 27·{b}² = {delta} mod {p}"))

        if not valida:
            curve_output.controls.append(ft.Text("Curva NO válida (discriminante = 0).", color=ft.Colors.RED))
            page.update()
            return

        state["a"] = a
        state["b"] = b
        state["p"] = p
        state["curve_valid"] = True
        puntos = obtener_todos_puntos(a, b, p)
        state["puntos"] = puntos

        puntos_afines = [pt for pt in puntos if pt is not None]
        lista_str = ", ".join([punto_to_str(pt) for pt in puntos])

        curve_output.controls.append(ft.Text("✓ Curva válida", color=ft.Colors.GREEN, weight="bold"))
        curve_output.controls.append(ft.Text(f"Orden |E| = {len(puntos)}  (incluyendo ∞)", color=ft.Colors.BLUE_700))
        curve_output.controls.append(ft.Text(f"Puntos: {lista_str}", size=10, color=ft.Colors.GREY_700))

        # Validar punto generador
        try:
            gx = int(gx_input.value)
            gy = int(gy_input.value)
            G = (gx, gy)
            if G in puntos_afines:
                gen_output.controls.append(ft.Text(f"✓ G = {punto_to_str(G)} pertenece a la curva.", color=ft.Colors.GREEN, weight="bold"))
            else:
                gen_output.controls.append(ft.Text(f"⚠ G = {punto_to_str(G)} NO pertenece a la curva.", color=ft.Colors.ORANGE))
        except ValueError:
            gen_output.controls.append(ft.Text("Ingresa coordenadas enteras para G.", color=ft.Colors.RED))

        page.update()

    def ejecutar_ecdh(e):
        resultado_output.controls.clear()

        if not state["curve_valid"]:
            resultado_output.controls.append(ft.Text("Primero valida la curva.", color=ft.Colors.RED))
            page.update()
            return

        a = state["a"]
        b = state["b"]
        p = state["p"]

        try:
            gx = int(gx_input.value)
            gy = int(gy_input.value)
        except ValueError:
            resultado_output.controls.append(ft.Text("Coordenadas de G inválidas.", color=ft.Colors.RED))
            page.update()
            return

        G = (gx, gy)
        puntos_afines = [pt for pt in state["puntos"] if pt is not None]
        if G not in puntos_afines:
            resultado_output.controls.append(ft.Text("G no pertenece a la curva.", color=ft.Colors.RED))
            page.update()
            return

        try:
            claves = [int(tf.value) for tf in claves_inputs]
        except ValueError:
            resultado_output.controls.append(ft.Text("Claves privadas deben ser enteros.", color=ft.Colors.RED))
            page.update()
            return

        n = len(claves)
        if any(k <= 0 for k in claves):
            resultado_output.controls.append(ft.Text("Las claves deben ser enteros positivos.", color=ft.Colors.RED))
            page.update()
            return

        # --- Ejecutar protocolo ---
        try:
            rondas, secretos = ecdh_n_personas(claves, G, a, p)
        except Exception as ex:
            resultado_output.controls.append(ft.Text(f"Error en cálculo: {ex}", color=ft.Colors.RED))
            page.update()
            return

        resultado_output.controls.append(
            ft.Text("Protocolo ECDH — Paso a Paso", size=22, weight="bold", color=ft.Colors.INDIGO_700)
        )
        resultado_output.controls.append(ft.Divider())

        # Parámetros públicos
        resultado_output.controls.append(ft.Text("Parámetros públicos:", weight="bold"))
        resultado_output.controls.append(
            ft.Text(f"  Curva: y² = x³ + {a}x + {b}  (mod {p})", font_family="monospace")
        )
        resultado_output.controls.append(
            ft.Text(f"  Punto generador G = {punto_to_str(G)}", font_family="monospace")
        )
        resultado_output.controls.append(ft.Divider())

        # Claves privadas (secretas)
        resultado_output.controls.append(ft.Text("Claves privadas (secretas):", weight="bold"))
        for i, k in enumerate(claves):
            resultado_output.controls.append(
                ft.Text(f"  k_{nombre(i)} = {k}", font_family="monospace", color=color_persona(i))
            )
        resultado_output.controls.append(ft.Divider())

        # Rondas
        for r_idx, ronda in enumerate(rondas):
            if r_idx == 0:
                titulo_ronda = "Ronda 1 — Claves públicas individuales (cada persona calcula kᵢ · G)"
                descripcion = lambda i: f"  {nombre(i)} calcula k_{nombre(i)} · G = {claves[i]} · {punto_to_str(G)} = {punto_to_str(ronda[i])}"
            else:
                titulo_ronda = f"Ronda {r_idx + 1} — Intercambio (cada persona multiplica por el punto recibido)"
                ronda_anterior = rondas[r_idx - 1]
                descripcion = lambda i: (
                    f"  {nombre(i)} recibe {punto_to_str(ronda_anterior[(i - 1) % n])} de {nombre((i - 1) % n)}"
                    f" → multiplica por k_{nombre(i)} = {claves[i]}"
                    f" → obtiene {punto_to_str(ronda[i])}"
                )

            resultado_output.controls.append(
                ft.Text(titulo_ronda, size=15, weight="bold", color=ft.Colors.INDIGO_400)
            )
            for i in range(n):
                resultado_output.controls.append(
                    ft.Text(descripcion(i), font_family="monospace", color=color_persona(i))
                )
            resultado_output.controls.append(ft.Divider())

        # Ronda final: secreto compartido
        resultado_output.controls.append(
            ft.Text("Ronda Final — Cálculo del Secreto Compartido", size=15, weight="bold", color=ft.Colors.INDIGO_400)
        )

        ultima_ronda = rondas[-1]
        for i in range(n):
            idx_anterior = (i - 1) % n
            pt_recibido = ultima_ronda[idx_anterior]
            resultado_output.controls.append(
                ft.Text(
                    f"  {nombre(i)} recibe {punto_to_str(pt_recibido)} de {nombre(idx_anterior)}"
                    f" → multiplica por k_{nombre(i)} = {claves[i]}"
                    f" → Secreto = {punto_to_str(secretos[i])}",
                    font_family="monospace",
                    color=color_persona(i),
                )
            )

        resultado_output.controls.append(ft.Divider())

        # Verificación
        todos_iguales = all(s == secretos[0] for s in secretos)
        secreto_comun = secretos[0]

        if todos_iguales:
            resultado_output.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("✓ ¡SECRETO COMPARTIDO ESTABLECIDO!", size=18, weight="bold", color=ft.Colors.WHITE),
                        ft.Text(f"  S = k_A · k_B · k_C · G = {punto_to_str(secreto_comun)}", font_family="monospace", color=ft.Colors.WHITE, size=16),
                        ft.Text(f"  Todos los participantes obtuvieron el mismo punto.", color=ft.Colors.WHITE),
                    ]),
                    bgcolor=ft.Colors.GREEN_700,
                    padding=16,
                    border_radius=10,
                )
            )
        else:
            resultado_output.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("✗ ERROR: Los secretos no coinciden.", size=16, weight="bold", color=ft.Colors.WHITE),
                        *[ft.Text(f"  {nombre(i)}: {punto_to_str(secretos[i])}", font_family="monospace", color=ft.Colors.WHITE) for i in range(n)],
                    ]),
                    bgcolor=ft.Colors.RED_700,
                    padding=16,
                    border_radius=10,
                )
            )

        # Resumen de rondas necesarias
        resultado_output.controls.append(ft.Divider())
        resultado_output.controls.append(
            ft.Text(
                f"Rondas de comunicación necesarias: {n - 1}  (para {n} personas se requieren n−1 = {n-1} rondas)",
                color=ft.Colors.BLUE_GREY_600,
                italic=True,
            )
        )

        page.update()

    validate_btn.on_click = validar_curva_action
    run_btn.on_click = ejecutar_ecdh

    # Inicializar campos de claves
    actualizar_claves()

    page.add(
        ft.Column([
            ft.Text("Diffie-Hellman con Curvas Elípticas (ECDH) — N Personas", size=26, weight="bold", color=ft.Colors.INDIGO_700),
            ft.Divider(),
            # Sección 1: Curva
            curve_title,
            ft.Row([a_input, b_input, p_input, validate_btn]),
            curve_output,
            ft.Divider(),
            # Sección 2: Punto generador
            gen_title,
            ft.Row([gx_input, gy_input]),
            gen_output,
            ft.Divider(),
            # Sección 3: Personas
            personas_title,
            n_personas_input,
            ft.Divider(),
            # Sección 4: Claves
            claves_title,
            claves_container,
            ft.Divider(),
            # Ejecutar
            run_btn,
            ft.Divider(),
            resultado_output,
        ])
    )


ft.app(target=main)

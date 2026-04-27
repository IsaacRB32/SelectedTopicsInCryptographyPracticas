import os
from ecdsa import SigningKey, NIST256p
from ecdsa.ellipticcurve import Point

def guardar_punto_txt(nombre_archivo, punto):
    ## Guardamos X en la primera línea y Y en la segunda
    with open(nombre_archivo, 'w') as f:
        f.write(f"{punto.x()}\n")
        f.write(f"{punto.y()}\n")
    print(f"\n¡ Se generó el archivo '{nombre_archivo}' !")
    print("-> Envía este archivo a tu SIGUIENTE compañero.")

def leer_punto_txt():
    print("\n[Paso de Lectura]")
    while True:
        # Actualizamos el texto de ayuda para que refleje el nuevo formato
        archivo = input("Ingresa el nombre del archivo .txt que recibiste (ej. alicia_ronda1.txt): ").strip()
        try:
            with open(archivo, 'r') as f:
                lineas = f.readlines()
                x = int(lineas[0].strip())
                y = int(lineas[1].strip())
            # Reconstruimos el punto geométrico en la curva
            print("Archivo leído correctamente")
            return Point(NIST256p.curve, x, y)
        except FileNotFoundError:
            print(f"Error: No se encontró '{archivo}'")
        except Exception as e:
            print(f"Error al procesar el archivo")

def main():
    print("*"*50)
    print(" Protocolo Diffie-Hellman con Curvas Elípticas para 3 ENTIDADES - NIST P-256")
    print("*"*50)

    ## Pedimos el nombre del usuario para nombrar sus archivos
    mi_nombre = input("\nIngresa tu nombre: ").strip().replace(" ", "_")

    ## 1. GENERACIÓN DE CLAVE PRIVADA LOCAL
    ## Usamos os.urandom para una semilla criptográficamente segura
    sk = SigningKey.generate(curve=NIST256p)
    clave_privada_escalar = sk.privkey.secret_multiplier
    print("\nTu clave privada secreta ha sido generada. ¡No la compartas con nadie!")

    ## 2. RONDA 1: Intercambio Inicial
    ## Multiplicamos nuestra clave privada por el Punto Generador (G)
    G = NIST256p.generator
    mi_punto_ronda1 = clave_privada_escalar * G

    print("\n" + "*"*50)
    print(" RONDA 1")
    print("*"*50)
    ## Generamos el archivo con el nombre personalizado
    archivo_ronda1 = f"{mi_nombre}_ronda1.txt"
    guardar_punto_txt(archivo_ronda1, mi_punto_ronda1)

    ## Esperamos a recibir el archivo del compañero anterior
    punto_recibido_r1 = leer_punto_txt()

    ## 3. RONDA 2: Intercambio Intermedio
    ## Multiplicamos nuestra clave privada por el punto que acabamos de recibir
    mi_punto_ronda2 = clave_privada_escalar * punto_recibido_r1

    print("\n" + "*"*50)
    print(" RONDA 2")
    print("*"*50)
    ## Generamos el segundo archivo con el nombre personalizado
    archivo_ronda2 = f"{mi_nombre}_ronda2.txt"
    guardar_punto_txt(archivo_ronda2, mi_punto_ronda2)

    ## Esperamos a recibir el segundo archivo del compañero anterior
    punto_recibido_r2 = leer_punto_txt()

    ## 4. CÁLCULO DEL SECRETO COMPARTIDO FINAL
    ## Multiplicamos nuestra clave privada por el último punto recibido
    secreto_final_punto = clave_privada_escalar * punto_recibido_r2

    print("\n" + "*"*50)
    print(" ¡CÁLCULO COMPLETADO!")
    print("*"*50)
    print(f"EL SECRETO COMPARTIDO ES:")
    print(f"\n{secreto_final_punto.x()}")
    print(f"\n{secreto_final_punto.y()}")
    print("\n¡Los tres deberían tener exactamente la misma coordenada!")

if __name__ == "__main__":
    main()
    
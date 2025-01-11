import subprocess
import json

API_URL = "http://10.1.3.1:5000/modificar_tc"

def enviar_solicitud(command, args, interface):
    payload = {
        "command": command,
        "args": args,
        "interface": interface
    }
    curl_command = [
        "curl",
        "-s",
        "-X", "POST",
        API_URL,
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    resultado = subprocess.run(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Respuesta de la API:")
    print(resultado.stdout)
    if resultado.stderr:
        print("Errores:")
        print(resultado.stderr)

def menu():
    while True:
        print("\n=== Menu para enviar comandos curl a la API ===")
        print("1) Agregar delay")
        print("2) Agregar perdida de paquetes")
        print("3) Limitar ancho de banda")
        print("4) Limpiar configuracion")
        print("5) Mostrar configuracion actual")
        print("6) Salir")

        opcion = input("Seleccione una opcion (1-6): ").strip()

        if opcion == "6":
            print("Saliendo...")
            break

        interface = input("Ingrese la interfaz (eth1 o eth2): ").strip()
        if opcion == "1":
            delay_valor = input("Ingrese el valor de delay: ").strip()
            enviar_solicitud("delay", delay_valor, interface)
        elif opcion == "2":
            loss_valor = input("Ingrese el porcentaje de perdida de paquetes: ").strip()
            enviar_solicitud("loss", loss_valor, interface)
        elif opcion == "3":
            rate = input("Ingrese la velocidad maxima: ").strip()
            enviar_solicitud("bandwidth", rate, interface)
        elif opcion == "4":
            enviar_solicitud("clean", "", interface)
        elif opcion == "5":
            enviar_solicitud("show", "", interface)
        else:
            print("Opcion no valida, intente nuevamente.")

if __name__ == "__main__":
    menu()


import argparse
import sys
import subprocess
import os
import json

CONFIG_FILE = '/home/vnx/interface_config.json'

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            "eth1": {"delay": None, "loss": None, "rate": None},
            "eth2": {"delay": None, "loss": None, "rate": None},
        }

def guardar_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

interface_config = cargar_config()

def delay_activo(interface, delay_valor):
    if interface not in interface_config:
        print("Error: Interfaz no valida.")
        return
    interface_config[interface]["delay"] = delay_valor
    reapply_tc(interface)

def perdida_de_paquetes_activo(interface, loss_valor):
    if interface not in interface_config:
        print("Error: Interfaz no valida.")
        return
    interface_config[interface]["loss"] = loss_valor
    reapply_tc(interface)

def ancho_de_banda_activo(interface, rate):
    if interface not in interface_config:
        print("Error: Interfaz no valida.")
        return
    interface_config[interface]["rate"] = rate
    reapply_tc(interface)

def limpiar_tc(interface):
    if interface not in interface_config:
        print("Error: Interfaz no valida.")
        return
    cmd = ["sudo", "tc", "qdisc", "del", "dev", interface, "root"]
    subprocess.run(cmd, stderr=subprocess.DEVNULL)
    print("Se ha eliminado la configuracion actual de tc en {}.".format(interface))
    interface_config[interface] = {"delay": None, "loss": None, "rate": None}
    guardar_config(interface_config)

def mostrar_configuracion(interface):
    if interface not in interface_config:
        print("Error: Interfaz no valida.")
        return
    try:
        resultado = subprocess.Popen(
            ["sudo", "tc", "qdisc", "show", "dev", interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = resultado.communicate()
        if resultado.returncode == 0:
            print("Configuracion actual de {}:\n{}".format(interface, stdout.decode()))
        else:
            print("No se pudo obtener la configuracion de tc en {}. Error:\n{}".format(interface, stderr.decode()))
    except Exception as e:
        print("Ocurrio un error al intentar mostrar la configuracion: {}".format(e))

def reapply_tc(interface):
    if interface not in interface_config:
        print("Error: Interfaz no valida.")
        return
    config = interface_config[interface]
    subprocess.run(["sudo", "tc", "qdisc", "del", "dev", interface, "root"], stderr=subprocess.DEVNULL)
    cmd = ["sudo", "tc", "qdisc", "add", "dev", interface, "root", "handle", "1:", "netem"]
    if config["delay"]:
        cmd.extend(["delay", config["delay"]])
    if config["loss"]:
        cmd.extend(["loss", config["loss"]])
    if config["rate"]:
        cmd.extend(["rate", config["rate"]])
    if len(cmd) > 6:
        subprocess.run(cmd, check=True)
    print("Configuraciones aplicadas en {}.".format(interface))
    guardar_config(interface_config)
    mostrar_configuracion(interface)

def menu_interactivo():
    while True:
        print("\n=== Menu principal ===")
        print("1) Agregar delay")
        print("2) Agregar perdida de paquetes")
        print("3) Limitar ancho de banda")
        print("4) Mostrar configuracion actual")
        print("5) Borrar la configuracion")
        print("6) Salir")
        choice = input("Elija una opcion (1-6): ").strip()
        if choice == "6":
            print("Saliendo...")
            break
        elif choice == "1":
            delay_valor = input("Introduzca el valor de delay: ").strip()
            interface = input("Indique la interfaz donde desea realizar la configuracion (eth1/eth2): ").strip()
            print("Aplicando delay {} en {}".format(delay_valor, interface))
            delay_activo(interface, delay_valor)
        elif choice == "2":
            loss_valor = input("Introduzca el porcentaje de perdida de paquetes: ").strip()
            interface = input("Indique la interfaz donde desea realizar la configuracion (eth1/eth2): ").strip()
            print("Aplicando perdida de paquetes {} en {}".format(loss_valor, interface))
            perdida_de_paquetes_activo(interface, loss_valor)
        elif choice == "3":
            rate = input("Introduzca la velocidad maxima: ").strip()
            interface = input("Indique la interfaz donde desea realizar la configuracion (eth1/eth2): ").strip()
            print("Limitar ancho de banda: {} en {}".format(rate, interface))
            ancho_de_banda_activo(interface, rate)
        elif choice == "4":
            interface = input("Indique la interfaz donde desea mostrar la configuracion actual (eth1/eth2): ").strip()
            mostrar_configuracion(interface)
        elif choice == "5":
            interface = input("Indique la interfaz donde desea borrar la configuracion (eth1/eth2): ").strip()
            limpiar_tc(interface)
        else:
            print("Opcion no valida. Intentelo de nuevo.")

def main():
    parser = argparse.ArgumentParser(description="Script para modificar configuraciones de tc")
    parser.add_argument("--command", required=True, help="Comando a ejecutar (delay, loss, bandwidth, etc.)")
    parser.add_argument("--args", required=True, help="Argumentos del comando")
    parser.add_argument("--interface", required=True, help="Interfaz donde se aplicara la configuracion (eth1 o eth2)")
    args = parser.parse_args()
    command = args.command
    argumentos = args.args
    interface = args.interface
    print("Ejecutando comando: {} {} en {}".format(command, argumentos, interface))
    if command == "delay":
        delay_activo(interface, argumentos)
    elif command == "loss":
        perdida_de_paquetes_activo(interface, argumentos)
    elif command == "bandwidth":
        params = argumentos.split()
        if len(params) >= 1:
            rate = params[0]
            ancho_de_banda_activo(interface, rate)
        else:
            print("Argumentos insuficientes para bandwidth")
    elif command == "clean":
        limpiar_tc(interface)
    elif command == "show":
        mostrar_configuracion(interface)
    else:
        print("Comando no reconocido")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        menu_interactivo()


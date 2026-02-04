import os
import subprocess
import readchar
from shutil import rmtree
from time import sleep
from constants import States, Path, actual_os, windows
from visuals import (
    get_format_line,
    get_option_format,
    print_success,
    print_error,
    clear_screen,
    draw_picker,
    title,
)

current_state = States.dir_picker
current_path = ""
cursor_index = 0
contents = []


def list_dir(path: str) -> list:
    """devuelve una lista con todos los contenidos de una carpeta"""
    result = os.listdir(path)
    result.append("..")
    return sorted(result)


def run_command(command: str) -> subprocess.CompletedProcess:
    """Ejecuta un comando dependiendo del sistema operativo"""
    if actual_os == windows:
        return subprocess.run(
            ["powershell", "-Command", command], capture_output=True, text=True
        )
    else:
        return subprocess.run(command.split(), capture_output=True, text=True)


def config_policy() -> None:
    """Configura la política de ejecucion para windows"""
    result = run_command("Set-ExecutionPolicy unrestricted")
    if result.returncode != 0:
        print(result.stderr)


def install_libs(libs: list[str]):
    for lib in libs:
        command = f"{Path.python} -m pip install {lib}"
        result = run_command(command)
        if result.returncode == 0:
            print_success(f"✅ Librería '{lib}' instalada.")
            sleep(1)
        else:
            print_error(f"❌ Error: {result.stderr}")
            input("Presioná Enter para continuar...")


def dir_picker():
    global current_path, cursor_index, current_state, contents
    clear_screen()

    draw_picker(contents, cursor_index, current_path)
    state_changes = {
        "l": States.library_installer,
        " ": States.venv_creator,
        "m": States.create_dir,
    }
    key = readchar.readkey()
    if key in state_changes:
        current_state = state_changes[key]
        return
    match key:
        case readchar.key.UP:
            cursor_index = max(cursor_index - 1, 0)

        case readchar.key.DOWN:
            cursor_index = min(cursor_index + 1, len(contents) - 1)

        case readchar.key.ENTER | readchar.key.RIGHT:
            if contents[cursor_index] != "..":
                current_state = States.choise_action
                return
            current_path = os.path.dirname(current_path.rstrip("/")) + "/"
            os.chdir(current_path)
            cursor_index = 0
            contents = os.listdir(current_path)

        case readchar.key.BACKSPACE | readchar.key.LEFT:
            current_path = os.path.dirname(current_path.rstrip("/")) + "/"
            os.chdir(current_path)
            cursor_index = 0
            contents = os.listdir(current_path)

        case "q" | readchar.key.ESC:
            exit(0)


def venv_creator():
    global current_state
    title("⚙️ Creando entorno virtual...")
    run_command("python -m venv .venv")
    print_success("✅ Entorno creado.")
    sleep(1)
    current_state = States.dir_picker


def lib_install():
    global current_state
    title("📦 Instalación de librerías")
    if not os.path.exists(".venv"):
        print_error("⚠️ No existe .venv. Creando...")
        sleep(1)
        current_state = States.venv_creator
        return

    if os.path.exists("requirements.txt"):
        title("📦 Instalando librerías desde requirements.txt")
        op = (
            input("Instalar las librerías desde requirements.txt? (si/no): ")
            .strip()
            .lower()
        )
        if "si" in op:
            command = f"{Path.python} -m pip install -r requirements.txt"
            result = run_command(command)
            if result.returncode == 0:
                print_success("✅ Librerías instaladas correctamente.")
            else:
                print_error(f"❌ Error: {result.stderr}")
                input("Presioná Enter para continuar...")
    else:
        print_error("❌ No se encontró requirements.txt.")
        print("(Podés instalar varias librerias separando sus nombres por una coma)")
        op = (
            input("¿Querés instalar una o varias librerias?  (si/no): ").strip().lower()
        )
        if "si" in op:
            lib = input("Nombre de la librería/s: ").strip()
            libraries = [lib] if "," not in lib else lib.split(",")
            install_libs(libraries)
        current_state = States.dir_picker


def create_dir():
    global current_state
    clear_screen()
    title("📦 Creación de carpetas")
    try:
        name = input("Nombre de la carpeta: ").strip()
        os.mkdir(name)
        print_success(f"✅ Carpeta '{name}' creada.")
    except Exception as e:
        print_error(f"Error en input(): {e}")
        input("Presioná Enter para continuar...")
    finally:
        current_state = States.dir_picker


def choise_action():
    global cursor_index, current_path, current_state, contents

    # Estado para elegir que hacer en una carpeta
    actual_element = contents[cursor_index]
    full_path = os.path.join(current_path, actual_element)
    line = get_format_line(full_path, "", actual_element)
    option_index = 0
    options = [
        "Abrir",
        "Crear entorno",
        "Instalar libreria en entorno",
        "Cambiar nombre",
        "Listar librerias instaladas",
        "Borrar",
        "Salir",
    ]

    if not (os.path.isdir(full_path)):
        current_state = States.dir_picker
        return

    # Estados para elegir que hacer en una carpeta
    states_to_switch = [
        States.dir_picker,
        States.venv_creator,
        States.library_installer,
        States.dir_picker,
        States.dir_picker,
        States.dir_picker,
    ]
    # Bucle del sub_menu
    while True:
        clear_screen()
        print(line)
        for index, option in enumerate(options):
            print(get_option_format(option, (index == option_index)))

        key = readchar.readkey()
        match key:
            case readchar.key.UP:
                option_index = max(option_index - 1, 0)
            case readchar.key.DOWN:
                option_index = min(option_index + 1, len(options) - 1)
            case readchar.key.ENTER:
                if option_index == 0 or option_index <= 2:
                    current_path += f"/{actual_element}"
                    os.chdir(current_path)
                    contents = os.listdir(current_path)
                if option_index == 3:
                    new_name = input("Nuevo nombre : ").strip()
                    os.rename(full_path, new_name)
                if option_index == 4:
                    title("📦 Listando librerias...")
                    command = f"{actual_element}/{Path.python} -m pip freeze"
                    result = run_command(command)
                    if result.returncode == 0:
                        print(result.stdout)
                    else:
                        print_error(f"❌ Error: {result.stderr}")
                    input("Presioná Enter para continuar...")
                if option_index == 5:
                    rmtree(full_path)

                cursor_index = 0
                current_state = states_to_switch[option_index]
                break


def main():
    global current_path, cursor_index, current_state, contents
    user: str = os.path.expanduser("~")
    current_path = user
    contents = os.listdir(current_path)
    os.chdir(current_path)

    if actual_os == windows:
        config_policy()

    is_running = True
    print(
        "📁 Navegá con ↑ ↓ - Enter para entrar, L para instalar libs, Space para crear venv"
    )
    input("Presioná Enter para empezar...")

    actions = {
        States.dir_picker: dir_picker,
        States.venv_creator: venv_creator,
        States.library_installer: lib_install,
        States.create_dir: create_dir,
        States.choise_action: choise_action,
    }

    while is_running:
        actions[current_state]()


if __name__ == "__main__":
    main()

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


def main():
    user: str = os.path.expanduser("~")
    current_path = user
    os.chdir(current_path)
    contents: list = list_dir(current_path)
    cursor_index: int = 0
    state: int = States.dir_picker

    if actual_os == windows:
        config_policy()

    is_running = True
    print(
        "📁 Navegá con ↑ ↓ - Enter para entrar, L para instalar libs, Space para crear venv"
    )
    input("Presioná Enter para empezar...")
    while is_running:
        if state == States.dir_picker:
            clear_screen()
            contents = list_dir(current_path)

            draw_picker(contents, cursor_index, current_path)
            state_changes = {
                "l": States.library_installer,
                " ": States.venv_creator,
                "m": States.create_dir,
            }
            key = readchar.readkey()
            if key in state_changes:
                state = state_changes[key]
                continue
            match key:
                case readchar.key.UP:
                    cursor_index = max(cursor_index - 1, 0)

                case readchar.key.DOWN:
                    cursor_index = min(cursor_index + 1, len(contents) - 1)

                case readchar.key.ENTER | readchar.key.RIGHT:
                    if contents[cursor_index] != "..":
                        state = States.choise_action
                        continue
                    current_path = os.path.dirname(current_path.rstrip("/")) + "/"
                    os.chdir(current_path)
                    cursor_index = 0

                case readchar.key.BACKSPACE | readchar.key.LEFT:
                    current_path = os.path.dirname(current_path.rstrip("/")) + "/"
                    os.chdir(current_path)
                    cursor_index = 0

                case "q" | readchar.key.ESC:
                    is_running = False
                    exit(0)

        elif state == States.venv_creator:
            title("⚙️ Creando entorno virtual...")
            run_command("python -m venv .venv")
            print_success("✅ Entorno creado.")
            sleep(1)
            state = States.dir_picker

        elif state == States.library_installer:
            title("📦 Instalación de librerías")
            if not os.path.exists(".venv"):
                print_error("⚠️ No existe .venv. Creando...")
                sleep(1)
                state = States.venv_creator
                continue

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
                print(
                    "(Podés instalar varias librerias separando sus nombres por una coma)"
                )
                op = (
                    input("¿Querés instalar una o varias librerias?  (si/no): ")
                    .strip()
                    .lower()
                )
                if "si" in op:
                    lib = input("Nombre de la librería/s: ").strip()
                    libraries = [lib] if "," not in lib else lib.split(",")
                    install_libs(libraries)
                state = States.dir_picker

        elif state == States.create_dir:
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
                state = States.dir_picker

        elif state == States.choise_action:
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
                state = States.dir_picker
                continue

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
                        state = states_to_switch[option_index]
                        break


if __name__ == "__main__":
    main()

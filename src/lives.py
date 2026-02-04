from rich.live import Live
import os
from renders import (
    render_picker,
    render_choise,
    title,
    print_success,
    print_error,
    console,
)
from shutil import rmtree
import readchar
from constants import States
import globals
from functions import create_venv, run_command, install_libs, Path
from time import sleep


def draw_picker():
    console.clear()
    with Live(
        render_picker(globals.contents, globals.cursor_index, globals.current_path),
        refresh_per_second=30,
    ) as live:
        while globals.current_state == States.dir_picker:
            state_changes = {
                "l": States.library_installer,
                " ": States.venv_creator,
                "m": States.create_dir,
            }
            key = readchar.readkey()
            if key in state_changes:
                globals.current_state = state_changes[key]
                return
            match key:
                case readchar.key.UP:
                    globals.cursor_index = max(globals.cursor_index - 1, 0)

                case readchar.key.DOWN:
                    globals.cursor_index = min(
                        globals.cursor_index + 1, len(globals.contents) - 1
                    )

                case readchar.key.ENTER | readchar.key.RIGHT:
                    if globals.contents[globals.cursor_index] != "..":
                        globals.current_state = States.choise_action
                        return
                    globals.current_path = (
                        os.path.dirname(globals.current_path.rstrip("/")) + "/"
                    )
                    os.chdir(globals.current_path)
                    globals.cursor_index = 0
                    globals.contents = os.listdir(globals.current_path)

                case readchar.key.BACKSPACE | readchar.key.LEFT:
                    globals.current_path = (
                        os.path.dirname(globals.current_path.rstrip("/")) + "/"
                    )
                    os.chdir(globals.current_path)
                    globals.cursor_index = 0
                    globals.contents = os.listdir(globals.current_path)

                case "q" | readchar.key.ESC:
                    exit(0)
            live.update(
                render_picker(
                    globals.contents, globals.cursor_index, globals.current_path
                )
            )


def venv_creator():
    console.clear()
    title("⚙️ Creando entorno virtual...")
    if create_venv() != 0:
        print_error("❌ Error al crear el entorno virtual.")
        console.input("Presioná Enter para continuar...")
        globals.current_state = States.dir_picker
        return
    print_success("✅ Entorno creado.")
    sleep(1)
    globals.current_state = States.dir_picker


def lib_install():
    console.clear()
    title("📦 Instalación de librerías")
    if not os.path.exists(".venv"):
        print_error("⚠️ No existe .venv. Creando...")
        sleep(1)
        globals.current_state = States.venv_creator
        return

    if os.path.exists("requirements.txt"):
        title("📦 Instalando librerías desde requirements.txt")
        op = (
            console.input("Instalar las librerías desde requirements.txt? (si/no): ")
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
        globals.current_state = States.dir_picker


def create_dir():
    console.clear()
    title("📦 Creación de carpetas")
    try:
        name = input("Nombre de la carpeta: ").strip()
        os.mkdir(name)
        print_success(f"✅ Carpeta '{name}' creada.")
    except Exception as e:
        print_error(f"Error en input(): {e}")
        input("Presioná Enter para continuar...")
    finally:
        globals.current_state = States.dir_picker


def choise_action():
    # Estado para elegir que hacer en una carpeta
    actual_element = globals.contents[globals.cursor_index]
    full_path = os.path.join(globals.current_path, actual_element)
    option_index = 0

    if not (os.path.isdir(full_path)):
        globals.current_state = States.dir_picker
        return

    # opciones disponibles
    options = [
        "Abrir",
        "Crear entorno",
        "Instalar libreria en entorno",
        "Cambiar nombre",
        "Listar librerias instaladas",
        "Borrar",
        "Salir",
    ]

    # Estados para elegir que hacer en una carpeta
    states_to_switch = [
        States.dir_picker,
        States.venv_creator,
        States.library_installer,
        States.dir_picker,
        States.dir_picker,
        States.dir_picker,
    ]
    console.clear()
    # Bucle del sub_menu
    with Live(render_choise(option_index, options), refresh_per_second=30) as live:
        while globals.current_state == States.choise_action:
            key = readchar.readkey()
            match key:
                case readchar.key.UP:
                    option_index = max(option_index - 1, 0)
                case readchar.key.DOWN:
                    option_index = min(option_index + 1, len(options) - 1)
                case readchar.key.ENTER:
                    if option_index == 0 or option_index <= 2:
                        globals.current_path += f"/{actual_element}"
                        os.chdir(globals.current_path)
                        globals.contents = os.listdir(globals.current_path)
                    if option_index == 3:
                        new_name = console.input("Nuevo nombre : ").strip()
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

                    globals.cursor_index = 0
                    globals.current_state = states_to_switch[option_index]
                    break
            live.update(render_choise(option_index, options))

import os
import platform
import subprocess
from colorama import Style, init, Fore, Back
import readchar
from time import sleep
from dataclasses import dataclass

init(autoreset=True)
windows = "Windows"
actual_system = platform.system()


@dataclass
class States:
    dir_picker = 0
    venv_creator = 1
    library_installer = 2
    create_dir = 3


def config_path() -> str:
    user = os.path.expanduser("~")
    if actual_system == windows:
        result = f"C://Users//{user}//Desktop"
    else:
        result = "/home/fede/"
        os.chdir(result)
    return result


def list_dir(path: str) -> list:
    result = os.listdir(path)
    result.append("..")
    return sorted(result)


def run_command(command: str) -> subprocess.CompletedProcess:
    if actual_system == windows:
        return subprocess.run(
            ["powershell", "-Command", command], capture_output=True, text=True
        )
    else:
        return subprocess.run(command.split(), capture_output=True, text=True)


def config_policy() -> None:
    result = run_command("Set-ExecutionPolicy unrestricted")
    if result.returncode != 0:
        print(result.stderr)


def clear_screen():
    os.system("cls" if actual_system == windows else "clear")


def get_format_line(full_path: str, cursor_content: str, content: str):
    is_dir = os.path.isdir(full_path)
    color = Fore.RED if is_dir else Fore.GREEN
    prefix = Back.WHITE if content == cursor_content else ""
    icon = "📁" if is_dir else "📄"
    result = f"{prefix}{icon}{color} {content} {Style.RESET_ALL}"
    line = result + " " * (50 - len(result.removeprefix(prefix)))
    return line


def draw_picker(contents: list[str], cursor_index: int, current_path):
    clear_screen()
    cursor_content = contents[cursor_index]
    print(f"Path actual : {current_path}")
    if len(contents) > 26:
        content_first_half = contents[: len(contents) // 2]
        content_second_half = contents[len(contents) // 2 :]
        for content in zip(content_first_half, content_second_half):
            line = ""
            for element in content:
                full_path = os.path.join(current_path, element)
                result = get_format_line(full_path, cursor_content, element)
                line += result
            print(line)
        return
    for element in contents:
        full_path = os.path.join(current_path, element)
        result = get_format_line(full_path, cursor_content, element)
        print(result)


def install_libs(libs: list[str]):
    for lib in libs:
        pip_path = ".venv/scripts/pip" if actual_system == windows else ".venv/bin/pip"
        result = run_command(f"{pip_path} install {lib}")
        if result.returncode == 0:
            print(Fore.GREEN + f"✅ Librería '{lib}' instalada.")
            sleep(1)
        else:
            print(Fore.RED + f"❌ Error: {result.stderr}")
            input("Presioná Enter para continuar...")


def main():
    current_path: str = config_path()
    contents: list = list_dir(current_path)
    cursor_index: int = 0
    state: int = States.dir_picker

    if actual_system == windows:
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
            try:
                key = readchar.readkey()
                if key == readchar.key.UP:
                    cursor_index = max(cursor_index - 1, 0)
                elif key == readchar.key.DOWN:
                    cursor_index = min(cursor_index + 1, len(contents) - 1)
                elif key == readchar.key.ENTER or key == readchar.key.RIGHT:
                    selected = contents[cursor_index]
                    if selected == "..":
                        current_path = os.path.dirname(current_path.rstrip("/")) + "/"
                    elif os.path.isdir(selected):
                        current_path = os.path.join(current_path, selected)
                    os.chdir(current_path)
                    cursor_index = 0
                elif key == readchar.key.BACKSPACE or key == readchar.key.LEFT:
                    current_path = os.path.dirname(current_path.rstrip("/")) + "/"
                    os.chdir(current_path)
                    cursor_index = 0
                elif key.lower() == "l":
                    state = States.library_installer
                elif key == " ":
                    state = States.venv_creator
                elif key.lower() == "m":
                    state = States.create_dir
                elif key.lower() == "q":
                    is_running = False
                    exit(0)
            except Exception:
                draw_picker(contents, cursor_index, current_path)

        elif state == States.venv_creator:
            print("⚙️ Creando entorno virtual...")
            run_command("python -m venv .venv")
            print(Fore.GREEN + "✅ Entorno creado.")
            sleep(1)
            state = States.dir_picker

        elif state == States.library_installer:
            print("📦 Instalación de librerías")
            if not os.path.exists(".venv"):
                print(Fore.RED + "⚠️ No existe .venv. Creando...")
                sleep(1)
                state = States.venv_creator
                continue

            if os.path.exists("requirements.txt"):
                print("📦 Instalando librerías desde requirements.txt")
                op = (
                    input("Instalar las librerías desde requirements.txt? (si/no): ")
                    .strip()
                    .lower()
                )
                if "si" in op:
                    pip_path = (
                        ".venv/scripts/pip"
                        if actual_system == windows
                        else ".venv/bin/pip"
                    )
                    result = run_command(f"{pip_path} install -r requirements.txt")
                    if result.returncode == 0:
                        print(Fore.GREEN + "✅ Librerías instaladas correctamente.")
                    else:
                        print(Fore.RED + f"❌ Error: {result.stderr}")
                        input("Presioná Enter para continuar...")
            else:
                print(Fore.RED + "❌ No se encontró requirements.txt.")
                try:
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
                except Exception as e:
                    print(f"Error en input(): {e}")
                    input("Presioná Enter para continuar...")
                finally:
                    state = States.dir_picker

        elif state == States.create_dir:
            clear_screen()
            print("📦 Estado: Creación de carpetas")
            try:
                name = input("Nombre de la carpeta: ").strip()
                os.mkdir(name)
                print(Fore.GREEN + f"✅ Carpeta '{name}' creada.")
            except Exception as e:
                print(Fore.RED + f"Error en input(): {e}")
                input("Presioná Enter para continuar...")
            finally:
                state = States.dir_picker


if __name__ == "__main__":
    main()

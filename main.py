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
    result.insert(0, "..")
    return sorted(result)


def run_command(command: str) -> subprocess.CompletedProcess:
    if actual_system == windows:
        return subprocess.run(
            ["powershell", "-Command", command], capture_output=True, text=True
        )
    else:
        return subprocess.run(command.split(), capture_output=True, text=True)


def config_policy() -> None:
    if actual_system == windows:
        result = run_command("Set-ExecutionPolicy unrestricted")
        if result.returncode != 0:
            print(result.stderr)


def clear_screen():
    os.system("cls" if actual_system == windows else "clear")


def draw_picker(contents: list[str], cursor_index: int, current_path):
    clear_screen()
    content_first_half = contents[: len(contents) // 2]
    content_second_half = contents[len(contents) // 2 :]
    cursor_content = contents[cursor_index]
    print(f"Path actual : {current_path}")
    for index, content in enumerate(zip(content_first_half, content_second_half)):
        line = ""
        for element in content:
            full_path = os.path.join(current_path, element)
            is_dir = os.path.isdir(full_path)
            color = Fore.RED if is_dir else Fore.GREEN
            prefix = Back.WHITE if element == cursor_content else ""
            icon = "📁" if is_dir else "📄"
            result = f"{prefix}{icon}{color} {element} {Style.RESET_ALL}"
            line += result + " " * (50 - len(result.removeprefix(prefix)))
        print(line)


def main():
    current_path: str = config_path()
    contents: list = list_dir(current_path)
    cursor_index: int = 0
    state: int = States.dir_picker
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
                elif key == readchar.key.ENTER:
                    selected = contents[cursor_index]
                    if selected == "..":
                        current_path = os.path.dirname(current_path.rstrip("/")) + "/"
                    elif os.path.isdir(selected):
                        current_path = os.path.join(current_path, selected)
                        os.chdir(current_path)
                        cursor_index = 0
                elif key.lower() == "l":
                    state = States.library_installer
                elif key == " ":
                    state = States.venv_creator
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
            print("📦 Estado: Instalador de librerías")
            if not os.path.exists(".venv"):
                print(Fore.RED + "⚠️ No existe .venv. Creando...")
                run_command("python -m venv .venv")
                print(Fore.GREEN + "✅ Entorno creado.")
                sleep(1)
                if os.path.exists("requirements.txt"):
                    print("📦 Instalando librerías desde requirements.txt")
                    op = (
                        input(
                            "Instalar las librerías desde requirements.txt? (si/no): "
                        )
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
                    state = States.dir_picker
            elif not os.path.exists("requirements.txt"):
                print(Fore.RED + "❌ No se encontró requirements.txt.")
                try:
                    op = (
                        input("¿Querés instalar una sola librería? (si/no): ")
                        .strip()
                        .lower()
                    )
                    if "si" in op:
                        lib = input("Nombre de la librería: ").strip()
                        pip_path = (
                            ".venv/scripts/pip"
                            if actual_system == windows
                            else ".venv/bin/pip"
                        )
                        result = run_command(f"{pip_path} install {lib}")
                        if result.returncode == 0:
                            print(f"✅ Librería '{lib}' instalada.")
                        else:
                            print(f"❌ Error: {result.stderr}")
                            input("Presioná Enter para continuar...")
                except Exception as e:
                    print(f"Error en input(): {e}")
                    input("Presioná Enter para continuar...")
                    state = States.dir_picker


if __name__ == "__main__":
    main()

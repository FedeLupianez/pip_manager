import os
import subprocess
from constants import actual_os, windows, Path, States
from renders import print_success, print_error
from time import sleep


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


def create_venv():
    return run_command("python -m venv .venv").returncode

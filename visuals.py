from colorama import Fore, Back, Style, init
import os
from constants import actual_os, windows


init(
    autoreset=True
)  # Config de colorama para iniciarlo y que cuando termine se reseteen los colores


def clear_screen():
    """Borra la pantalla con el comando especifico de windows o linux""" ""
    os.system("cls" if actual_os == windows else "clear")


def print_error(message: str):
    print(Fore.RED + message + Style.RESET_ALL)


def print_success(message: str):
    print(Fore.GREEN + message + Style.RESET_ALL)


def get_format_line(full_path: str, cursor_content: str, content: str):
    """Retorna la linea formateada de un element dependiendo de qué sea este"""
    is_dir = os.path.isdir(full_path)
    color = Fore.RED if is_dir else Fore.GREEN
    prefix = Back.WHITE if content == cursor_content else ""
    icon = "📁" if is_dir else "📄"
    result = f"{prefix}{icon}{color} {content} {Style.RESET_ALL}"
    line = result + " " * (50 - len(result.removeprefix(prefix)))
    return line


def draw_picker(contents: list[str], cursor_index: int, current_path):
    """Dibuja la pantalla de navegacion"""
    clear_screen()
    cursor_content = contents[cursor_index]
    print(f"Path actual : {current_path}")
    # Si hay mas de 25 elementos, los dibuja en dos columnas
    if len(contents) >= 26:
        middle_index = len(contents) // 2
        content_first_half = contents[:middle_index]
        content_second_half = contents[middle_index + 1 :]
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
        line = get_format_line(full_path, cursor_content, element)
        print(line)


def title(text: str):
    print(f"{Fore.YELLOW} {text}{Style.RESET_ALL}")


def get_option_format(option: str, is_selected: bool):
    color = Fore.RED if is_selected else Fore.WHITE
    return f"{color} {option} {Style.RESET_ALL}"

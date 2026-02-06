import os
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text
from functools import lru_cache


terminal_size = os.get_terminal_size()
console = Console(width=terminal_size.columns, height=terminal_size.lines)


def clear_screen():
    console.clear()


def print_error(message: str):
    console.print(message, style="bold red", justify="center")


def print_success(message: str):
    console.print(message, style="bold green", justify="center")


@lru_cache(maxsize=30)
def get_format_line(current_path: str, cursor_content: str, element: str) -> Text:
    """Retorna la linea formateada de un element dependiendo de qué sea este"""
    full_path = os.path.join(current_path, element)
    is_dir = os.path.isdir(full_path)
    style = ""
    style = "white" * (element == cursor_content)
    if not style:
        style = (
            f"{'red' if is_dir else 'green'} "
            + f"{'bold' if element == cursor_content else ''}"
        )

    icon = "📁" if is_dir else "📄"
    result = Text(f"{icon} {element}")
    result.stylize(style)
    return result


def render_picker(contents: list[str], cursor_index: int, current_path: str) -> Panel:
    """Dibuja la pantalla de navegación"""
    if not contents:
        return Panel(Text("No hay contenido"), title=current_path)
    cursor_content = contents[cursor_index]
    max_cols = terminal_size.columns // 30
    if max_cols < 1:
        max_cols = 1
    if len(contents) > terminal_size.lines:
        cols = min(len(contents), max_cols)
        elements_per_col = (len(contents) + cols - 1) // cols
        dir_group = [[] for _ in range(cols)]
        for i in range(len(contents)):
            element = contents[i]
            col_index = i // elements_per_col
            result = get_format_line(current_path, cursor_content, element)
            dir_group[col_index].append(result)
        columns = [Text("\r\n").join(col) for col in dir_group]
        return Panel(Columns(columns, equal=False, expand=True, title=current_path))
    else:
        result_table = []

        for i, element in enumerate(contents):
            result = get_format_line(current_path, cursor_content, element)
            result_table.append(result)

        return Panel(
            Text("\n").join(result_table),
            title=current_path,
            title_align="left",
        )


def render_choise(option_index: int, options: list[str]):
    texts = []
    for index, option in enumerate(options):
        texts.append(get_option_format(option, (index == option_index)))
    result = Text("\n").join(texts)
    return Panel(result)


def title(text: str):
    console.print(f"{text}", style="bold yellow")


def get_option_format(option: str, is_selected: bool):
    text = Text(option)
    text.stylize("bold red" if is_selected else "white")
    return text

import platform
from dataclasses import dataclass
import os

actual_os = platform.system()
windows = "windows"


# Estados en los que puede estar el bucle principal
@dataclass
class States:
    dir_picker = 0
    venv_creator = 1
    library_installer = 2
    create_dir = 3
    choise_action = 4


@dataclass
class Path:
    user = os.path.expanduser("~")
    python = ".venv/scripts/python" if actual_os == windows else ".venv/bin/python"

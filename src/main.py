import os
from constants import States, actual_os, windows
from lives import draw_picker, venv_creator, lib_install, create_dir, choise_action
from functions import config_policy
import globals


def main():
    global current_path, cursor_index, current_state, contents
    user: str = os.path.expanduser("~")
    globals.current_path = user
    globals.contents = os.listdir(globals.current_path)
    os.chdir(globals.current_path)

    if actual_os == windows:
        config_policy()

    is_running = True
    print(
        "📁 Navegá con ↑ ↓ - Enter para entrar, L para instalar libs, Space para crear venv"
    )
    input("Presioná Enter para empezar...")

    actions = {
        States.dir_picker: draw_picker,
        States.venv_creator: venv_creator,
        States.library_installer: lib_install,
        States.create_dir: create_dir,
        States.choise_action: choise_action,
    }

    while is_running:
        actions[globals.current_state]()


if __name__ == "__main__":
    main()

import threading
from queue import Queue
from common_types.game_types import SCREEN_WIDTH, SCREEN_HEIGHT
from games.secret_paint_game.secret_paint_game_updates import SecretPaintGameUpdate
from ui.drawing_utils import apply_ui_scale_int
import subprocess
from pathlib import Path

WEB_RUNNER_PATH = Path(__file__).parent / "web_game_runner"

def launch_secret_paint_game(update_queue: Queue[SecretPaintGameUpdate], ui_scale: float):
    thread = threading.Thread(target=_run_secret_paint_game, args=(update_queue, ui_scale))
    thread.daemon = True # Allows the program to exit even if the thread is running.
    thread.start()


def _run_secret_paint_game(update_queue: Queue[SecretPaintGameUpdate], ui_scale: float):
    proc = subprocess.Popen(
        [
            'python', 
            '-m', 
            'uv', 
            'run', 
            'main.py', 
            str(apply_ui_scale_int(SCREEN_WIDTH, ui_scale)),
            str(apply_ui_scale_int(SCREEN_HEIGHT, ui_scale)),
            'Secret Paint Game',
            'https://paint-chess.onrender.com/',
        ],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW,
        shell=False,
        cwd=WEB_RUNNER_PATH,
    )

    exit_code = None
    while exit_code is None:
        exit_code = proc.poll()

    print(f"Web Game ended with exit code: {exit_code}")

    update_queue.put('finished')

import threading
from queue import Queue
from games.secret_paint_game.secret_paint_game_updates import SecretPaintGameUpdate

def launch_secret_paint_game(update_queue: Queue[SecretPaintGameUpdate]):
    thread = threading.Thread(target=run_secret_paint_game, args=(update_queue,))
    thread.daemon = True # Allows the program to exit even if the thread is running.
    thread.start()


def run_secret_paint_game(update_queue: Queue[SecretPaintGameUpdate]):
    import time
    time.sleep(5)

    update_queue.put('finished')

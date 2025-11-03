from games.secret_dlc_store.secret_dlc_store_update import SecretDLCStoreUpdate, SecretDLCStoreDownloadProgress, SecretDLCIntallationFinish, SecretDLCGameFinish, SecretDLCGError
import games.secret_dlc_store.dlc_networking as dlc_networking
import queue
import threading
import time

def start_getting_dlc(update_queue: queue.Queue[SecretDLCStoreUpdate]):
    thread = threading.Thread(target=manage_dlc, args=(update_queue,))
    thread.daemon = True # Allows the program to exit even if the thread is running.
    thread.start()


def manage_dlc(update_queue: queue.Queue[SecretDLCStoreUpdate]):
    def update_progress(percent: float):
        update_queue.put(SecretDLCStoreDownloadProgress(percent))

    if not dlc_networking.download_dlc(update_progress):
        update_queue.put(SecretDLCGError())
        return
    
    if not dlc_networking.extract_dlc_zip():
        update_queue.put(SecretDLCGError())
        return
    
    update_queue.put(SecretDLCIntallationFinish())
    time.sleep(0.5)

    proc = dlc_networking.run_dlc_executable()

    if proc is None:
        return
    
    # Wait until the process running the DLC game exits.
    exit_code = None
    while exit_code is None:
        exit_code = proc.poll()

    print(f"LOG: DLC game terminated with exit code {exit_code}")
    dlc_networking.cleanup_dlc_files()

    update_queue.put(SecretDLCGameFinish())

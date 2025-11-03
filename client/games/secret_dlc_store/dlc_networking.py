import requests
import os
import subprocess
import zipfile
from pathlib import Path
import shutil

from typing import Callable

DLC_PATH = Path(__file__).parent / "dlc"

DOWNLOAD_URL = "https://github.com/cyan-wolf/Rust-Adventure/releases/download/v0.0.1/Rust.Adventure.zip"
DOWNLOAD_PATH = DLC_PATH / "downloads"
DOWNLOAD_FILE = DOWNLOAD_PATH / "download.zip"

EXTRACT_DIR = DLC_PATH / "Rust Adventure"
GAME_EXE_PATH = EXTRACT_DIR / "Rust Adventure.exe"

CHUNK_SIZE_BYTES = 8192

def download_dlc(update_progress: Callable[[float], None]) -> bool:
    try:
        resp = requests.get(DOWNLOAD_URL, stream=True)
        resp.raise_for_status()

        if not os.path.exists(DOWNLOAD_PATH):
            os.makedirs(DOWNLOAD_PATH)

        progress_bytes = 0
        total_size_bytes = int(resp.headers.get('content-length', 0))

        with open(DOWNLOAD_FILE, "wb") as f:
            for chunk in resp.iter_content(chunk_size=CHUNK_SIZE_BYTES):
                if chunk:
                    f.write(chunk)
                    progress_bytes += CHUNK_SIZE_BYTES

                    if total_size_bytes != 0:
                        # Callback to track progress.
                        update_progress(progress_bytes / total_size_bytes)

        print("LOG: Successfully downloaded file.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error: Could not download DLC due to: {e}")
        return False


def extract_dlc_zip() -> bool:
    try: 
        with zipfile.ZipFile(DOWNLOAD_FILE, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)

        print("LOG: Successfully extracted DLC.")
        return True
    
    except zipfile.BadZipFile:
        print("Error: could not extract downloaded DLC archive")
        return False
    

def run_dlc_executable():
    if not os.path.exists(GAME_EXE_PATH):
        print("Error: Could not locate DLC executable to run.")
        return None
    
    try:
        proc = subprocess.Popen(
            [GAME_EXE_PATH],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            shell=False,
        )
        return proc
    
    except FileNotFoundError:
        print("Error: Could not execute DLC file.")


def cleanup_dlc_files():
    if os.path.exists(DLC_PATH):
        shutil.rmtree(DLC_PATH)
        print("LOG: Cleaned up DLC files.")


# def run_dlc():
#     if not download_dlc():
#         return
    
#     if not extract_dlc_zip():
#         return
    
#     run_dlc_executable()


# if __name__ == "__main__":
#     run_dlc()
        
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import uuid
import os
import threading
import time
from collections import defaultdict
from typing import Dict

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# EN_MODEL_PATH = os.path.join(BASE_DIR, "models/vits_English_Female/best_model.pth")
# EN_CONFIG_PATH = os.path.join(BASE_DIR, "models/vits_English_Female/config.json")
EN_MODEL_PATH = os.path.join(BASE_DIR, "models/vits_English_Female/best_model.pth")
EN_CONFIG_PATH = os.path.join(BASE_DIR, "models/vits_English_Female/config.json")
HI_MODEL_PATH = os.path.join(BASE_DIR, "models/vits_Hindi_Female/best_model.pth")
HI_CONFIG_PATH = os.path.join(BASE_DIR, "models/vits_Hindi_Female/config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "tts_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

tts_cache_lock = threading.Lock()
tts_cache: Dict[str, dict] = {}  # {text: {"file": path, "last_access": timestamp, "lang": "en"/"hi"}}
CACHE_EXPIRY_SECONDS = 300  # 5 minutes


def delete_file_later(path):
    def _delete():
        try:
            os.remove(path)
        except Exception as e:
            print(f"Failed to delete TTS file {path}: {e}")
    threading.Timer(5.0, _delete).start()  # Delete after 5 seconds

def get_tts_cache_key(text: str, lang: str) -> str:
    return f"{lang}:{text}"

def cleanup_tts_cache():
    while True:
        now = time.time()
        with tts_cache_lock:
            expired_keys = [key for key, val in tts_cache.items() if now - val["last_access"] > CACHE_EXPIRY_SECONDS]
            for key in expired_keys:
                try:
                    os.remove(tts_cache[key]["file"])
                except Exception as e:
                    print(f"Failed to delete expired TTS file {tts_cache[key]['file']}: {e}")
                del tts_cache[key]
        time.sleep(60)  # Check every minute

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_tts_cache, daemon=True)
cleanup_thread.start()


def get_or_generate_tts(text: str, lang: str, model_path: str, config_path: str) -> str:
    key = get_tts_cache_key(text, lang)
    now = time.time()
    with tts_cache_lock:
        if key in tts_cache and os.path.exists(tts_cache[key]["file"]):
            tts_cache[key]["last_access"] = now
            return tts_cache[key]["file"]
    # Not cached or file missing, generate
    output_file = os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}.wav")
    cmd = [
        "tts",
        "--text", text,
        "--model_path", model_path,
        "--config_path", config_path,
        "--out_path", output_file
    ]
    subprocess.run(cmd, check=True)
    with tts_cache_lock:
        tts_cache[key] = {"file": output_file, "last_access": now, "lang": lang}
    return output_file

def cleanup_all_tts_files():
    """Delete all TTS output files and clear the cache."""
    with tts_cache_lock:
        for key, val in list(tts_cache.items()):
            try:
                if os.path.exists(val["file"]):
                    os.remove(val["file"])
            except Exception as e:
                print(f"Failed to delete TTS file {val['file']}: {e}")
            del tts_cache[key]
    # Also delete any stray files in OUTPUT_DIR
    for fname in os.listdir(OUTPUT_DIR):
        fpath = os.path.join(OUTPUT_DIR, fname)
        try:
            if os.path.isfile(fpath):
                os.remove(fpath)
        except Exception as e:
            print(f"Failed to delete stray TTS file {fpath}: {e}")


@router.post("/tts/english")
async def english_tts(request: Request):
    start_time = time.time()
    data = await request.json()
    parse_time = time.time()
    text = data.get("text")
    if not text:
        return JSONResponse({"error": "No text provided."}, status_code=400)
    try:
        print(f"[TTS] Time to parse request: {parse_time - start_time:.3f}s")
        tts_start = time.time()
        output_file = get_or_generate_tts(text, "en", EN_MODEL_PATH, EN_CONFIG_PATH)
        tts_end = time.time()
        print(f"[TTS] Time for TTS (cached or generated): {tts_end - tts_start:.3f}s")
        response = FileResponse(output_file, media_type="audio/wav")
        file_response_time = time.time()
        print(f"[TTS] Time to prepare FileResponse: {file_response_time - tts_end:.3f}s")
        total_time = time.time() - start_time
        print(f"[TTS] Total time for /tts/english: {total_time:.3f}s")
        return response
    except subprocess.CalledProcessError as e:
        print(f"TTS subprocess error: {e}")
        return JSONResponse({"error": "TTS generation failed."}, status_code=500)

@router.post("/tts/hindi")
async def hindi_tts(request: Request):
    start_time = time.time()
    data = await request.json()
    parse_time = time.time()
    text = data.get("text")
    if not text:
        return JSONResponse({"error": "No text provided."}, status_code=400)
    try:
        print(f"[TTS] Time to parse request: {parse_time - start_time:.3f}s")
        tts_start = time.time()
        output_file = get_or_generate_tts(text, "hi", HI_MODEL_PATH, HI_CONFIG_PATH)
        tts_end = time.time()
        print(f"[TTS] Time for TTS (cached or generated): {tts_end - tts_start:.3f}s")
        response = FileResponse(output_file, media_type="audio/wav")
        file_response_time = time.time()
        print(f"[TTS] Time to prepare FileResponse: {file_response_time - tts_end:.3f}s")
        total_time = time.time() - start_time
        print(f"[TTS] Total time for /tts/hindi: {total_time:.3f}s")
        return response
    except subprocess.CalledProcessError as e:
        print(f"TTS subprocess error: {e}")
        return JSONResponse({"error": "TTS generation failed."}, status_code=500) 
import os
import json
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from pathlib import Path
from datetime import datetime, timezone
from model_loader import reset_model

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_MODEL_NAME = os.getenv("SUPABASE_MODEL_BUCKET")

# Local paths

MODEL_DIR = "models"
LOCAL_MODEL_FILE = os.path.join(MODEL_DIR, "final_model_latest.tflite")
LOCAL_LABELS_FILE = os.path.join(MODEL_DIR, "labels_full.txt")

# Remote paths inside the bucket (with folder prefix!)
REMOTE_MODEL_FILE = "models/final_model_latest.tflite"
REMOTE_LABELS_FILE = "models/labels_full.txt"


CACHE_FILE = os.path.join(MODEL_DIR, "model_cache.json")
CACHE_TTL = 600  # 10 minutes


def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(data: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


# Ensure local models folder exists
os.makedirs(MODEL_DIR, exist_ok=True)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_remote_last_modified(bucket_name: str, remote_file: str) -> datetime | None:
    """Get last modified timestamp of a file in Supabase storage"""
    try:
        # extract folder from remote_file
        folder = os.path.dirname(remote_file)
        name = os.path.basename(remote_file)

        files = supabase.storage.from_(bucket_name).list(folder)
        print("📂 Files in bucket/models/:")
        for f in files:
            print(" -", f["name"])
            if f["name"] == name:
                return datetime.fromisoformat(f["updated_at"].replace("Z", "+00:00"))
    except Exception as e:
        print(f"⚠️ Error fetching metadata for {remote_file}: {e}")
    return None

def download_if_newer(bucket_name: str, remote_file: str, local_path: str):
    """Download file from Supabase if it's missing or outdated"""
    try:

        cache = load_cache()
        now = time.time()

        local_exists = Path(local_path).exists()

        # get cached timestamp if available
        cache_entry = cache.get(remote_file, {})
        cached_ts = cache_entry.get("remote_ts")
        cached_at = cache_entry.get("cached_at", 0)

        remote_last_modified = None


        # only refresh Supabase if cache expired
        if (now - cached_at) > CACHE_TTL or not cached_ts:
            remote_last_modified = get_remote_last_modified(bucket_name, remote_file)
            if remote_last_modified:
                cache[remote_file] = {
                    "remote_ts": remote_last_modified.isoformat(),
                    "cached_at": now
                }
                save_cache(cache)
        else:
            remote_last_modified = datetime.fromisoformat(cached_ts)


        # Compare timestamps
        should_download = True

        if local_exists and remote_last_modified:
            local_mtime = datetime.fromtimestamp(Path(local_path).stat().st_mtime, tz=timezone.utc)
            if local_mtime >= remote_last_modified:
                should_download = False

        if should_download:
            response = supabase.storage.from_(bucket_name).download(remote_file)
            if response:
                with open(local_path, "wb") as f:
                    f.write(response)
                print(f"✅ Synced {remote_file} → {local_path}")


                 # Reset if we just updated the model
                if "tflite" in remote_file:
                    reset_model()
            else:
                raise FileNotFoundError(f"{remote_file} missing in Supabase bucket.")
        else:
            print(f"⏩ Using cached {local_path}, already up to date.")
    except Exception as e:
        print(f"⚠️ Error syncing {remote_file}: {e}")

def sync_model_files():
    """Ensure model + labels are up-to-date locally"""
    download_if_newer(BUCKET_MODEL_NAME, REMOTE_MODEL_FILE, LOCAL_MODEL_FILE)
    download_if_newer(BUCKET_MODEL_NAME, REMOTE_LABELS_FILE, LOCAL_LABELS_FILE)

if __name__ == "__main__":
    sync_model_files()
# utils/storage_helper.py
import os
from datetime import datetime

_run_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

def get_version_folder(base_dir='data/profile_versions') -> str:
    """
    Creates and returns a single version folder for the entire session,
    based on the first time this function is called.
    """
    full_path = os.path.join(base_dir, _run_timestamp)
    os.makedirs(full_path, exist_ok=True)
    return full_path
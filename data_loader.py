# Data Loader .py loading data from folders path
#=============================================================================================
import os
import re
import numpy as np
#=============================================================================================

GID_PATTERN = re.compile(
    r"(?P<channel>.+)-(?P<param>[A-Z]+)_(?P<crank>\d{6})\.GID",
    re.IGNORECASE
)

def read_gid_file(filepath):
    """
    Reads a GID file:
    - skips header until 'END'
    - removes first column
    - returns 2D numpy array
    """
    data = []
    with open(filepath, "r") as f:
        lines = f.readlines()

    start = False
    for line in lines:
        if start:
            parts = line.strip().split()
            if len(parts) > 1:
                data.append([float(x) for x in parts[1:]])
        elif line.strip() == "END":
            start = True

    return np.array(data)


def load_channel_folder(folder_path):
    """
    Loads all GID files in a folder, parses crank angle from filename,
    sorts them, and returns:
        frames: list[np.ndarray]
        crank_angles: list[int]
    """
    all_files = os.listdir(folder_path)
    #print("DEBUG all files:", all_files)

    gid_files = []

    for fname in all_files:
        match = GID_PATTERN.match(fname)
        if match:
            crank = int(match.group("crank"))
            gid_files.append((crank, fname))

    #print("DEBUG GID files:", len(gid_files))

    if not gid_files:
        raise RuntimeError(f"No valid GID files found in {folder_path}")

    # sort by crank angle
    gid_files.sort(key=lambda x: x[0])

    frames = []
    crank_angles = []

    for crank, fname in gid_files:
        full_path = os.path.join(folder_path, fname)
        data = read_gid_file(full_path)
        frames.append(data)
        crank_angles.append(crank)

    return frames, crank_angles

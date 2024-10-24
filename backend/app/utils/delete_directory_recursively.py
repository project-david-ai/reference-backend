import os
import shutil


def delete_directory_recursively(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted: {path}")
    else:
        print(f"Directory does not exist: {path}")

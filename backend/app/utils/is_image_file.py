import os


def is_image_file(file_url):
    _, file_extension = os.path.splitext(file_url)
    return file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']
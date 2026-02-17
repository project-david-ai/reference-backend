import os
from urllib.parse import urlparse


def get_file_name_and_extension(url):

    parsed_url = urlparse(url)
    file_path = parsed_url.path
    file_name = os.path.basename(file_path)
    file_name = file_name.replace("%5B", "[").replace(
        "%5D", "]"
    )  # Decode URL-encoded characters
    file_extension = os.path.splitext(file_name)[1]
    return file_name, file_extension


def save_file_objects_locally(file_objects, file_urls, output_directory):

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    saved_file_paths = []

    for file_object, file_url in zip(file_objects, file_urls):
        file_name, file_extension = get_file_name_and_extension(file_url)
        file_path = os.path.join(output_directory, file_name)

        with open(file_path, "wb") as destination:
            file_object.seek(0)
            destination.write(file_object.read())

        saved_file_paths.append(file_path)

    return saved_file_paths

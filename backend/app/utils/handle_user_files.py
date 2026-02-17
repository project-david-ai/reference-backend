import re
from urllib.parse import unquote


def handle_user_files(upload_service, user_id, thread_id, entity):
    """
    Handles retrieval and preparation of user files from GCS.
    This function fetches file URLs for a given user and thread from GCS and prepares file objects
    from those URLs for further processing, like appending to messages or processing by an AI model.

    Parameters:
    - upload_service (GCSUploadService): An instance of the GCSUploadService class responsible for interacting with GCS.
    - user_id (str): The ID of the user whose files are being handled.
    - thread_id (str): The ID of the thread for which files are being handled.

    Returns:
    - tuple: A tuple containing two lists: file_urls (list of str), and file_objects (list of file-like objects).
    """

    if entity == "q":
        pattern = r"https://storage\.googleapis\.com/q_retrieval/(.*)"
    if entity == "r":
        pattern = r"https://storage\.googleapis\.com/r_retrieval/(.*)"

    # Fetch file URLs from GCS for the given user and thread
    try:
        file_urls = upload_service.find_user_files_by_thread_id(user_id, thread_id)
        if file_urls:
            print("Files found for user", user_id, "and thread", thread_id)
            for file_url in file_urls:
                print(file_url)
        else:
            print("No files found for user", user_id, "and thread", thread_id)
            return [], []  # Return empty lists if no files are found
    except Exception as e:
        print(f"Error fetching user files: {e}")
        return [], []  # Return empty lists in case of an error

    # Prepare file objects from the fetched file URLs
    file_objects = []
    for file_url in file_urls:
        try:
            # Extract the relative file path from the URL using regex
            match = re.search(pattern, file_url)
            if match:
                file_path = match.group(1)
                # URL-decode the file path
                file_path = unquote(file_path)
                # Open the file using the decoded file path
                file_object = upload_service.open_file(file_path)
                file_objects.append(file_object)
            else:
                print(f"Error extracting file path from URL: {file_url}")
        except Exception as e:
            print(f"Error preparing file {file_url}: {e}")
            # Continue processing the next file if unable to prepare the current one

    return file_urls, file_objects


def handle_user_files_simple(upload_service, user_id):
    """
    Handles retrieval and preparation of user files from GCS without considering thread_id.
    This function fetches file URLs for a given user from GCS and prepares file objects
    from those URLs for further processing, like appending to messages or processing by an AI model.

    Parameters:
    - upload_service (GCSUploadService): An instance of the GCSUploadService class responsible for interacting with GCS.
    - user_id (str): The ID of the user whose files are being handled.

    Returns:
    - tuple: A tuple containing two lists: file_urls (list of str), and file_objects (list of file-like objects).
    """
    # Fetch file URLs from GCS for the given user
    try:
        file_urls = upload_service.find_user_files_simple(user_id)
        if file_urls:
            print("Files found for user", user_id)
            for file_url in file_urls:
                print(file_url)
        else:
            print("No files found for user", user_id)
            return [], []  # Return empty lists if no files are found
    except Exception as e:
        print(f"Error fetching user files: {e}")
        return [], []  # Return empty lists in case of an error

    # Prepare file objects from the fetched file URLs
    file_objects = []
    for file_url in file_urls:
        try:
            # Extract the relative file path from the URL using regex
            pattern = r"https://storage\.googleapis\.com/q_retrieval/(.*)"
            match = re.search(pattern, file_url)
            if match:
                file_path = match.group(1)
                # URL-decode the file path
                file_path = unquote(file_path)
                # Open the file using the decoded file path
                file_object = upload_service.open_file(file_path)
                file_objects.append(file_object)
            else:
                print(f"Error extracting file path from URL: {file_url}")
        except Exception as e:
            print(f"Error preparing file {file_url}: {e}")
            # Continue processing the next file if unable to prepare the current one

    return file_urls, file_objects

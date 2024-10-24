import magic


def get_file_type(file_obj):
    try:
        # Create a magic object
        m = magic.Magic(mime=True)

        # Get the MIME type of the file
        file_type = m.from_buffer(file_obj.getvalue())
        return file_type
    except Exception as e:
        print(f"Error determining file type: {e}")
        return None
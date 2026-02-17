def determine_media_type(file_id):
    file_extension = file_id.split(".")[-1].lower()
    # Add additional types as necessary
    media_type_map = {
        "png": "image",
        "jpg": "image",
        "jpeg": "image",
        "gif": "image",
        "pdf": "pdf",
        "txt": "text",
        "csv": "text",
        "md": "text",
        "doc": "document",
        "docx": "document",
        "pptx": "presentation",
        "xlsx": "spreadsheet",
        "c": "code",
        "cs": "code",
        "cpp": "code",
        "java": "code",
        "php": "code",
        "py": "code",
        "rb": "code",
        "js": "code",
        "ts": "code",
        "sh": "code",
        "html": "markup",
        "css": "markup",
        "xml": "markup",
        "zip": "archive",
        "tar": "archive",
    }
    return media_type_map.get(file_extension, "other")

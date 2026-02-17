from backend.app.services.google_services.upload_files_to_gcs_service.gcs_upload_service import \
    GCSUploadService
from backend.app.utils.handle_user_files import (handle_user_files,
                                                 handle_user_files_simple)


class UserContentService:
    def __init__(self, entity):
        self.entity = entity
        self.bucket_name = f"{entity}_retrieval"

    def handle_user_content(self, user_id, thread_id):
        upload_service = GCSUploadService(bucket_name=self.bucket_name)
        file_urls, file_objects = handle_user_files(
            upload_service, user_id, thread_id, entity=self.entity
        )
        return file_urls, file_objects

    def handle_user_content_simple(self, user_id):
        upload_service = GCSUploadService(bucket_name=self.bucket_name)
        file_urls, file_objects = handle_user_files_simple(upload_service, user_id)
        return file_urls, file_objects

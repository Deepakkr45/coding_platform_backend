# controllers/file_controller.py
import logging
from utils.file_utils import save_file, list_files, delete_file, validate_upload

MAX_FILES_PER_USER = 10

# Setup logging
logging.basicConfig(level=logging.INFO)

def upload_user_file(file, user_id):
    """Handles file upload with validation and saves it."""
    validation_error = validate_upload(file, user_id)
    if validation_error:
        return validation_error

    file_path = save_file(file, user_id, file.filename)
    
    if file_path == "exists":
        return {"error": "File already exists"}, 409
    elif file_path == "limit_exceeded":
        return {"error": "File limit exceeded. Delete old files."}, 400
    elif isinstance(file_path, str):
        logging.info(f"File '{file.filename}' uploaded by User {user_id}")
        return {"message": f"File '{file.filename}' uploaded successfully"}, 201
    else:
        return {"error": "Unknown error occurred while saving file."}, 500

def list_user_files(user_id):
    """Lists all uploaded files for a user."""
    files = list_files(user_id)
    return {"files": files}, 200

def delete_user_file(user_id, filename):
    """Deletes a specific file for a user."""
    if not delete_file(user_id, filename):
        return {"error": "File not found"}, 404
    logging.info(f"File '{filename}' deleted by User {user_id}")
    return {"message": f"File '{filename}' deleted successfully"}, 200
import os
import logging

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {'csv', 'json'}

# Set up logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_upload(file, user_id):
    """Validates user ID and file before uploading."""
    if not user_id or not isinstance(user_id, str):
        return {"status": "error", "message": "Valid User ID is required"}, 400
    if file.filename == '':
        return {"status": "error", "message": "No file selected"}, 400
    if not allowed_file(file.filename):
        return {"status": "error", "message": "Only CSV & JSON files allowed"}, 415  # Unsupported Media Type
    return None

def find_channel_name_by_id(channel_id, data):
    """Find channel name from channel ID."""
    for channel in data.get('channels', []):
        if channel.get('_id') == channel_id:
            return channel.get('name')
    return None

def save_csv_to_disk(token, content, file_name):
    """Save CSV content to disk."""
    try:
        user_folder = os.path.join(UPLOAD_DIR, token)
        os.makedirs(user_folder, exist_ok=True)

        file_path = os.path.join(user_folder, f'{file_name}.csv')

        with open(file_path, 'wb') as f:
            f.write(content)

        return file_path
    except Exception as e:
        logging.error(f"Failed to save CSV file: {e}")
        return {"status": "error", "message": "Failed to save CSV file"}, 500  # Internal Server Error

def save_file(file, user_id, filename):
    """Save a file to the user's upload folder."""
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)

    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        return {"status": "error", "message": "File already exists"}, 409  # Conflict

    if len(os.listdir(user_folder)) >= 10:
        return {"status": "error", "message": "File limit exceeded. Delete old files."}, 403  # Forbidden

    file.save(file_path)
    return {"status": "success", "message": "File uploaded successfully", "file_path": file_path}, 201  # Created

def list_files(user_id):
    """List all files for a user."""
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    if not os.path.exists(user_folder):
        return {"status": "success", "files": []}, 200  # Return empty list instead of error
    return {"status": "success", "files": os.listdir(user_folder)}, 200

def delete_file(user_id, filename):
    """Delete a specific file for a user."""
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    file_path = os.path.join(user_folder, filename)

    if not os.path.exists(file_path):
        return {"status": "error", "message": "File not found"}, 404  # Not Found

    os.remove(file_path)
    return {"status": "success", "message": f"File '{filename}' deleted successfully"}, 200  # OK

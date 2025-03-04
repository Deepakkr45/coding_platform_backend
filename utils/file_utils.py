import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {'csv', 'json'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_upload(file, user_id):
    """Validates user ID and file before uploading."""
    if not user_id or not isinstance(user_id, str):
        return {"error": "Valid User ID is required"}, 400
    if file.filename == '':
        return {"error": "No file selected"}, 400
    if not allowed_file(file.filename):
        return {"error": "Only CSV & JSON files allowed"}, 400
    return None

def save_file(file, user_id, filename):
    """Save a file to the user's upload folder."""
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)  # Ensure directory exists
    file_path = os.path.join(user_folder, filename)
    
    if os.path.exists(file_path):
        return "exists"
    
    if len(os.listdir(user_folder)) >= 10:
        return "limit_exceeded"
    
    file.save(file_path)
    return file_path

def list_files(user_id):
    """List all files for a user."""
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    if not os.path.exists(user_folder):
        return []
    return os.listdir(user_folder)

def delete_file(user_id, filename):
    """Delete a specific file for a user."""
    user_folder = os.path.join(UPLOAD_DIR, user_id)
    file_path = os.path.join(user_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

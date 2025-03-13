import os
import logging
import config
import requests

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
        return {"error": "Valid User ID is required"}, 400
    if file.filename == '':
        return {"error": "No file selected"}, 400
   
    if ' ' in file.filename:
        return {"error": "File name should not contain spaces"}, 400
    if not allowed_file(file.filename):
        return {"error": "Only CSV & JSON files allowed"}, 400
    return None


def fetch_user_id(token):
    headers = {"Authorization": token}
    try:
        response = requests.get(config.user_api, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            user_id = response_data.get("user")

            if user_id:
                return user_id
            else:
                print("User ID not found in the response")
                return None
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
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
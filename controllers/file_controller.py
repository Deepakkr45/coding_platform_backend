import logging
from utils.file_utils import save_file, list_files, delete_file, validate_upload, save_csv_to_disk, find_channel_name_by_id, fetch_user_id, rename_file
import config
import requests
import json

MAX_FILES_PER_USER = 10

NODEJS_API_URL = config.export_api
FETCH_CHANNELS_URL = config.channel_fetch

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

def fetch_user_data(channel_id, token):
    """Fetch CSV from Node.js backend and save it."""
    if not channel_id:
        return {"status": "error", "message": "Channel ID is required"}, 400

    try:
        # Fetch the CSV file from the Node.js backend
        nodejs_response = requests.get(NODEJS_API_URL.format(channel_id=channel_id))

        channels_json = requests.get(
            FETCH_CHANNELS_URL,
            headers={'Authorization': token}
        )
        file_name = find_channel_name_by_id(channel_id, channels_json.json())

        logging.info(f"Fetching data for channel {channel_id} - Status: {nodejs_response.status_code}")

        # Raise an error for bad status codes
        nodejs_response.raise_for_status()

        if not nodejs_response.text.strip():  # Check if the response is empty
            return {"status": "error", "message": "Empty response received"}, 204
        if file_name is None:
            return {"status": "error", "message": "Channel does not exist"}, 404

        user_id = fetch_user_id(token)

        if user_id:
            file_path = save_csv_to_disk(user_id, nodejs_response.content, file_name)
            if not file_path:
                return {"status": "error", "message": "Failed to save CSV file"}, 500

            logging.info(f"CSV file for channel {channel_id} fetched and saved successfully.")
            return {"status": "success", "message": f"CSV file for channel {channel_id} saved successfully"}, 200
        else:
            return {"error": "No user ID exists, please login again."}, 401
        


    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch CSV file from Database: {e}")
        return {"status": "error", "message": "Failed to fetch CSV file from the database"}, 500

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

# Function to handle renaming logic
def rename_user_file(user_id, old_filename, new_filename):
    """Renames a specific file for a user."""
    if not rename_file(user_id, old_filename, new_filename):
        return {"error": "File not found or new filename already exists"}, 404
    logging.info(f"File '{old_filename}' renamed to '{new_filename}' by User {user_id}")
    return {"message": f"File '{old_filename}' renamed to '{new_filename}' successfully"}, 200
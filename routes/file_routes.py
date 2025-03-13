from flask import Blueprint, request, jsonify
import logging
from controllers.file_controller import upload_user_file, list_user_files, delete_user_file, fetch_user_data
from utils.file_utils import fetch_user_id
file_routes = Blueprint('files', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@file_routes.route('/upload', methods=['POST'])
def upload_file():
    # Get the authorization token from the request headers
    token = request.headers.get('Authorization')

    # Get the file from the request 
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Call the function to fetch user data
    user_id = fetch_user_id(token)

    if user_id:
        # If user_id exists, proceed with uploading the file
        response, status = upload_user_file(file, user_id)
        return jsonify(response), status
    else:
        # If no user_id exists, return an error message
        return jsonify({"error": "No user ID exists, please login again."}), 401


@file_routes.route('/fetch', methods=['POST'])
def fetch_csv():
    """Fetches CSV file from backend based on channel_id."""
    token = request.headers.get('Authorization')
    if not token:
        logging.warning("Fetch attempt without token.")
        return jsonify({"status": "error", "message": "Authorization token is required"}), 401

    request_data = request.get_json()
    channel_id = request_data.get('channel_id')

    if not channel_id:
        return jsonify({"status": "error", "message": "Channel ID is required"}), 400


    response, status = fetch_user_data(channel_id, token)
    return jsonify(response), status

@file_routes.route('/list', methods=['GET'])
def list_files():
    # user_id = request.args.get('user_id')
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "token is required"}), 400
    user_id = fetch_user_id(token)
    response, status = list_user_files(user_id)
    return jsonify(response), status

@file_routes.route('/delete', methods=['DELETE'])
def delete_file():
    data = request.json
    token = request.headers.get('Authorization')
    # user_id = data.get('user_id')
    filename = data.get('filename')
    if not token or not filename:
        return jsonify({"error": "User ID and filename are required"}), 400
    user_id = fetch_user_id(token)
    response, status = delete_user_file(user_id, filename)
    return jsonify(response), status


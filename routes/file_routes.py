from flask import Blueprint, request, jsonify
import logging
from controllers.file_controller import upload_user_file, list_user_files, delete_user_file, fetch_user_data

file_routes = Blueprint('files', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@file_routes.route('/upload', methods=['POST'])
def upload_file():
    """Handles file upload request."""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Missing file"}), 400

    token = request.headers.get('Authorization')
    if not token:
        logging.warning("Upload attempt without token.")
        return jsonify({"status": "error", "message": "Authorization token is required"}), 401

    file = request.files['file']
    response, status = upload_user_file(file, token)
    return jsonify(response), status

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
    """Lists all uploaded files for the authenticated user."""
    token = request.headers.get('Authorization')
    if not token:
        logging.warning("List files attempt without token.")
        return jsonify({"status": "error", "message": "Authorization token is required"}), 401

    response, status = list_user_files(token)
    return jsonify(response), status

@file_routes.route('/delete', methods=['DELETE'])
def delete_file():
    """Deletes a specific file for the user."""
    token = request.headers.get('Authorization')
    if not token:
        logging.warning("Delete attempt without token.")
        return jsonify({"status": "error", "message": "Authorization token is required"}), 401

    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({"status": "error", "message": "Filename is required"}), 400

    response, status = delete_user_file(token, filename)
    return jsonify(response), status

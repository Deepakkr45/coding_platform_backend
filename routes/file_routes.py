from flask import Blueprint, request, jsonify
import logging
from controllers.file_controller import upload_user_file, list_user_files, delete_user_file, fetch_user_data, rename_user_file
from utils.file_utils import fetch_user_id
file_routes = Blueprint('files', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@file_routes.route('/upload', methods=['POST'])
def upload_file_route():
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
        return jsonify({"error": "Session ended, Please login again"}), 401


@file_routes.route('/fetch', methods=['POST'])
def fetch_csv_route():
    """Fetches CSV file from backend based on channel_id."""
    token = request.headers.get('Authorization')
    token = 'Bearer ' + token
    if not token:
        logging.warning("Fetch attempt without token.")
        return jsonify({"status": "error", "message": "token is required"}), 401

    request_data = request.get_json()
    # print("this is req data",request_data)
    channel_id = request_data.get('channel_id')
    # print("this is channel data",channel_id)


    if not channel_id:
        return jsonify({"status": "error", "message": "Channel ID is required"}), 400


    response, status = fetch_user_data(channel_id, token)
    return jsonify(response), status

@file_routes.route('/list', methods=['GET'])
def list_files_route():
    # user_id = request.args.get('user_id')
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "token is required"}), 400
    user_id = fetch_user_id(token)
    response, status = list_user_files(user_id)
    return jsonify(response), status

@file_routes.route('/delete', methods=['DELETE'])
def delete_file_route():
    data = request.json
    token = request.headers.get('Authorization')
    # user_id = data.get('user_id')
    filename = data.get('filename')
    if not token or not filename:
        return jsonify({"error": "User ID and filename are required"}), 400
    user_id = fetch_user_id(token)
    response, status = delete_user_file(user_id, filename)
    return jsonify(response), status

@file_routes.route('/rename', methods=['POST'])
def rename_file_route():
    data = request.json
    token = request.headers.get('Authorization')

    if not data or 'old_filename' not in data or 'new_filename' not in data:
        return jsonify({"error": "Missing 'old_filename' or 'new_filename' in request body"}), 400

    user_id = fetch_user_id(token)
    if not user_id:
        return jsonify({"error": "Invalid or missing authorization token"}), 401

    old_filename = data.get('old_filename')
    new_filename = data.get('new_filename')

    response, status = rename_user_file(user_id, old_filename, new_filename)
    return jsonify(response), status
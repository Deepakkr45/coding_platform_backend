from flask import Blueprint, request, jsonify
import logging
from controllers.file_controller import upload_user_file, list_user_files, delete_user_file, fetch_user_data

file_routes = Blueprint('files', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@file_routes.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400
    token = request.headers.get('Authorization')
    file = request.files['file']
    # user_id = request.form['user_id']
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
    # user_id = request.args.get('user_id')
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "token is required"}), 400
    response, status = list_user_files(token)
    return jsonify(response), status

@file_routes.route('/delete', methods=['DELETE'])
def delete_file():
    data = request.json
    token = request.headers.get('Authorization')
    # user_id = data.get('user_id')
    filename = data.get('filename')
    if not token or not filename:
        return jsonify({"error": "User ID and filename are required"}), 400
    response, status = delete_user_file(token, filename)
    return jsonify(response), status

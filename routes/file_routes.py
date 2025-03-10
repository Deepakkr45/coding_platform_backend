from flask import Blueprint, request, jsonify
from controllers.file_controller import upload_user_file, list_user_files, delete_user_file

file_routes = Blueprint('files', __name__)

@file_routes.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400
    token = request.headers.get('Authorization')
    file = request.files['file']
    # user_id = request.form['user_id']
    response, status = upload_user_file(file, token)
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

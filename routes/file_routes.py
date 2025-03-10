from flask import Blueprint, request, jsonify
from controllers.file_controller import upload_user_file, list_user_files, delete_user_file

file_routes = Blueprint('files', __name__)

@file_routes.route('/upload', methods=['POST'])
def upload_file(user_id):
    if 'file' not in request.files or 'user_id' not in request.form:
        return jsonify({"error": "Missing file or user ID"}), 400
    file = request.files['file']
    # user_id = request.form['user_id']
    response, status = upload_user_file(file, user_id)
    return jsonify(response), status

@file_routes.route('/list', methods=['GET'])
def list_files(user_id):
    # user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    response, status = list_user_files(user_id)
    return jsonify(response), status

@file_routes.route('/delete', methods=['DELETE'])
def delete_file(user_id):
    data = request.json
    # user_id = data.get('user_id')
    filename = data.get('filename')
    if not user_id or not filename:
        return jsonify({"error": "User ID and filename are required"}), 400
    response, status = delete_user_file(user_id, filename)
    return jsonify(response), status

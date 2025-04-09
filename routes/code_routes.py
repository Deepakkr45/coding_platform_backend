from flask import Blueprint, request, jsonify, send_file
from controllers.code_controller import execute_user_code
from utils.code_utils import allowed_file

code_routes = Blueprint('code_routes', __name__)

@code_routes.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    token = request.headers.get('Authorization')
    response, status = execute_user_code(code,token)
    return jsonify(response), status

@code_routes.route('/export', methods=['POST'])
def export_code():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body must be JSON"}), 400
        if 'code' not in data:
            return jsonify({"status": "error", "message": "Missing 'code' field in request body"}), 400

        code = data['code']
        if not isinstance(code, str) or not code.strip():
            return jsonify({"status": "error", "message": "'code' must be a non-empty string"}), 400

        file_path = "main.py"
        try:
            with open(file_path, "w") as f:
                f.write(code)
        except IOError as e:
            return jsonify({"status": "error", "message": f"Failed to write file: {str(e)}"}), 500

        return send_file(file_path, as_attachment=True, download_name="main.py")

    except Exception as e:
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}), 500

@code_routes.route('/import', methods=['POST'])
def import_code():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided in the request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"status": "error", "message": "Invalid file type. Only .py files are allowed"}), 415

        try:
            code = file.read().decode("utf-8")
        except UnicodeDecodeError:
            return jsonify({"status": "error", "message": "File could not be decoded as UTF-8"}), 415
        except Exception as e:
            return jsonify({"status": "error", "message": f"Failed to read file: {str(e)}"}), 500

        return jsonify({"status":"success","code": code}),200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


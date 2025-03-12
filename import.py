# from flask import Flask, request, send_file, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# @app.route('/generate', methods=['POST'])
# def generate_file():
#     try:
#         data = request.get_json()
#         if not data or 'code' not in data:
#             return jsonify({"error": "Invalid request, 'code' missing"}), 400

#         code = data['code']
#         file_path = "main.py"

#         with open(file_path, "w") as f:
#             f.write(code)

#         return send_file(file_path, as_attachment=True, download_name="main.py")

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/import', methods=['POST'])
# def import_file():
#     try:
#         if 'file' not in request.files:
#             return jsonify({"error": "No file provided"}), 400
        
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({"error": "No selected file"}), 400

#         code = file.read().decode("utf-8")
#         return jsonify({"code": code})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)


from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import ast
import os

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {"py"}

def is_valid_python_code(code):
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, str(e)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/generate', methods=['POST'])
def generate_file():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({"error": "Invalid request, 'code' missing"}), 400

        code = data['code']
        is_valid, error_message = is_valid_python_code(code)
        if not is_valid:
            return jsonify({"error": f"Invalid Python syntax: {error_message}"}), 400

        file_path = "main.py"
        with open(file_path, "w") as f:
            f.write(code)

        return send_file(file_path, as_attachment=True, download_name="main.py")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/import', methods=['POST'])
def import_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only .py files are allowed."}), 400

        code = file.read().decode("utf-8")
        is_valid, error_message = is_valid_python_code(code)
        if not is_valid:
            return jsonify({"error": f"Invalid Python syntax: {error_message}"}), 400

        return jsonify({"code": code})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  # Add this

app = Flask(__name__)
CORS(app)  # Allow all origins (frontend can now send requests)

@app.route('/generate', methods=['POST'])
def generate_file():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({"error": "Invalid request, 'code' missing"}), 400

        code = data['code']
        file_path = "main.py"

        with open(file_path, "w") as f:
            f.write(code)

        return send_file(file_path, as_attachment=True, download_name="main.py")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Make it accessible

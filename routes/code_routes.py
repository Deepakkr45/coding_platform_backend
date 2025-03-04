from flask import Blueprint, request, jsonify
from controllers.code_controller import execute_user_code

code_routes = Blueprint('code_routes', __name__)

@code_routes.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    user_id = data.get('user_id', '')
    response, status = execute_user_code(code,user_id)
    return jsonify(response), status

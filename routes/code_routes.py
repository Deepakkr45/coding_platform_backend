from flask import Blueprint, request, jsonify
from controllers.code_controller import execute_user_code

code_routes = Blueprint('code_routes', __name__)

@code_routes.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')
    token = request.headers.get('Authorization')
    print(token)
    # user_id = data.get('user_id', '')
    response, status = execute_user_code(code,token)
    return jsonify(response), status


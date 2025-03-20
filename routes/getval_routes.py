from flask import request, jsonify
from flask import Blueprint
import logging
from controllers.getval_controller import get_feild_data

getval_routes = Blueprint('getval_routes', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@getval_routes.route('/read_data', methods=['GET'])
def get_data():
    channel_id = request.args.get('channel_id')
    fields = request.args.getlist('fields')

    if not channel_id or not fields:
        return jsonify({"error": "channel_id and at least one field are required!"}), 400
    
    response, status = get_feild_data(channel_id, fields)

    return jsonify(response), status

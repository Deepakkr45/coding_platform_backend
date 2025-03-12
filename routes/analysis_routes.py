import requests
import logging
from flask import Blueprint, request, jsonify
from controllers.analysis_controller import perform_analysis
from utils.data_cleaning import clean_data
import config

NODEJS_API_URL = config.read_api

analysis_routes = Blueprint('analysis_routes', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@analysis_routes.route('/analysis', methods=['POST'])
def analysis():
    try:
        request_data = request.get_json()
        channel_id = request_data.get('channel_id')
        field = request_data.get('field')
        analysis_type = request_data.get('analysis_type')
        num_entries = request_data.get('num_entries')

        if not all([channel_id, field, analysis_type]):
            return jsonify({'status': 'error', 'message': 'channel_id, field, and analysis_type are required'}), 400

        nodejs_response = requests.get(NODEJS_API_URL.format(channel_id=channel_id))

        if nodejs_response.status_code != 200:
            logging.error(f"Failed to fetch data from Node.js backend. Status: {nodejs_response.status_code}")
            return jsonify({'status': 'error', 'message': 'Failed to fetch data from Node.js backend'}), 502

        nodejs_data = nodejs_response.json()
        data = clean_data(nodejs_data['entries'], field)

        if num_entries is None or num_entries == "":
            num_entries = len(data)
        else:
            num_entries = int(num_entries)
            if num_entries <= 0:
                return jsonify({'status': 'error', 'message': 'Number of entries must be more than 0'}), 400

        if len(data) < num_entries:
            return jsonify({
                'status': 'error',
                'message': f'Requested {num_entries} entries, but only {len(data)} available'
            }), 422  # 422 Unprocessable Entity

        data = data.tail(num_entries)
        result = perform_analysis(data, analysis_type)

        return jsonify({'status': 'success', 'data': result}), 200

    except ValueError as e:
        logging.error(f"ValueError: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred'}), 500  # Internal Server Error

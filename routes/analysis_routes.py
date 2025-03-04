import requests
from flask import Blueprint, request, jsonify
from controllers.analysis_controller import perform_analysis
from utils.data_cleaning import clean_data

NODEJS_API_URL = 'http://cloud.xtranssolutions.com/node/api/channels/{channel_id}/entries/read'

analysis_routes = Blueprint('analysis_routes', __name__)

@analysis_routes.route('/analysis', methods=['POST'])
def analysis():
    try:
        request_data = request.get_json()
        channel_id = request_data.get('channel_id')
        field = request_data.get('field')
        analysis_type = request_data.get('analysis_type')
        num_entries = request_data.get('num_entries')
        token = request.headers.get('Authorization')

        if not all([channel_id, field, analysis_type]):
            return jsonify({'error': 'channel_id, field, and analysis_type are required'}), 400

        nodejs_response = requests.get(
            NODEJS_API_URL.format(channel_id=channel_id),
            headers={'Authorization': token}
        )

        if nodejs_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from Node.js backend'}), 400

        nodejs_data = nodejs_response.json()
        data = clean_data(nodejs_data['entries'], field)

        if num_entries is None or num_entries == "":
            num_entries = len(data)
        else:
            num_entries = int(num_entries)
            if num_entries <= 0:
                return jsonify({'error': 'Number of Entries must be more than 0'}), 400

        if len(data) < num_entries:
            return jsonify({'error': 'Requested {} entries, but only {} available'.format(num_entries, len(data))}), 400

        data = data.tail(num_entries)
        result = perform_analysis(data, analysis_type)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred: {}'.format(str(e))}), 400

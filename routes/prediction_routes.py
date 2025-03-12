import requests
import logging
from flask import Blueprint, request, jsonify
from controllers.prediction_controller import perform_prediction_with_timestamps
from utils.data_cleaning import clean_data
import config

NODEJS_API_URL = config.read_api

prediction_routes = Blueprint('prediction_routes', __name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

@prediction_routes.route('/prediction', methods=['POST'])
def prediction():
    try:
        request_data = request.get_json()
        channel_id = request_data.get('channel_id')
        field = request_data.get('field')
        prediction_hours = request_data.get('prediction_hours')

        if not all([channel_id, field, prediction_hours]):
            return jsonify({'status': 'error', 'message': 'channel_id, field, and prediction_hours are required'}), 400

        try:
            prediction_hours = int(prediction_hours)
            if prediction_hours <= 0:
                return jsonify({'status': 'error', 'message': 'Prediction Hours must be greater than 0'}), 400
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Prediction Hours must be an integer'}), 400

        required_entries = prediction_hours * 12

        nodejs_response = requests.get(NODEJS_API_URL.format(channel_id=channel_id))

        if nodejs_response.status_code != 200:
            logging.error(f"Failed to fetch data from Node.js backend. Status: {nodejs_response.status_code}")
            return jsonify({'status': 'error', 'message': 'Failed to fetch data from Node.js backend'}), 502  # Bad Gateway

        nodejs_data = nodejs_response.json()
        data = clean_data(nodejs_data['entries'], field)

        if len(data) < required_entries:
            return jsonify({
                'status': 'error',
                'message': f'Not enough data for prediction. Required: {required_entries}, Available: {len(data)}'
            }), 422  # Unprocessable Entity

        forecast, timestamps = perform_prediction_with_timestamps(data, prediction_hours)

        return jsonify({
            'status': 'success',
            'forecast': list(zip(timestamps, forecast.tolist()))
        }), 200

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred'}), 500  # Internal Server Error

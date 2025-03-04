import requests
from flask import Blueprint, request, jsonify
from controllers.prediction_controller import perform_prediction_with_timestamps
from utils.data_cleaning import clean_data
import config

NODEJS_API_URL = config.backend_api

prediction_routes = Blueprint('prediction_routes', __name__)

@prediction_routes.route('/prediction', methods=['POST'])
def prediction():
    try:
        request_data = request.get_json()
        channel_id = request_data.get('channel_id')
        field = request_data.get('field')
        prediction_hours = request_data.get('prediction_hours')
        token = request.headers.get('Authorization')

        if not prediction_hours:
            return jsonify({'error': 'Prediction Hours is required'}), 400

        prediction_hours = int(prediction_hours)
        if prediction_hours <= 0:
            return jsonify({'error': 'Prediction Hours must be greater than 0'}), 400

        required_entries = prediction_hours * 12

        nodejs_response = requests.get(
            NODEJS_API_URL.format(channel_id=channel_id),
            headers={'Authorization': token}
        )

        if nodejs_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from Node.js backend'}), 400

        nodejs_data = nodejs_response.json()
        data = clean_data(nodejs_data['entries'], field)

        if len(data) < required_entries:
            return jsonify({'error': 'Not enough data for prediction. Required: {}, Available: {}'.format(required_entries, len(data))}), 400

        forecast, timestamps = perform_prediction_with_timestamps(data, prediction_hours)
        return jsonify({"forecast": list(zip(timestamps, forecast.tolist()))}), 200

    except Exception as e:
        return jsonify({"error": 'An unexpected error occurred: {}'.format(str(e))}), 500

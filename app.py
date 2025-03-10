from flask import Flask
from flask_cors import CORS
# from routes.user_routes import user_routes
from routes.code_routes import code_routes
from routes.file_routes import file_routes
# from database import init_db
from routes.analysis_routes import analysis_routes
from routes.prediction_routes import prediction_routes

app = Flask(__name__)
CORS(app)

# Database Initialization
# init_db(app)

# Register Blueprints (Routes)
app.register_blueprint(code_routes, url_prefix='/code')
app.register_blueprint(file_routes, url_prefix='/file')
app.register_blueprint(analysis_routes, url_prefix='/api')
app.register_blueprint(prediction_routes, url_prefix='/api')


@app.route('/')
def home():
    return "Flask API is running!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

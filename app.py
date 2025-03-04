from flask import Flask
from flask_cors import CORS
# from routes.user_routes import user_routes
from routes.code_routes import code_routes
from routes.file_routes import file_routes
# from database import init_db

app = Flask(__name__)
CORS(app)

# Database Initialization
# init_db(app)

# Register Blueprints (Routes)
app.register_blueprint(code_routes, url_prefix='/api/code')
app.register_blueprint(file_routes, url_prefix='/api/files')

if __name__ == '__main__':
    app.run(debug=True)

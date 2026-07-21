"""Flask application factory."""

from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    # Allow the React dev server (Vite, default port 5173) to call the API
    # from the browser. Wide open for local development; tighten
    # `origins` before deploying anywhere public.
    CORS(app, resources={r"/*": {"origins": "*"}})

    from app.routes import inventory_bp
    app.register_blueprint(inventory_bp)

    return app

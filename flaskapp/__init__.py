# your_app/__init__.py
from flask import Flask
from .config import Config
from flask_cors import CORS


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(config_class)

    app.config["CORS_HEADERS"] = "Content-Type"
    # Initialize extensions (e.g., SQLAlchemy, Marshmallow, etc.)

    # Register blueprints
    from .paths.tables import tab_bp
    from .paths.deps import dep_bp

    app.register_blueprint(dep_bp, url_prefix="/api/deps")
    app.register_blueprint(tab_bp, url_prefix="/api/tables")

    return app

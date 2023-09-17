# your_app/__init__.py
from flask import Flask
from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions (e.g., SQLAlchemy, Marshmallow, etc.)

    # Register blueprints
    from .paths.tables import tab_bp
    from .paths.deps import dep_bp

    app.register_blueprint(tab_bp, url_prefix="/api/tables")
    app.register_blueprint(dep_bp, url_prefix="/api/deps")

    return app

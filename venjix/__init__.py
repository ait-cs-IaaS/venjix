from flask import Flask


def main():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    from . import venjix

    venjix.bootstrap()
    app.register_blueprint(venjix.bp)

    return app

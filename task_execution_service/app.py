# app.py
import logging
from flask import Flask
from extensions import db, migrate
from config import Config
from prometheus_flask_exporter import PrometheusMetrics
from routes import manual_exec_bp, execution_bp
import models  # Ensure models are imported

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    app.register_blueprint(manual_exec_bp, url_prefix='/execute')
    app.register_blueprint(execution_bp)

    # Logging configuration
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Task Execution Service started.')

    # Prometheus metrics
    metrics = PrometheusMetrics(app)
    metrics.info('app_info', 'Task Execution Service Info', version='1.0.0')

    return app

if __name__ == '__main__':
    # Only run the built-in server if this file is executed directly
    app = create_app()
    app.run(host='0.0.0.0', port=5001)

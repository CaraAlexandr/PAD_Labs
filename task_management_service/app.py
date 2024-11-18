import logging

from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

from config import Config
from extensions import db, migrate
from routes import task_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    app.register_blueprint(task_bp, url_prefix='/tasks')

    # Setup Logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Task Management Service started.')

    # Initialize Prometheus Metrics
    metrics = PrometheusMetrics(app)
    # Optional: Customize metrics
    metrics.info('app_info', 'Task Management Service Info', version='1.0.0')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)

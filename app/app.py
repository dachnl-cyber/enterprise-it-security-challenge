from flask import Flask
from .db import init_db
from .routes import register_routes
from .seed import seed_data

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="dev-secret-key-hardcoded",
        DATABASE="data/app.db",
        UPLOAD_FOLDER="uploads",
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,
        TESTING=False,
        INTERNAL_IMPORT_ENABLED=True,
        DEFAULT_IMPORT_TIMEOUT=2,
        ALLOWED_IMPORT_SCHEMES=["http", "https"],
        SUPPORT_EMAIL="it-support@example.internal",
    )

    init_db(app)

    with app.app_context():
        seed_data()

    register_routes(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

import os
from flask import Flask, session
from config import config
from models import db


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.db_path = app.config["DATABASE"]

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(app.config["DATABASE"]):
        db.initialize()
        print("Database initialized!")

    from routes import main, admin, auth, upload, predict, api

    @app.route("/")
    def index():
        from flask import redirect, url_for

        if "user_id" in session:
            return redirect(url_for("main.dashboard"))
        return redirect(url_for("auth.login"))

    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(upload)
    app.register_blueprint(predict)
    app.register_blueprint(api)

    @app.context_processor
    def inject_user():
        return {
            "logged_in": "user_id" in session,
            "username": session.get("username"),
            "is_admin": session.get("role") == "admin",
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

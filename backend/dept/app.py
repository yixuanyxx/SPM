import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","), supports_credentials=True)

    # Register routes
    from controllers.dept_controller import dept_bp
    app.register_blueprint(dept_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    port = "5005"  # pick a unique port for this microservice
    app.run(host="0.0.0.0", port=port, debug=True)
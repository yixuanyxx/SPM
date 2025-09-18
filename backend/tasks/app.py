import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","), supports_credentials=True)

    # Register routes
    from controllers.task_controller import task_bp
    app.register_blueprint(task_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "5002"))  # pick a unique port for this microservice
    app.run(host="0.0.0.0", port=port, debug=True)

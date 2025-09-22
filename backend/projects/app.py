import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","), supports_credentials=True)

    # Register routes
    from controllers.project_controller import project_bp
    app.register_blueprint(project_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    port = "5001"
    print(f"Projects microservice running on port {port}")
    app.run(host="0.0.0.0", port=int(port), debug=True)

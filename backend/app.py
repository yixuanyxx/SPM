# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from dotenv import load_dotenv

# load_dotenv()
# app = Flask(__name__)
# CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","), supports_credentials=True)

# # Supabase client (server-side)
# from supabase import create_client, Client
# SUPABASE_URL = os.environ["SUPABASE_URL"]
# SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# @app.get("/health")
# def health():
#     return jsonify({"ok": True})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")))

from flask import Flask
from flask_cors import CORS
from config import Config

# Import blueprints
from routes.health import health_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # Register routes
    app.register_blueprint(health_bp, url_prefix="/")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=app.config["PORT"])

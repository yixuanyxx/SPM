import os
import random
from flask import Blueprint, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
auth_bp = Blueprint("auth", __name__)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# -----------------------------
# 1. Register (Create account)
# -----------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    required_fields = {"email", "password", "re_password", "name", "role"}
    data = request.form if request.form else request.json

    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing fields {required_fields}", "Code": 400}), 400

    email = data["email"].strip().lower()
    password = data["password"]
    re_password = data["re_password"]
    name = data["name"]
    role = data["role"]

    if "@" not in email:
        return jsonify({"error": "Invalid email format", "Code": 400}), 400
    if password != re_password:
        return jsonify({"error": "Passwords do not match", "Code": 400}), 400

    # check existing
    existing = supabase.table("users").select("*").eq("email", email).execute()
    if existing.data:
        return jsonify({"error": "Email already registered", "Code": 200}), 200

    # generate OTP (simulate)
    otp = str(random.randint(100000, 999999))

    user_data = {
        "email": email,
        "password": password,   # TODO: hash in prod
        "name": name,
        "role": role,
        "is_verified": False,
        "otp_code": otp
    }

    res = supabase.table("users").insert(user_data).execute()
    if res.error:
        return jsonify({"error": str(res.error), "Code": 500}), 500

    # Simulate sending OTP → return in response for demo
    return jsonify({
        "Message": "User created. Please verify OTP.",
        "otp_demo": otp,
        "Code": 201
    }), 201


# -----------------------------
# 2. Verify OTP
# -----------------------------
@auth_bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.form if request.form else request.json
    email = data.get("email", "").lower()
    otp = data.get("otp")

    user_res = supabase.table("users").select("*").eq("email", email).execute()
    if not user_res.data:
        return jsonify({"error": "User not found", "Code": 404}), 404
    user = user_res.data[0]

    if user.get("is_verified"):
        return jsonify({"Message": "Already verified", "Code": 200}), 200

    if str(user.get("otp_code")) != str(otp):
        return jsonify({"error": "Invalid OTP", "Code": 400}), 400

    update_res = supabase.table("users").update({"is_verified": True, "otp_code": None}).eq("email", email).execute()
    if update_res.error:
        return jsonify({"error": str(update_res.error), "Code": 500}), 500

    return jsonify({"Message": "Account verified!", "Code": 200}), 200


# -----------------------------
# 3. Login
# -----------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form if request.form else request.json
    email = data.get("email", "").lower()
    password = data.get("password")

    user_res = supabase.table("users").select("*").eq("email", email).execute()
    if not user_res.data:
        return jsonify({"error": "Invalid email or password", "Code": 401}), 401
    user = user_res.data[0]

    if not user.get("is_verified"):
        return jsonify({"error": "Email not verified", "Code": 403}), 403

    if user["password"] != password:
        return jsonify({"error": "Invalid email or password", "Code": 401}), 401

    return jsonify({
        "Message": "Login successful",
        "user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]},
        "Code": 200
    }), 200


# -----------------------------
# 4. Update Account
# -----------------------------
@auth_bp.route("/update_account", methods=["POST"])
def update_account():
    data = request.form if request.form else request.json
    email = data.get("email", "").lower()

    user_res = supabase.table("users").select("*").eq("email", email).execute()
    if not user_res.data:
        return jsonify({"error": "User not found", "Code": 404}), 404
    user = user_res.data[0]

    updates = {}
    if "name" in data and data["name"]:
        updates["name"] = data["name"]
    if "new_password" in data and data["new_password"]:
        if data["new_password"] != data.get("confirm_password"):
            return jsonify({"error": "Passwords do not match", "Code": 400}), 400
        updates["password"] = data["new_password"]

    if not updates:
        return jsonify({"error": "No updates provided", "Code": 400}), 400

    update_res = supabase.table("users").update(updates).eq("email", email).execute()
    if update_res.error:
        return jsonify({"error": str(update_res.error), "Code": 500}), 500

    return jsonify({"Message": "Account updated", "Code": 200}), 200

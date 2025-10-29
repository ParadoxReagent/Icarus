"""
Vulnerable API Application for Project Icarus - Scenario 3
Contains intentional vulnerabilities for educational purposes
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import pymongo
import bcrypt
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# VULNERABILITY: Hardcoded JWT secret (should be in env var)
JWT_SECRET = "super_secret_key_123"
JWT_ALGORITHM = "HS256"

# MongoDB connection
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["vulnerable_api"]
users_collection = db["users"]
posts_collection = db["posts"]


@app.route("/")
def home():
    return jsonify({
        "message": "Vulnerable API v1.0",
        "endpoints": [
            "/api/register",
            "/api/login",
            "/api/users/<id>",
            "/api/posts",
            "/api/posts/<id>",
            "/api/admin/flag"
        ]
    })


@app.route("/api/register", methods=["POST"])
def register():
    """User registration endpoint"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # Check if user exists
    if users_collection.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Create user
    user = {
        "username": username,
        "password": hashed,
        "role": "user",
        "created_at": datetime.now()
    }
    result = users_collection.insert_one(user)

    return jsonify({
        "message": "User created successfully",
        "user_id": str(result.inserted_id)
    }), 201


@app.route("/api/login", methods=["POST"])
def login():
    """Login endpoint with JWT token generation"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    # VULNERABILITY: NoSQL injection possible
    # Should sanitize input, but instead we pass it directly
    query = {"username": username}
    if isinstance(data.get("username"), dict):
        # Allow dict queries (NoSQL injection)
        query = data.get("username")

    user = users_collection.find_one(query)

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Verify password
    if not bcrypt.checkpw(password.encode(), user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # Generate JWT token
    token = jwt.encode({
        "user_id": str(user["_id"]),
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "username": user["username"],
            "role": user["role"]
        }
    })


@app.route("/api/users/<user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get user details
    VULNERABILITY: IDOR - No authorization check
    """
    # Should verify JWT and check if user has permission
    # But we skip authorization entirely (IDOR vulnerability)

    user = users_collection.find_one({"_id": pymongo.ObjectId(user_id)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user["role"],
        "created_at": str(user["created_at"])
    })


@app.route("/api/posts", methods=["GET", "POST"])
def posts():
    """Posts endpoint"""
    if request.method == "GET":
        # VULNERABILITY: No pagination, can DoS with large responses
        all_posts = list(posts_collection.find())
        for post in all_posts:
            post["_id"] = str(post["_id"])
        return jsonify(all_posts)

    elif request.method == "POST":
        # VULNERABILITY: No authentication required to create posts
        data = request.get_json()
        post = {
            "title": data.get("title"),
            "content": data.get("content"),
            "author_id": data.get("author_id"),
            "created_at": datetime.now()
        }
        result = posts_collection.insert_one(post)
        return jsonify({
            "message": "Post created",
            "post_id": str(result.inserted_id)
        }), 201


@app.route("/api/posts/<post_id>", methods=["GET", "DELETE"])
def post_detail(post_id):
    """Get or delete a specific post"""
    if request.method == "GET":
        post = posts_collection.find_one({"_id": pymongo.ObjectId(post_id)})
        if not post:
            return jsonify({"error": "Post not found"}), 404
        post["_id"] = str(post["_id"])
        return jsonify(post)

    elif request.method == "DELETE":
        # VULNERABILITY: No authorization check - anyone can delete
        result = posts_collection.delete_one({"_id": pymongo.ObjectId(post_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Post not found"}), 404
        return jsonify({"message": "Post deleted"})


@app.route("/api/admin/flag", methods=["GET"])
def admin_flag():
    """
    Admin endpoint to get flag
    VULNERABILITY: Weak JWT verification
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "No authorization token"}), 401

    try:
        token = auth_header.split(" ")[1]
        # VULNERABILITY: JWT secret is exposed in .git or error messages
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # VULNERABILITY: Only checks role in JWT, can be manipulated
        if payload.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403

        # Read flag file
        with open("/app/data/admin_flag.json", "r") as f:
            flag_data = json.load(f)

        return jsonify(flag_data)

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        # VULNERABILITY: Exposes internal error details
        return jsonify({"error": str(e)}), 500


@app.route("/api/debug/secret", methods=["GET"])
def debug_secret():
    """
    VULNERABILITY: Debug endpoint exposing JWT secret
    Should never be in production
    """
    return jsonify({
        "jwt_secret": JWT_SECRET,
        "jwt_algorithm": JWT_ALGORITHM,
        "warning": "This endpoint should not exist in production!"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

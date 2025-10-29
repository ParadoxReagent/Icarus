"""
Initialize database with test data for API target
"""

import pymongo
import bcrypt
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["vulnerable_api"]

# Clear existing data
db.users.delete_many({})
db.posts.delete_many({})

# Create admin user
admin_password = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
admin_user = {
    "username": "admin",
    "password": admin_password,
    "role": "admin",
    "created_at": datetime.now()
}
admin_id = db.users.insert_one(admin_user).inserted_id

# Create regular users
user1_password = bcrypt.hashpw(b"password123", bcrypt.gensalt())
user1 = {
    "username": "john",
    "password": user1_password,
    "role": "user",
    "created_at": datetime.now()
}
user1_id = db.users.insert_one(user1).inserted_id

user2_password = bcrypt.hashpw(b"qwerty", bcrypt.gensalt())
user2 = {
    "username": "alice",
    "password": user2_password,
    "role": "user",
    "created_at": datetime.now()
}
user2_id = db.users.insert_one(user2).inserted_id

# Create some posts
posts = [
    {
        "title": "Welcome to the API",
        "content": "This is a test post",
        "author_id": str(admin_id),
        "created_at": datetime.now()
    },
    {
        "title": "API Documentation",
        "content": "Check /api/docs for more information",
        "author_id": str(user1_id),
        "created_at": datetime.now()
    },
    {
        "title": "Security Notice",
        "content": "Please report any security issues to admin",
        "author_id": str(admin_id),
        "created_at": datetime.now()
    }
]

db.posts.insert_many(posts)

print("Database initialized successfully!")
print(f"Admin user: admin / admin123")
print(f"Regular user 1: john / password123")
print(f"Regular user 2: alice / qwerty")

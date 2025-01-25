from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Muat environment variable
load_dotenv()

app = Flask(__name__)
CORS(app)

# Koneksi MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.user_database
users_collection = db.users

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')

    if not username or not email:
        return jsonify({"error": "Username dan email diperlukan"}), 400

    # Cek duplikasi
    existing_user = users_collection.find_one({
        "$or": [{"username": username}, {"email": email}]
    })

    if existing_user:
        return jsonify({"error": "Username atau email sudah terdaftar"}), 409

    # Tambah user
    user_data = {
        "username": username,
        "email": email
    }
    result = users_collection.insert_one(user_data)
    
    return jsonify({
        "message": "User berhasil dibuat",
        "user_id": str(result.inserted_id)
    }), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = list(users_collection.find())
    
    # Konversi ObjectId ke string
    for user in users:
        user['_id'] = str(user['_id'])
    
    return jsonify(users)

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if user:
            user['_id'] = str(user['_id'])
            return jsonify(user)
        
        return jsonify({"error": "User tidak ditemukan"}), 404
    
    except:
        return jsonify({"error": "ID tidak valid"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
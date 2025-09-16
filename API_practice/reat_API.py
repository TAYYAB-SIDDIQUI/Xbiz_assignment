from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory database (just a list for simplicity)
users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

# READ: Get all users
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

# READ: Get a single user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"message": "User not found"}), 404

# CREATE: Add a new user
@app.route('/users', methods=['POST'])
def create_user():
    new_user = request.get_json()
    new_user["id"] = users[-1]["id"] + 1 if users else 1
    users.append(new_user)
    return jsonify(new_user), 201

# UPDATE: Update an existing user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if user:
        data = request.get_json()
        user.update(data)
        return jsonify(user)
    return jsonify({"message": "User not found"}), 404

# DELETE: Remove a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": "User deleted"}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

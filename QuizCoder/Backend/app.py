from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from models import (
    create_user,
    verify_user,
    update_user_score,
    get_all_users,
    record_notes_round
)

from utils import (
    fetch_online_questions,
    generate_notes_quiz
)

# Folder to save uploaded notes
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Flask setup
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=[
    "http://localhost:8000",
    "http://127.0.0.1:8000"
])

# ------------------------------
#  USER REGISTRATION
# ------------------------------
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify(success=False, message="Missing credentials"), 400

        result = create_user(username, password)
        return jsonify(success=result["success"], message=result["message"])
    except Exception as e:
        app.logger.error(f"Error in /register: {e}", exc_info=True)
        return jsonify(success=False, message="Server error occurred"), 500

# ------------------------------
#  USER LOGIN
# ------------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if verify_user(username, password):
        return jsonify(success=True, username=username)
    return jsonify(success=False, message="Invalid credentials"), 401

# ------------------------------
#  START QUIZ - fetch questions
# ------------------------------
@app.route('/quiz', methods=['GET'])
def quiz():
    try:
        questions = fetch_online_questions(10)
        return jsonify(questions=questions)
    except Exception as e:
        app.logger.error(f"Error fetching quiz questions: {e}", exc_info=True)
        return jsonify(success=False, message="Failed to load quiz"), 500

# ------------------------------
#  SUBMIT QUIZ SCORE
# ------------------------------
@app.route('/submit', methods=['POST'])
def submit_score():
    try:
        data = request.get_json()
        username = data["username"]
        score = data["score"]
        update_user_score(username, score)
        return jsonify(success=True)
    except Exception as e:
        app.logger.error(f"Error in /submit: {e}", exc_info=True)
        return jsonify(success=False, message="Failed to submit score"), 500

# ------------------------------
#  UPLOAD NOTES FILE
# ------------------------------
@app.route('/upload_notes', methods=['POST'])
def upload_notes():
    try:
        if 'file' not in request.files:
            return jsonify(error="No file provided"), 400
        file = request.files['file']
        if file.filename == "":
            return jsonify(error="Empty file name"), 400

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        # Generate notes quiz
        rounds = generate_notes_quiz(path)
        return jsonify(rounds=rounds)
    except Exception as e:
        app.logger.error(f"Error in /upload_notes: {e}", exc_info=True)
        return jsonify(success=False, message="Failed to process notes"), 500

# ------------------------------
#  SUBMIT NOTES QUIZ SCORES
# ------------------------------
@app.route('/submit_notes', methods=['POST'])
def submit_notes_scores():
    try:
        data = request.get_json()
        username = data.get("username")
        scores = data.get("round_scores")  # list of integers
        record_notes_round(username, scores)
        update_user_score(username, max(scores))  # highest round score becomes main score
        return jsonify(success=True)
    except Exception as e:
        app.logger.error(f"Error in /submit_notes: {e}", exc_info=True)
        return jsonify(success=False, message="Failed to submit notes scores"), 500

# ------------------------------
#  LEADERBOARD
# ------------------------------
@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        users = get_all_users()
        sorted_users = sorted(users, key=lambda x: x["score"], reverse=True)
        return jsonify(users=sorted_users)
    except Exception as e:
        app.logger.error(f"Error in /leaderboard: {e}", exc_info=True)
        return jsonify(success=False, message="Failed to load leaderboard"), 500


if __name__ == '__main__':
    print("🚀 Flask backend running at http://127.0.0.1:5000")
    app.run(debug=True)
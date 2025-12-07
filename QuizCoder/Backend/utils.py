import random
import json
import requests

# ------------------------------
#  Fetch Online Quiz Questions
# ------------------------------
def fetch_online_questions(count=10):
    """
    Fetches 'count' quiz questions from Open Trivia DB API.
    Ensures exactly 4 options per question and clean text.
    Falls back to local sample questions if API fails.
    """
    try:
        url = f"https://opentdb.com/api.php?amount={count}&type=multiple"
        res = requests.get(url, timeout=5)
        data = res.json()

        if data["response_code"] != 0:
            raise Exception("API returned no results")

        questions = []
        for q in data["results"]:
            options = q["incorrect_answers"] + [q["correct_answer"]]
            random.shuffle(options)
            questions.append({
                "question": clean_text(q["question"]),
                "options": [clean_text(opt) for opt in options],
                "answer": clean_text(q["correct_answer"])
            })

        return questions

    except Exception as e:
        print(f"⚠️ Error fetching online questions: {e}")
        return sample_questions(count)


# ------------------------------
#  Generate Notes Quiz
# ------------------------------
def generate_notes_quiz(file_path):
    """
    Generates 3 rounds of quiz questions from uploaded notes file.
    Each round has 5 questions with 4 options each.
    Falls back to sample questions if parsing fails.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split notes into sentences for question generation
        sentences = [s.strip() for s in content.replace("\n", " ").split(".") if s.strip()]

        if len(sentences) < 5:
            raise Exception("Not enough content to create quiz")

        rounds = []
        for _ in range(3):  # 3 rounds
            round_qs = []
            for _ in range(5):  # 5 questions per round
                sentence = random.choice(sentences)
                answer = sentence.split(" ")[0] if " " in sentence else sentence
                wrong_options = random.sample(sentences, min(3, len(sentences)))
                options = [answer] + wrong_options
                options = list(set(options))  # remove duplicates
                while len(options) < 4:
                    options.append(f"Option {len(options)+1}")
                options = options[:4]
                random.shuffle(options)

                round_qs.append({
                    "question": f"What is the first word of: '{sentence[:50]}...'",
                    "options": options,
                    "answer": answer
                })
            rounds.append(round_qs)

        return rounds

    except Exception as e:
        print(f"⚠️ Error generating notes quiz: {e}")
        # fallback to sample data
        return [sample_questions(5) for _ in range(3)]


# ------------------------------
#  Helpers
# ------------------------------
def clean_text(text):
    """Remove unwanted HTML entities and formatting from question text."""
    replacements = {
        "&quot;": '"',
        "&#039;": "'",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()


def sample_questions(count):
    """Fallback sample questions if API/notes fail."""
    samples = [
        {
            "question": "What is the capital of France?",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "answer": "Paris"
        },
        {
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "answer": "4"
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Mars", "Earth", "Jupiter", "Venus"],
            "answer": "Mars"
        },
        {
            "question": "Who wrote 'Hamlet'?",
            "options": ["Shakespeare", "Tolstoy", "Hemingway", "Orwell"],
            "answer": "Shakespeare"
        }
    ]
    return random.sample(samples, min(count, len(samples)))

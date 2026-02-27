from flask import Flask, request, jsonify, render_template
import requests
import re

app = Flask(__name__)

HUGGINGFACE_API_KEY = "AIzaSyA1Nk9qkqRIZbYuqgmFovJfIJgKDpwL_1c"

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

# -----------------------------
# ANALYSE IA
# -----------------------------
def analyze_with_ai(text):
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": ["information fiable", "information douteuse", "fake news"]
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    if "scores" in result:
        labels = result["labels"]
        scores = result["scores"]
        return dict(zip(labels, scores))

    return {}

# -----------------------------
# ANALYSE MULTI-CRITÈRES
# -----------------------------
def analyze_text(text):

    indicators = []

    # 1️⃣ Analyse émotionnelle
    emotional_words = ["scandale", "choquant", "incroyable", "urgent", "révélation"]
    emotion_score = sum(word in text.lower() for word in emotional_words)

    if emotion_score > 0:
        indicators.append("Langage émotionnel détecté")

    # 2️⃣ Source officielle
    if ".gov" in text or ".org" in text:
        source_score = 1
        indicators.append("Source officielle détectée")
    else:
        source_score = 0

    # 3️⃣ Longueur
    if len(text.split()) < 10:
        indicators.append("Texte très court, manque de contexte")

    # 4️⃣ IA
    ai_result = analyze_with_ai(text)

    ai_fake = ai_result.get("fake news", 0)
    ai_reliable = ai_result.get("information fiable", 0)

    # -----------------------------
    # SCORE FINAL (pondéré)
    # -----------------------------
    score = 50
    score += int(ai_reliable * 40)
    score -= int(ai_fake * 40)
    score -= emotion_score * 5
    score += source_score * 10

    score = max(0, min(100, score))

    # Couleur
    if score > 70:
        label = "🟢 Fiable"
    elif score > 40:
        label = "🟡 Douteux"
    else:
        label = "🔴 Risque élevé"

    explanation = f"""
    Score basé sur :
    - Analyse IA
    - Détection émotionnelle
    - Vérification source
    - Longueur du contenu
    """

    return {
        "score": score,
        "label": label,
        "indicators": indicators,
        "confidence": round(ai_reliable * 100, 2),
        "explanation": explanation
    }

# -----------------------------
# ROUTES
# -----------------------------
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data["text"]

    result = analyze_text(text)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

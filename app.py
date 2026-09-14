from flask import Flask, render_template, request, jsonify
from google import genai
import os
app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(
    api_key=GEMINI_API_KEY
)
# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# ASK GEMINI
# ==========================================

@app.route("/ask", methods=["POST"])
def ask():

    try:

        data = request.get_json()

        question = data.get("question", "").strip()
        language = data.get("language", "en")

        if not question:
            return jsonify({
                "success": False,
                "error": "No question received."
            }), 400


        language_names = {
            "en": "English",
            "el": "Greek",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "es": "Spanish",
            "pt": "Portuguese",
            "nl": "Dutch",
            "sv": "Swedish",
            "da": "Danish",
            "no": "Norwegian",
            "fi": "Finnish",
            "pl": "Polish",
            "cs": "Czech",
            "sk": "Slovak",
            "hu": "Hungarian",
            "ro": "Romanian",
            "bg": "Bulgarian",
            "hr": "Croatian",
            "sl": "Slovenian",
            "sr": "Serbian",
            "uk": "Ukrainian",
            "tr": "Turkish",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "hi": "Hindi",
            "ar": "Arabic",
            "bn": "Bengali",
            "id": "Indonesian",
            "vi": "Vietnamese",
            "th": "Thai",
            "he": "Hebrew"
        }

        selected_language = language_names.get(
            language,
            "English"
        )


        # ==========================================
        # PROMPT
        # ==========================================

        prompt = prompt = f"""
You are the Acropolis Assistant.

You are an intelligent visitor assistant specifically
for the Acropolis of Athens in Greece.

The visitor asked:

{question}

Answer in {selected_language}.

Rules:

Answer the visitor directly and naturally.

Your answer must be no more than 50 words.

Use only normal sentences and paragraphs.

Do not use bullet points.

Do not use numbered lists.

Do not use asterisks.

Do not use dashes.

Do not use emojis.

Do not use quotation marks unless absolutely necessary.

Do not use any special symbols.

The only punctuation marks you may use are:
period and question mark.

Keep the answer short, clear and useful for a tourist.

Do not repeat or rephrase the visitor's question.


Do not add introductions or conclusions that are not useful.

Focus on the Acropolis of Athens and its monuments.

Do not invent historical facts.

If you are uncertain about a historical fact, say so briefly.

Do not mention that you are an AI unless the visitor specifically asks.

When the visitor asks a general question about the Acropolis
  without mentioning a specific monument, assume they are referring
  to the Parthenon.
  
  If there is something in a question that doesn't fit with the rest or is off-topic, then simply skip it.
"""


        # ==========================================
        # GEMINI REQUEST
        # ==========================================

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        answer = response.text


        return jsonify({
            "success": True,
            "answer": answer
        })


    except Exception as error:

        print("Gemini error:", error)

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
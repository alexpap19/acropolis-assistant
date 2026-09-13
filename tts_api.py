from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import sherpa_onnx
import os
import wave
import tempfile


app = Flask(__name__)

CORS(app)

# =========================================================
# PATHS
# =========================================================

MODEL_DIR = r"C:\Users\alex\Downloads\sherpa-onnx-supertonic-3-tts-int8-2026-05-11\sherpa-onnx-supertonic-3-tts-int8-2026-05-11\sherpa-onnx-supertonic-3-tts-int8-2026-05-11"


# =========================================================
# SUPER TTS CONFIG
# =========================================================

tts_model = sherpa_onnx.OfflineTtsSupertonicModelConfig(

    duration_predictor=os.path.join(
        MODEL_DIR,
        "duration_predictor.int8.onnx"
    ),

    text_encoder=os.path.join(
        MODEL_DIR,
        "text_encoder.int8.onnx"
    ),

    vector_estimator=os.path.join(
        MODEL_DIR,
        "vector_estimator.int8.onnx"
    ),

    vocoder=os.path.join(
        MODEL_DIR,
        "vocoder.int8.onnx"
    ),

    tts_json=os.path.join(
        MODEL_DIR,
        "tts.json"
    ),

    unicode_indexer=os.path.join(
        MODEL_DIR,
        "unicode_indexer.bin"
    ),

    voice_style=os.path.join(
        MODEL_DIR,
        "voice.bin"
    )
)


tts_model_config = sherpa_onnx.OfflineTtsModelConfig(
    supertonic=tts_model
)


tts_config = sherpa_onnx.OfflineTtsConfig(
    model=tts_model_config
)


tts = sherpa_onnx.OfflineTts(tts_config)


print("SUPER TTS READY!")


# =========================================================
# SUPPORTED LANGUAGES
# =========================================================

SUPPORTED_LANGUAGES = {

    "en": "en",
    "el": "el",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "es": "es",
    "pt": "pt",
    "nl": "nl",
    "sv": "sv",
    "da": "da",
    "fi": "fi",
    "pl": "pl",
    "cs": "cs",
    "sk": "sk",
    "hu": "hu",
    "ro": "ro",
    "bg": "bg",
    "hr": "hr",
    "sl": "sl",
    "uk": "uk",
    "tr": "tr",
    "zh": "zh",
    "ja": "ja",
    "ko": "ko",
    "hi": "hi",
    "ar": "ar",
    "id": "id",
    "vi": "vi"
}


# =========================================================
# TTS API
# =========================================================

@app.route("/tts", methods=["POST"])
def text_to_speech():

    try:

        data = request.get_json()

        text = data.get(
            "text",
            ""
        ).strip()

        language = data.get(
            "language",
            "en"
        ).lower()


        # =================================================
        # CHECK TEXT
        # =================================================

        if not text:

            return jsonify({
                "success": False,
                "error": "No text received."
            }), 400


        # =================================================
        # CHECK LANGUAGE
        # =================================================

        if language not in SUPPORTED_LANGUAGES:

            language = "en"


        tts_language = \
            SUPPORTED_LANGUAGES[language]


        print(
            "TTS LANGUAGE:",
            tts_language
        )

        print(
            "TTS TEXT:"
        )

        print(text)


        # =================================================
        # GENERATION CONFIG
        # =================================================

        gen_config = \
            sherpa_onnx.GenerationConfig()


        gen_config.sid = 0


        gen_config.num_steps = 8


        gen_config.speed = 1.0


        gen_config.extra["lang"] = \
            tts_language


        # =================================================
        # GENERATE AUDIO
        # =================================================

        audio = tts.generate(
            text,
            gen_config
        )


        # =================================================
        # TEMP WAV FILE
        # =================================================

        output_file = \
            tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            )

        output_file.close()


        # =================================================
        # SAVE WAV
        # =================================================

        samples = audio.samples


        with wave.open(
            output_file.name,
            "wb"
        ) as wav_file:

            wav_file.setnchannels(
                1
            )

            wav_file.setsampwidth(
                2
            )

            wav_file.setframerate(
                audio.sample_rate
            )


            pcm_data = bytearray()


            for sample in samples:

                sample = max(
                    -1.0,
                    min(
                        1.0,
                        sample
                    )
                )


                value = int(
                    sample * 32767
                )


                pcm_data.extend(
                    value.to_bytes(
                        2,
                        byteorder="little",
                        signed=True
                    )
                )


            wav_file.writeframes(
                pcm_data
            )


        print(
            "Audio generated:",
            output_file.name
        )


        # =================================================
        # RETURN AUDIO
        # =================================================

        return send_file(
            output_file.name,
            mimetype="audio/wav",
            as_attachment=False
        )


    except Exception as error:

        print(
            "TTS ERROR:",
            error
        )


        return jsonify({

            "success": False,

            "error": str(error)

        }), 500


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5001,

        debug=True

    )
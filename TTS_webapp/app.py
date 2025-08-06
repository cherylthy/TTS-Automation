from flask import Flask, render_template, request
import os
from script_automation import generate_audio  # Assume function-based version
from pathlib import Path

app = Flask(__name__)
SCRIPT_PATHS = {
    "qc": {
        "en": "TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_en.txt",
        "zh-cn": "TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_man.txt",
        "zh-hk": "TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_can.txt"
    },
    "epp": {
        "en": "TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_en.txt",
        "zh-cn": "TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_man.txt",
        "zh-hk": "TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_can.txt"
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    script_text = ""
    audio_file = None
    show_textbox = False

    # Default values
    loan_type = "qc"
    language = "en"

    if request.method == "POST":
        loan_type = request.form.get("loan_type", "qc")
        language = request.form.get("language", "en")
        action = request.form["action"]
        script_path = SCRIPT_PATHS[loan_type][language]

        if action == "confirm":
            show_textbox = True
            if os.path.exists(script_path):
                with open(script_path, "r", encoding="utf-8") as f:
                    script_text = f.read()

        elif action == "save":
            show_textbox = True
            script_text = request.form["script"].strip()

            try:
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(script_text)
                print(f"[INFO] Script saved to {script_path}")
            except Exception as e:
                print(f"[ERROR] Failed to write script: {e}")

            audio_file = generate_audio(loan_type, language, script_text)
            print(f"[INFO] Generated audio file: {audio_file}")


    return render_template("index.html", script_text=script_text, audio_file=audio_file, selected_loan=loan_type, selected_language=language, show_textbox=show_textbox)
if __name__ == "__main__":
    app.run(debug=True)

import requests
import textwrap
from pydub import AudioSegment
import os
import html
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Azure TTS credentials
subscription_key = "a63eb7d3d1be4ae8bec8509fbb14ddc0"
region = "eastus"

# Language and file_name-to-file and voice mapping
language_config = {
    "en": {
        "qc": {
            "file": "TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_en.txt",
            "voice": "en-US-AriaNeural",
            "lang": "en-US"
        },
        "epp": {
            "file": "TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_en.txt",
            "voice": "en-US-AriaNeural",
            "lang": "en-US"
        }
    },
    "zh-cn": {
        "qc": {
            "file": "TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_man.txt",
            "voice": "zh-CN-XiaoqiuNeural",
            "lang": "zh-CN"
        },
        "epp": {
            "file": "TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_man.txt",
            "voice": "zh-CN-XiaoqiuNeural",
            "lang": "zh-CN"
        }
    },
    "zh-hk": {
        "qc": {
            "file": "TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_can.txt",
            "voice": "zh-HK-HiuGaaiNeural",
            "lang": "zh-HK"
        },
        "epp": {
            "file": "TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_can.txt",
            "voice": "zh-HK-HiuGaaiNeural",
            "lang": "zh-HK"
        }
    }
}

def generate_audio(file_name, language_choice, custom_text=None):
    if language_choice not in language_config or file_name not in language_config[language_choice]:
        raise ValueError("Invalid language or file_name selection.")

    config = language_config[language_choice][file_name]

    # Read from script file if custom_text is not provided
    if custom_text is None:
        with open(config["file"], "r", encoding="utf-8") as f:
            full_text = f.read()
    else:
        full_text = custom_text.strip()

    if not full_text:
        raise ValueError("Script text is empty.")

    # Wrap into chunks
    chunks = textwrap.wrap(full_text, 1000, break_long_words=False, replace_whitespace=False)

    # Retry-enabled HTTP session
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[502, 503, 504], allowed_methods=["POST"])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)

    url = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": subscription_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
        "User-Agent": "MyTTSApp"
    }

    # Output path
    lang_suffix = {
        "en": "en",
        "zh-cn": "man",
        "zh-hk": "can"
    }
    output_folder = os.path.join("static/audio", f"{file_name}_{lang_suffix[language_choice]}")
    os.makedirs(output_folder, exist_ok=True)

    # Generate each audio chunk
    for i, chunk in enumerate(chunks):
        escaped_chunk = html.escape(chunk)
        ssml = f"""
        <speak version='1.0' xml:lang='{config["lang"]}'>
        <voice xml:lang='{config["lang"]}' name='{config["voice"]}'>
            {escaped_chunk}
        </voice>
        </speak>
        """

        output_filename = os.path.join(output_folder, f"output_part_{i+1}.mp3")
        for attempt in range(3):
            try:
                response = session.post(url, headers=headers, data=ssml.encode("utf-8"))
                if response.status_code == 200:
                    with open(output_filename, "wb") as f:
                        f.write(response.content)
                    print(f"[INFO] 🔊 Chunk {i+1} saved: {output_filename}")
                    break
                else:
                    print(f"[ERROR] ❌ Status {response.status_code} on chunk {i+1}: {response.text}")
            except Exception as e:
                print(f"[ERROR] 🔁 Attempt {attempt+1} failed on chunk {i+1}: {e}")

    # Combine all audio parts
    combined = AudioSegment.empty()
    for i in range(len(chunks)):
        part_file = os.path.join(output_folder, f"output_part_{i+1}.mp3")
        if os.path.exists(part_file):
            combined += AudioSegment.from_mp3(part_file)
        else:
            print(f"[WARNING] ⚠️ Missing chunk file: {part_file}")

    # Save final audio
    final_audio_name = f"final_output_{file_name}_{language_choice}.mp3"
    final_audio_path = os.path.join("static/audio", final_audio_name)
    try:
        combined.export(final_audio_path, format="mp3")
        print(f"[SUCCESS] ✅ Final audio saved: {final_audio_path}")
    except Exception as e:
        print(f"[ERROR] ❌ Failed to export final audio: {e}")

    return final_audio_name


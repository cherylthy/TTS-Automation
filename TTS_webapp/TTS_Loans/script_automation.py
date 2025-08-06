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

# Choose file name: "qc" or "epp"
file_name = "MU_FS"

# 🔀 Choose language: "en", "zh-cn", or "zh-hk"
language_choice = "zh-hk"

# 🗂 Language and file_name-to-file and voice mapping
language_config = {
    "en": {
        "qc": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_en.txt",
            "voice": "en-US-AriaNeural",
            "lang": "en-US"
        },
        "epp": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_en.txt",
            "voice": "en-US-AriaNeural",
            "lang": "en-US"
        },
        "MU_Plus":{ 
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/SOW7/MU_Plus_20250515_approved_ENG.txt",
            "voice": "en-US-AriaNeural",
            "lang": "en-US"
        },
        "MU_FS": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/SOW7/MU_FS_en.txt",
            "voice": "en-US-AriaNeural",
            "lang": "en-US"
        },
        "MU_HY": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/SOW7/MU_HY_en.txt",
            "voice": "en-US-AriaNeural",
            "lang": "en-US"
        }
    },
    "zh-cn": {
        "qc": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_man.txt",
            "voice": "zh-CN-XiaoqiuNeural",
            "lang": "zh-CN"
        },
        "epp": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_man.txt",
            "voice": "zh-CN-XiaoqiuNeural",
            "lang": "zh-CN"
        },
          "MU_Plus": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/SOW7/MU_Plus_20250515_approved_MAN.txt",
            "voice": "zh-CN-XiaoqiuNeural",
            "lang": "zh-CN"
        },
        "MU_FS": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/SOW7/MU_FS_man.txt",
            "voice": "zh-CN-XiaoqiuNeural",
            "lang": "zh-CN"
        },
        "MU_HY": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/SOW7/MU_HY_man.txt",
            "voice": "zh-CN-XiaoqiuNeural",
            "lang": "zh-CN"
        }
        
    },
    "zh-hk": {
        "qc": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/QC_Texts/qc_static_script_can.txt",
            "voice": "zh-HK-HiuGaaiNeural",
            "lang": "zh-HK"
        },
        "epp": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/EPP_Texts/epp_static_script_can.txt",
            "voice": "zh-HK-HiuGaaiNeural",
            "lang": "zh-HK"
        },
        "MU_Plus": {
            "file": "TTS-Automation\TTS_webapp\TTS_Loans\SOW7\MU_Plus_20250515_approved_CAN.txt",
            "voice": "zh-HK-HiuGaaiNeural",
            "lang": "zh-HK"
        },
        "MU_FS": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/SOW7/MU_FS_can.txt",
            "voice": "zh-HK-HiuGaaiNeural",
            "lang": "zh-HK"
        },
        "MU_HY": {
            "file": "TTS-Automation/TTS_webapp/TTS_Loans/SOW7/MU_HY_can.txt",
            "voice": "zh-HK-HiuGaaiNeural",
            "lang": "zh-HK"
        }
    }
}

# Validate input
if language_choice not in language_config or file_name not in language_config[language_choice]:
    raise ValueError("Invalid language or file_name selection.")

config = language_config[language_choice][file_name]

# 📁 Determine output folder
lang_suffix = {
    "en": "en",
    "zh-cn": "man",
    "zh-hk": "can"
}
output_folder = os.path.join(f"TTS-Automation\TTS_webapp\TTS_Loans\{file_name}\{file_name}_{language_choice}",f"{file_name}_audio_files", f"{file_name}_{lang_suffix[language_choice]}")
os.makedirs(output_folder, exist_ok=True)

# Load and split text
with open(config["file"], "r", encoding="utf-8") as file:
    full_text = file.read()

chunks = textwrap.wrap(full_text, 2000, break_long_words=False, replace_whitespace=False)

# Setup retry-enabled session
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

# Process chunks
for i, chunk in enumerate(chunks):
    escaped_chunk = html.escape(chunk)
    ssml = f"""
    <speak version='1.0' xml:lang='{config["lang"]}'>
    <voice xml:lang='{config["lang"]}' name='{config["voice"]}'>
        {escaped_chunk}
    </voice>
    </speak>
    """

    output_filename = os.path.join(output_folder, f"output_{file_name}_{language_choice}_part_{i+1}.mp3")
    for attempt in range(3):
        try:
            response = session.post(url, headers=headers, data=ssml.encode("utf-8"))
            if response.status_code == 200:
                with open(output_filename, "wb") as f:
                    f.write(response.content)
                print(f"✅ Saved: {output_filename}")
                break
            else:
                print(f"❌ Error {response.status_code} on chunk {i+1}: {response.text}")
        except Exception as e:
            print(f"🔥 Attempt {attempt+1} failed on chunk {i+1}: {e}")

# Combine audio chunks
combined = AudioSegment.empty()
for i in range(len(chunks)):
    filename = os.path.join(output_folder, f"output_{file_name}_{language_choice}_part_{i+1}.mp3")
    if os.path.exists(filename):
        audio = AudioSegment.from_mp3(filename)
        combined += audio
    else:
        print(f"⚠️ Missing file: {filename}")

final_filename = os.path.join(output_folder, f"final_output_{file_name}_{language_choice}.mp3")
combined.export(final_filename, format="mp3")
print(f"🎉 Final audio saved as {final_filename}")
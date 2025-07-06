import os
import platform
import socket
import difflib
import subprocess
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import openai

from modules import (
    network, device, active_directory, cloud,
    printer, qol, security, software, system
)

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
chat_history = []

# Master intent map
INTENT_ROUTER = {
    "network": network.handle_network_command,
    "device": device.handle_device_command,
    "ad": active_directory.handle_ad_command,
    "cloud": cloud.handle_cloud_command,
    "printer": printer.handle_printer_command,
    "qol": qol.handle_qol_command,
    "security": security.handle_security_command,
    "software": software.handle_software_command,
    "system": system.handle_system_command,
}

# Intent keywords mapping to categories
INTENT_KEYWORDS = {
    "flush dns": "network",
    "reset adapter": "network",
    "check internet": "network",
    "wifi": "network",
    "printer": "printer",
    "print": "printer",
    "account locked": "ad",
    "reset password": "ad",
    "create user": "ad",
    "cloud backup": "cloud",
    "cloud storage": "cloud",
    "slow": "qol",
    "clear temp": "qol",
    "security": "security",
    "antivirus": "security",
    "install software": "software",
    "uninstall": "software",
    "disk space": "system",
    "uptime": "system",
    "temp files": "system"
}


def detect_intent(user_input):
    lower_input = user_input.lower()
    for keyword, group in INTENT_KEYWORDS.items():
        if keyword in lower_input:
            return group
    return None


def generate_response(user_input):
    group = detect_intent(user_input)
    if group and group in INTENT_ROUTER:
        handler = INTENT_ROUTER[group]
        return handler(user_input)

    # Fallback to ChatGPT
    try:
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a smart IT help desk assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        return {"type": "chatgpt", "response": completion.choices[0].message.content}

    except Exception as e:
        return {"type": "error", "response": f"❌ Error accessing smart assistant: {str(e)}"}


@app.route("/")
def home():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    chat_history.append({"user": user_message})

    try:
        response = generate_response(user_message)

        # If it's a dict with "type"
        if isinstance(response, dict):
            if response.get("type") == "steps":
                combined = "\n".join(response["steps"]) + f"\n\n{response['summary']}"
                chat_history.append({"bot": combined})
                return jsonify({"response": combined})
            elif response.get("type") == "chatgpt":
                chat_history.append({"bot": response["response"]})
                return jsonify({"response": response["response"]})
            elif response.get("type") == "error":
                chat_history.append({"bot": response["response"]})
                return jsonify({"response": response["response"]})

        # If it's a list (from system, qol, etc.)
        elif isinstance(response, list):
            combined = "\n".join(response)
            chat_history.append({"bot": combined})
            return jsonify({"response": combined})

        else:
            return jsonify({"response": "⚠️ Unexpected response format."})

    except Exception as e:
        error_msg = f"❌ Internal error: {str(e)}"
        chat_history.append({"bot": error_msg})
        return jsonify({"response": error_msg})


if __name__ == "__main__":
    app.run(debug=True)


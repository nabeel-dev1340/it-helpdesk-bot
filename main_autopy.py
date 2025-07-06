import os
import platform
import subprocess
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    return jsonify({"response": "✅ Real automation placeholder active. Full version coming soon."})

if __name__ == "__main__":
    app.run(debug=True)

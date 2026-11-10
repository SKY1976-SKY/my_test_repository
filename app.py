import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI

load_dotenv(r"C:\env\.env")

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages")

    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "메시지를 입력해 주세요."}), 400

    cleaned = []
    for message in messages:
        if not isinstance(message, dict):
            return jsonify({"error": "메시지 형식이 올바르지 않습니다."}), 400
        role = message.get("role")
        content = message.get("content")
        if role not in {"system", "user", "assistant"} or not isinstance(content, str):
            return jsonify({"error": "메시지 형식이 올바르지 않습니다."}), 400
        text = content.strip()
        if text:
            cleaned.append({"role": role, "content": text})

    if not cleaned or cleaned[-1]["role"] != "user":
        return jsonify({"error": "메시지를 입력해 주세요."}), 400

    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({"error": "OPENAI_API_KEY가 설정되어 있지 않습니다."}), 500

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=cleaned,
        )
        reply = response.choices[0].message.content or ""
    except Exception as exc:
        return jsonify({"error": f"응답을 가져오지 못했습니다: {exc}"}), 502

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)

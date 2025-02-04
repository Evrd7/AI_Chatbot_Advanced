import os
import openai
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

from dotenv import load_dotenv
load_dotenv()  # This loads variables from .env into os.environ

app = Flask(__name__)

# 1. Set a secret key for sessions (in production, keep it secret!)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "some_dev_key")


# 2. Configure server-side sessions (to handle multi-user more reliably)
#    We'll store sessions in server memory for now.
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

openai.api_key = os.getenv("OPENAI_API_KEY", "")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if "conversation_history" not in session:
        # Initialize a new conversation for this user session
        session["conversation_history"] = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
    
    conversation_history = session["conversation_history"]

    user_message = request.form.get("user_message", "")
    if not user_message.strip():
        return jsonify({"reply": "Please enter a valid message."})

    # Add user's message
    conversation_history.append({"role": "user", "content": user_message})

    # Call OpenAI
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=100,
        temperature=0.7
    )

    assistant_reply = response.choices[0].message.content.strip()

    # Add assistant's reply
    conversation_history.append({"role": "assistant", "content": assistant_reply})

    # Save updated conversation back to session
    session["conversation_history"] = conversation_history

    return jsonify({"reply": assistant_reply})

if __name__ == "__main__":
    app.run(debug=True)

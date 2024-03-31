import datetime
from flask import Flask, render_template, request
import random

app = Flask(__name__)
pending_messages = []


@app.route("/")
def index():
    return render_template("chat.html")


@app.route('/data', methods=['FETCH'])
def data():
    print(request.json)
    messages = pending_messages.copy()
    pending_messages.clear()

    """
        return [{
            "username": "User" + str(random.randint(1, 100)),
            "text": " ".join([str(random.randint(1, 10**10)) for i in range(random.randint(1, 10))]),
            "time": current_time
        } for _ in range(random.randint(1, 3))]
    """

    return messages


def start_app():
    app.run(debug=True)


def add_message(username, text):
    pending_messages.append({
            "username": username,
            "text": text,
            "time": datetime.datetime.now().strftime("%I:%M %p")
        })


if __name__ == "__main__":
    start_app()

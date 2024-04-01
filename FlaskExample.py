import datetime
from flask import Flask, render_template, request
import random
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
pending_messages = []

log = logging.getLogger('werkzeug')
log.disabled = True


@app.route("/")
def index():
    return render_template("chat.html")


@app.route('/data', methods=['FETCH'])
def data():
    answer = dict()
    answer["data"] = pending_messages[-10:]
    if "from_id" in request.json:
        _index = request.json["from_id"]
        answer["data"] = pending_messages[_index + 1:]
        if request.json["from_id"] >= len(pending_messages):
            answer["reset_index"] = max(len(pending_messages) - 10, -1)
            answer["data"] = pending_messages[answer["reset_index"]:]


    """
        return [{
            "username": "User" + str(random.randint(1, 100)),
            "text": " ".join([str(random.randint(1, 10**10)) for i in range(random.randint(1, 10))]),
            "time": current_time
        } for _ in range(random.randint(1, 3))]
    """

    return answer


def start_app():
    # app.run(debug=True)
    app.run(debug=False)


def add_message(username, text):
    pending_messages.append({
        "username": username,
        "text": text,
        "time": datetime.datetime.now().strftime("%I:%M %p"),
        "id": len(pending_messages)
    })


if __name__ == "__main__":
    start_app()

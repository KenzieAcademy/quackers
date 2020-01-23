import os

import dotenv
import slack
from flask import Flask, request, jsonify

dotenv.load_dotenv()


client = slack.WebClient(token=os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])

app = Flask(__name__)

@app.route('/question/', methods=['POST'])
def question():
    data = request.json

    client.chat_postMessage(
        channel="CSZPGCUAC",
        text="Hello from your app! :tada:",
        icon_emoji=":qbert:"
    )

    return jsonify(data)



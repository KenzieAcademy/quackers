import os

import dotenv
import slack
from flask import Flask, request, jsonify

dotenv.load_dotenv()

client = slack.WebClient(token=os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])

app = Flask(__name__)

modal = {
    "type": "modal",
    "title": {
        "type": "plain_text",
        "text": "QBert!",
        "emoji": True
    },
    "submit": {
        "type": "plain_text",
        "text": "Submit",
        "emoji": True
    },
    "close": {
        "type": "plain_text",
        "text": "Cancel",
        "emoji": True
    },
    "blocks": [
        {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "ml_input",
                "multiline": True
            },
            "label": {
                "type": "plain_text",
                "text": "What else should we know about the problem you're facing?"
            },
            "hint": {
                "type": "plain_text",
                "text": "Any context you can provide will help!"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "*NOTE*: Your question won't get sent to the coaches until you click submit!"
                }
            ]
        }
    ]
}


@app.route('/question/', methods=['POST'])
def question():
    data = request.form.to_dict(flat=False)

    return jsonify(modal)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

import os

import dotenv
import slack
import requests
from flask import Flask, request, jsonify

dotenv.load_dotenv()

client = slack.WebClient(token=os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])

app = Flask(__name__)

modal_start = {
    "type": "modal",
    "callback_id": "qbert-step-1",
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


@app.route('/questionfollowup/', methods=['POST'])
def questionfollowup():
    data = request.form.to_dict()
    breakpoint()


@app.route('/question/', methods=['POST'])
def question():
    data = request.form.to_dict()
    if trigger_id := data.get('trigger_id'):
        resp = {
            "trigger_id": trigger_id,
            "view": modal_start
        }
        requests.post(
            "https://slack.com/api/views.open",
            json=resp,
            headers={
                "Authorization": "Bearer {}".format(os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])
            }
        )
    # final response: return jsonify({"response_action": "clear"})
    # return an empty string per slack docs
    return ('', 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

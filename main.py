import os
import json

from copy import deepcopy

import dotenv
import slack
import requests
from flask import Flask, request, jsonify

dotenv.load_dotenv()

client = slack.WebClient(token=os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])

app = Flask(__name__)

modal_start = {
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
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "The question was: {}",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
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
    data['payload'] = json.loads(data['payload'])

    # slack randomizes the block names. That means the location that the response will
    # be in won't always be the same. We need to pull the ID out of the rest of the
    # response before we go hunting for the data we need.
    # Bonus: every block will have an ID! Just... only one of them will be right.
    block_id = None
    for block in data['payload']['view']['blocks']:
        if block.get('type') == "input":
            block_id = block.get('block_id')


    if not block_id:
        raise Exception("Didn't get valid block ID!")

    message = data['payload']['view']['state']['values'][block_id]['ml_input']['value']
    print("THEY SAID: {}".format(message))
    return ('', 200)

@app.route('/question/', methods=['POST'])
def question():
    data = request.form.to_dict()
    if trigger_id := data.get('trigger_id'):
        new_modal = deepcopy(modal_start)
        new_modal['blocks'][0]['text']['text'] = modal_start['blocks'][0]['text']['text'].format('aaaa')
        resp = {
            "trigger_id": trigger_id,
            "view": new_modal
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

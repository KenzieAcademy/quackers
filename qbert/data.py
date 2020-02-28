start_modal = {
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
                "text": "The question was: {0}\nYour channel: {1}",
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
                    "text": "*NOTE*: Your question won't get sent to the coaches until you click submit!\nID: {}"
                }
            ]
        }
    ]
}

error_modal = {
    "type": "modal",
    "title": {
        "type": "plain_text",
        "text": "Hey! Listen! 🌟",
        "emoji": True
    },
    "close": {
        "type": "plain_text",
        "text": "OK",
        "emoji": True
    },
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "I'm not set up to run in this channel; you'll have to call me from your cohort channel. Sorry!"
            }
        },
        {
            "type": "image",
            "image_url": "https://gamepedia.cursecdn.com/zelda_gamepedia_en/0/08/OoT3D_Navi_Artwork.png?version=61b243ef9637615abdf7534b17361c7a",
            "alt_text": "Navi from The Legend of Zelda - a blue glowing orb with fairy wings. Artwork from the Ocarina of Time 3D."
        }
    ]
}

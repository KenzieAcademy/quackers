import logging

from flask import Flask, request

from quackers.core import process_question, process_question_followup, client
from quackers.helpers import ChannelMap

# *********************************************
# EDIT HERE
# *********************************************

# map is in the following format:
# (channel-to-listen-to, coach-channel, program-this-channel-set-belongs-to)

UX = 'ux'
SE = 'se'

channel_map = ChannelMap(slack_conn=client)

channels = [
    ("joe-slackbot-testing", "joe-slackbot-coaches", SE),
    # software engineering channels
    ("se-july-2020", "se-july-2020-coaches", SE),
    ("se-april-2020", "se-april-2020-coaches", SE),
    ("se-october-2019", "se-q4-staff", SE),
    ("se-january-2020", "se-q3-staff", SE),
    # user experience channels
    ("ux-5", "ux-triage-uie", UX),
    ("ux-6", "ux-triage-uxd", UX),
    ("ux-7", "ux-triage-uxd", UX),
    # old maps
    ("ux-4-indy", "ux-triage-uie", UX),
    ("ux-4-remote", "ux-triage-uie", UX)
]
for channel in channels:
    channel_map.add_channel(
        listen_to=channel[0], post_to=channel[1], airtable=channel[2]
    )

# for responses returned to the student
emoji_list = [
    'party',
    'thepuff',
    'carlton',
    'fire',
    'spinning',
    'party-parrot',
    'heykirbyhey',
    'capemario'
]
# *********************************************
# DO NOT EDIT BEYOND THIS POINT
# *********************************************

app = Flask(__name__)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
else:
    app.logger.setLevel(logging.INFO)


@app.route('/questionfollowup/', methods=['POST'])
def questionfollowup():
    with app.app_context():
        process_question_followup(request.form.to_dict(), channel_map, emoji_list)
    # this endpoint spawns another thread to do its dirty work, so we need to
    # return the 200 OK ASAP so that Slack will be happy.
    return ("", 200)


@app.route('/question/', methods=['POST'])
def question():
    with app.app_context():
        return process_question(request.form.to_dict(), channel_map)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

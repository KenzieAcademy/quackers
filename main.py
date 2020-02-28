import asyncio
import json
import logging
import os
import random
from copy import deepcopy
from datetime import datetime
from pprint import pprint as pp

import dotenv
import slack
from airtable import Airtable
from flask import Flask, request

from qbert.helpers import fire_and_forget
from qbert.data import error_modal, start_modal
from qbert.core import post_message_to_coaches, post_message_to_user

from qbert.core import process_question, process_question_followup

# *********************************************
# EDIT HERE
# *********************************************

# map is in the following format:
# "channel-name-to-listen-on": {
#   "target": "channel-name-to-post-to",
#   "airtable": "se" if it goes to the SE airtable or "ux" if it goes to the UX airtable
# }
# example:
# 'joe-slackbot-testing': 'joe-slackbot-coaches'

channel_map = {
    'joe-slackbot-testing': {
        'target': 'joe-slackbot-coaches', 'airtable': 'se'
    },
    'se-january-2020': {
        'target': 'se-jan-2020-coaches', 'airtable': 'se'
    },
    'se-7': {
        'target': 'staff-se7', 'airtable': 'se'
    },
    'se-6': {
        'target': 'se-q4-staff', 'airtable': 'se'
    },
    'se-october-2019': {
        'target': 'se-october-coaches', 'airtable': 'se'
    },
}

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

logger = logging.getLogger('qbert')
hdlr = logging.FileHandler('qbert.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.WARNING)


@app.route('/questionfollowup/', methods=['POST'])
def questionfollowup():
    process_question_followup(request.form.to_dict(), channel_map, emoji_list)
    # this endpoint spawns another thread to do its dirty work, so we need to
    # return the 200 OK ASAP so that Slack will be happy.
    return ("", 200)


@app.route('/question/', methods=['POST'])
def question():
    return process_question(request.form.to_dict(), channel_map)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

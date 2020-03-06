import json
import logging
import os
import random
from copy import deepcopy
from datetime import datetime

import dotenv
import slack
from airtable import Airtable

from quackers.data import error_modal, start_modal
from quackers.helpers import fire_and_forget

DEBUG = True

if DEBUG:
    dotenv.load_dotenv(".env.testing")
else:
    dotenv.load_dotenv(".env")

client = slack.WebClient(token=os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])

se_students = Airtable(os.environ.get('SE_AIRTABLE_BASE_ID'), 'Students')
se_instructors = Airtable(os.environ.get('SE_AIRTABLE_BASE_ID'), 'Instructors')
se_questions = Airtable(os.environ.get('SE_AIRTABLE_BASE_ID'), 'Quackers Questions')

ux_students = Airtable(os.environ.get('UX_AIRTABLE_BASE_ID'), 'Students')
ux_instructors = Airtable(os.environ.get('UX_AIRTABLE_BASE_ID'), 'Instructors')
ux_questions = Airtable(os.environ.get('UX_AIRTABLE_BASE_ID'), 'Quackers Questions')

logger = logging.getLogger('quackers.core')


def post_message_to_coaches(user, channel, question, info, client, channel_map):
    ch = channel_map.get_coach_channel(channel)
    message = (
        f"Received request for help from @{user} with the following info:\n\n"
        f"Question: {question}\n"
        f"Additional info: {info}"
    )

    client.chat_postMessage(
        channel=ch,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            }
        ],
        icon_emoji=":quackers:"
    )


def post_to_airtable(user_id, slack_username, channel, channel_map, question, info):
    # We want to log both student interactions and instructor interactions.
    # We'll check the student table first (because it's most likely that a
    # student is the one using the system), then check for an instructor.
    # The mapping in main.py is used to select which set of airtable instances
    # we check, mostly just to save time.
    #
    # ...and if we don't get a positive response from AirTable? Send it to
    # Unresolved User.

    # make pycharm happy
    person_id = None
    option = None

    base = channel_map.get_base(channel).lower()  # .lower() == safety check

    if base == "se":
        airtable_target = se_questions
        search_options = [
            {'table': se_students, 'is_student': True},
            {'table': se_instructors, 'is_student': False},
        ]
    elif base == "ux":
        airtable_target = ux_questions
        search_options = [
            {'table': ux_students, 'is_student': True},
            {'table': ux_instructors, 'is_student': False},
        ]
    else:
        raise Exception(f"No search options found for Airtable base {base}")

    for option in search_options:
        if person := option['table'].search('Slack ID', user_id):
            person_id = person[0]['id']
            break

    if not person_id:
        # we didn't find anyone with the right Slack ID in Airtable, so we'll force
        # the next set of checks to return None for each of the questions.
        option = {}

    student_id, instructor_id, unresolved_user_id = (
        person_id if option.get("is_student") else None,
        person_id if not option.get("is_student") else None,
        slack_username if not person_id else ""
    )

    data = {
        'Question': question,
        'Additional Info': info,
        'Channel': channel,
        'Student': [student_id] if student_id else None,
        'Instructor': [instructor_id] if instructor_id else None,
        'Unresolved User': unresolved_user_id if unresolved_user_id else None,
        'Date': datetime.now().isoformat()
    }

    airtable_target.insert(data)


def post_message_to_user(user_id, channel, channel_map, question, emoji_list, client):
    channel = channel_map.get_channel_id(channel)
    client.chat_postEphemeral(
        user=user_id,
        channel=channel,
        text=(
            "Thanks for reaching out! One of the coaches or facilitators will be"
            " with you shortly! :{}: Your question was: {}".format(
                random.choice(emoji_list), question
            )
        )
    )


@fire_and_forget
def process_question_followup(data, channel_map, emoji_list):
    # the payload is a dict... as a string.
    data['payload'] = json.loads(data['payload'])

    # slack randomizes the block names. That means the location that the response will
    # be in won't always be the same. We need to pull the ID out of the rest of the
    # response before we go hunting for the data we need.
    # Bonus: every block will have an ID! Just... only one of them will be right.
    channel = None
    original_q = None
    addnl_info_block_id = None
    user_id = None

    for block in data['payload']['view']['blocks']:
        if block.get('type') == "input":
            addnl_info_block_id = block.get('block_id')
        if block.get('type') == "section":
            previous_data = block['text']['text'].split("\n")
            original_q = previous_data[0][previous_data[0].index(":") + 2:]
            channel = previous_data[1][previous_data[1].index(":") + 2:]
        if block.get('type') == "context":
            user_id = block['elements'][0]['text'].split(':')[2].strip()

    dv = data['payload']['view']

    additional_info = dv['state']['values'][addnl_info_block_id]['ml_input']['value']
    username = data['payload']['user']['username']

    post_message_to_coaches(
        user=username,
        channel=channel,
        question=original_q,
        info=additional_info,
        client=client,
        channel_map=channel_map
    )
    post_to_airtable(
        user_id, username, channel, channel_map, original_q, additional_info
    )
    post_message_to_user(
        user_id=user_id,
        channel=channel,
        channel_map=channel_map,
        question=original_q,
        emoji_list=emoji_list,
        client=client
    )


def process_question(data, channel_map):
    if trigger_id := data.get('trigger_id'):
        # first we need to verify that we're being called in the right place
        if data.get('channel_name') not in channel_map.keys():
            client.views_open(
                trigger_id=trigger_id,
                view=error_modal
            )
            return ("", 200)

        # copy the modal so that we don't accidentally modify the version in memory.
        # the garbage collector will take care of the copies later.
        start_modal_copy = deepcopy(start_modal)
        # stick the original question they asked and the channel they asked from
        # into the modal so we can retrieve it in the next section
        start_modal_copy['blocks'][0]['text']['text'] = \
            start_modal['blocks'][0]['text']['text'].format(
                data.get('text'), data.get('channel_name')
            )

        start_modal_copy['blocks'][4]['elements'][0]['text'] = \
            start_modal['blocks'][4]['elements'][0]['text'].format(data.get('user_id'))

        client.views_open(
            trigger_id=trigger_id,
            view=start_modal_copy
        )
    # return an empty string as fast as possible per slack docs
    return ("", 200)

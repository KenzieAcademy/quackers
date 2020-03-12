import threading
import flask

APP = flask.current_app

# https://stackoverflow.com/a/59043636
def fire_and_forget(f, *args, **kwargs):
    def wrapped(*args, **kwargs):
        threading.Thread(target=f, args=(args), kwargs=kwargs).start()

    return wrapped


class ChannelMap(object):

    def __init__(self, slack_conn):
        self.client = slack_conn
        self.mapping = {}

    def add_channel(self, listen_to: str=None, post_to: str=None, airtable: str=None):
        if not listen_to or not post_to or not airtable:
            raise ValueError("Must pass in all three variables!")
        self.mapping.update({listen_to: {'target': post_to, 'airtable': airtable}})
        APP.logger.info(f"Registered {listen_to} -> {post_to} for the {airtable.upper()} program")

    def get_coach_channel(self, c):
        result = self.mapping[c]
        if not result:
            raise Exception("No matching channel found!")
        if not result['target'].startswith("#"):
            result = "#{}".format(result['target'])

        return result

    def get_channel_id(self, channel_name):
        # reference: https://github.com/KenzieAcademy/quackers/issues/8
        # https://github.com/KenzieAcademy/quackers/issues/7
        channels = self.client.users_conversations(
            types="public_channel,private_channel"
        ).data['channels']
        for c in channels:
            if c.get('name') == channel_name:
                return c['id']
        APP.logger.error("Could not find matching channel!")

    def get_base(self, channel):
        result = self.mapping[channel]
        if not result:
            raise Exception("No matching channel found!")
        return result['airtable']

    def get(self, item):
        return self.mapping.get(item)

    def keys(self):
        return self.mapping.keys()

    def items(self):
        return self.mapping.items()

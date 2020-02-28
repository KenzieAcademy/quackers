import threading


# https://stackoverflow.com/a/59043636
def fire_and_forget(f, *args, **kwargs):
    def wrapped(*args, **kwargs):
        threading.Thread(target=f, args=(args), kwargs=kwargs).start()

    return wrapped


def get_coach_channel(c, channel_map):
    result = channel_map[c]
    if not result:
        raise Exception("No matching channel found!")
    if not result['target'].startswith("#"):
        result = "#{}".format(result['target'])

    return result


def get_base(channel, channel_map):
    result = channel_map[channel]
    if not result:
        raise Exception("No matching channel found!")
    return result['airtable']


def get_channel_id(channel_name, client):
    channels = client.users_conversations().data['channels']
    for c in channels:
        if c.get('name') == channel_name:
            return c['id']


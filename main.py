import os

import slack
import dotenv

dotenv.load_dotenv()

# client = slack.WebClient(token=os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])
#
# client.chat_postMessage(
#     channel="CSZPGCUAC",
#     text="Hello from your app! :tada:",
#     icon_emoji=":qbert:"
# )

@slack.RTMClient.run_on(event='message')
def say_hello(**payload):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    if 'Hello' in data.get('text', []):
        channel_id = data['channel']
        thread_ts = data['ts']
        user = data['user']

        web_client.chat_postMessage(
            channel=channel_id,
            text=f"Hi <@{user}>!",
            thread_ts=thread_ts
        )

slack_token = os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"]
rtm_client = slack.RTMClient(token=slack_token)
rtm_client.start()

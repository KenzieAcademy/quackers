import os

import cherrypy
import dotenv
import slack

dotenv.load_dotenv()


client = slack.WebClient(token=os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])


class Root(object):
    @cherrypy.expose
    def question(self):
        client.chat_postMessage(
            channel="CSZPGCUAC",
            text="Hello from your app! :tada:",
            icon_emoji=":qbert:"
        )
        return "thhhhtbbbbbt"


cherrypy.config.update({'server.socket_port': 8090,
                        'engine.autoreload.on': False,
                        'log.access_file': './access.log',
                        'log.error_file': './error.log'})
cherrypy.quickstart(Root())


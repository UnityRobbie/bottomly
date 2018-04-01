import logging
import os
from abc import ABC, abstractmethod

from slacker import Slacker
from slacksocket import SlackSocket
from config import Config, ConfigKeys

help_token = "-?"

class AbstractEventHandler(ABC):

    @property
    @abstractmethod
    def command(self):
        pass

    @abstractmethod
    def can_handle(self, slack_event):
        pass

    @abstractmethod
    def _invoke_handler_logic(self, slack_event):
        pass

    @abstractmethod
    def _get_command_symbol(self):
        pass

    @abstractmethod
    def get_usage(self):
        pass

    @property
    def _help_message(self):
        return self.command_trigger + help_token

    def handle(self, slack_event):
        if slack_event["text"] == self._help_message:
            purpose = self.command.get_purpose() + os.linesep
            usage = "Usage: `" + self.get_usage() + "`"
            message = purpose + usage
            if self.debug:
                message = "[DEBUG] " + message
            self._send_message_response(message, slack_event)
        else:
            self._invoke_handler_logic(slack_event)


    def _send_message_response(self, response_message, slack_event):
        try :
            with SlackSocket(self.token) as s:
                msg = s.send_msg(response_message, slack_event["channel"])
                logging.info(msg.sent)
        except Exception:
            logging.exception("Error sending message response to: " + str(slack_event))

    def _send_reaction_response(self, slack_event):
        try :
            slack = Slacker(self.token)
            slack.reactions.add(name="robot_face",
                                channel=slack_event["channel_id"],
                                timestamp=slack_event["ts"])
        except Exception:
            logging.exception("Error sending reaction to: " + str(slack_event))

    def _send_dm_response(self, response_message, slack_event):
        try:
            slack = Slacker(self.token)
            im = slack.im.open(slack_event["user_id"]).body
            if im["ok"]:
                channel_id = im["channel"]["id"]
                slack.chat.post_message(channel_id, text=response_message)

            else:
                raise Exception("Failed to open a DM to send response.")

        except Exception:
            logging.exception("Error sending DM response to: " + str(slack_event))

    def _get_config(self):
        config = Config()
        self.token = config.get_config_value(ConfigKeys.slack_bot_token)
        self.command_trigger = config.get_prefix() + self._get_command_symbol() + " "

    def __init__(self, debug=False):
        self.debug = debug
        self._get_config()
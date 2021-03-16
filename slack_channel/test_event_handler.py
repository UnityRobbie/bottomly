# coding=utf-8
from commands import VoidCommand
from slack_channel.abstract_event_handler import AbstractEventHandler


command_symbol = "test"


class TestEventHandler(AbstractEventHandler):
    @property
    def command(self) -> VoidCommand:
        return VoidCommand()

    @property
    def name(self):
        return "Test"

    def get_usage(self):
        return self.command_trigger

    def can_handle(self, slack_event):
        text = slack_event["text"]
        return text.startswith(self.command_trigger[:-1])

    def _invoke_handler_logic(self, slack_event):
        self.command.execute()
        self._send_message_response("OK", slack_event)

    def _get_command_symbol(self):
        return command_symbol

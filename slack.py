import logging
import os

import slack_sdk

TOKEN = os.environ.get('SLACK_TOKEN', '')
CHANNEL = '#news'

# https://medium.com/@life-is-short-so-enjoy-it/slack-post-message-with-slack-app-without-incoming-webhooks-52b52456b6b4
class SlackBot(object):

    def __init__(self, token: str, channel: str, logger: logging.Logger=None) -> None:
        self.token: str = token
        self.channel: str = channel
        self.logger: logging.Logger = logger

        # TODO: Error check and log.
        self.client = slack_sdk.WebClient(token=self.token)


    def log(self, message: str, level: str) -> None:
        if self.logger is None:
            return
        # TODO: Check level
        self.logger.info(message)


    def post_message(self, message: str) -> None:
        self.log(f'Posting message: {message}', 'info')
        try:
            result = self.client.chat_postMessage(
                    channel=self.channel,
                    text=message)
            self.log(result, 'info')
        except slack_sdk.errors.SlackApiError as err:
            self.log(f'Error posting message: {err}', 'error')

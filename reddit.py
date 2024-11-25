import logging
import os
import typing

import praw

CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET', '')
USER_AGENT = 'redditbot by u/cucyber'

class RedditBot(object):

    def __init__(self, client_id: str, client_secret: str, user_agent: str,
            logger: logging.Logger=None) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.logger = logger

        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent
        )

    def log(self, message: str, level: str) -> None:
        if self.logger is None:
            return
        # TODO: Check level
        self.logger.info(message)

    def fetch_posts(self, subreddit: str, num_posts: int) -> list:
        posts: typing.List[str] = []
        self.log(f'Fetching posts from {subreddit}', 'info')
        for submission in self.reddit.subreddit(subreddit).new(limit=num_posts):
            self.log(f'Fetched post: {submission.title}', 'debug')
            posts.append(submission)
        return posts

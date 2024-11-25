import datetime
import logging
import sched
import sys
import time
import typing

import slack
import reddit

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
LOGGER.addHandler(handler)

POLL_INTERVAL = 60 # Seconds
MAX_POSTS = 10
SUBSCRIBED_SUBREDDITS_PATH = 'conf/subscribed_subreddits'
LAST_POLL_PATH = 'conf/last_poll_time'

class Submission(object):

    def __init__(self, title: str, time_created: float, url: str, subreddit: str):
        self.title = title
        self.time_created = time_created
        self.url = url
        self.subreddit = subreddit


class Bot(object):

    def __init__(self, last_poll_time_path: str, subreddits_path: str) -> None:

        self._last_poll_time_path = last_poll_time_path
        self._subreddits_path = subreddits_path

        self.slackbot = slack.SlackBot(slack.TOKEN, slack.CHANNEL, LOGGER)
        self.redditbot = reddit.RedditBot(
            reddit.CLIENT_ID,
            reddit.CLIENT_SECRET,
            reddit.USER_AGENT,
            LOGGER)

    @property
    def last_poll_time(self) -> float:
        # TODO: If file does not exist, create it and populate it with -1.
        with open(self._last_poll_time_path, 'r', encoding='utf-8') as poll_fd:
            last_poll_time_ = float(poll_fd.read().strip())
        return last_poll_time_

    @last_poll_time.setter
    def last_poll_time(self, poll_time: float) -> None:
        with open(self._last_poll_time_path, 'w', encoding='utf-8') as poll_fd:
            poll_fd.write(str(poll_time))


    @property
    def subscribed_subreddits(self) -> typing.List[str]:
        subscribed_subreddits_ = []
        # TODO: If file does not exist, create it.
        with open(self._subreddits_path, 'r', encoding='utf-8') as poll_fd:
            for line in poll_fd:
                subscribed_subreddits_.append(line.strip())
        return subscribed_subreddits_


    @property
    def subscribed_subreddits_formatted(self) -> str:
        return '+'.join(self.subscribed_subreddits)


    def fetch_new_reddit_submissions(self) -> typing.List[Submission]:
        posts = self.redditbot.fetch_posts(self.subscribed_subreddits_formatted, MAX_POSTS)
        time_since = self.last_poll_time
        print(f'time_since: {time_since}')
        self.last_poll_time = time.time()
        print(f'posts[0] created: {posts[0].created}')
        return [
            Submission(post.title, post.created, post.permalink, post.subreddit)
            for post in posts if post.created > time_since
        ]


    def post_submission_to_slack(self, submission: Submission, debug: bool=True) -> None:
        time_format = '%H:%M:%S %m/%d/%Y'
        message_time = datetime.datetime.fromtimestamp(
            submission.time_created
            ).strftime(time_format)
        message = (
            f"\"{submission.title}\"\n"
            f"Posted in r/{submission.subreddit} at {message_time}\n"
            f"www.reddit.com{submission.url}")
        if not debug:
            self.slackbot.post_message(message)
        else:
            LOGGER.info(message)


def callback_handler(s: sched.scheduler, bot: Bot) -> None:

    # Reset the timer.
    s.enter(POLL_INTERVAL, 1, callback_handler, (s, bot, ))
    print("handler called")

    # For each subscribed subreddit, check if new posts exist since time of
    # last poll.
    new_submissions = bot.fetch_new_reddit_submissions()
    if not new_submissions:
        LOGGER.info('No recent submissions')

    # For each new post found, post in slack.
    for submission in new_submissions:
        bot.post_submission_to_slack(submission, debug=False)


def main() -> None:

    bot = Bot(LAST_POLL_PATH, SUBSCRIBED_SUBREDDITS_PATH)
    s = sched.scheduler(time.time, time.sleep)
    s.enter(POLL_INTERVAL, 1, callback_handler, (s, bot, ))
    s.run()


if __name__ == '__main__':
    main()

"""
Messaging module is for sending notifications over firebase messaging service
it supports per user notification using the notification token and
per topic notification using the topic name.
requires the firebase credentials to be initialized first.

you can set a global title, for the notifications sent to your apps, that would be used as a default if you don't
provide a title entry in the message argument. not providing any of them would throw an Exception.

pro-tip: if you are looking for a way to notify all the users of your app at once, since firebase doesn't offer this option
directly, you can work around that by creating a topic named 'all' or whatever you like, subscribe your users to that
topic on app launch and then notify them using that! that would work so much better than iterating over all
the available tokens and sending them one by one.

ENJOY!
"""

from . import SETTINGS
from firebase_admin import messaging
import logging

from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def notify_user(notifications_token: str, message: dict):
    """
    Notifies a user using his notifications token (provided from the apps)
    :param notifications_token: the user's notification token
    :param message: the message should be a dict normal use case consists of two keys (title,message)
    :return: None
    """
    if notifications_token == '' or notifications_token is None:
        raise ValueError('notifications_token must not be empty, you should provide the user\'s notification token')

    if len(message.keys()) < 2:
        raise ValueError('you must provide a message in the notification')

    if type(message) is not dict:
        raise TypeError('The message must be a dictionary containing a title and message')

    if message['title'] is None and SETTINGS.get("APP_NAME", None) is not None:
        message['title'] = SETTINGS.get("APP_NAME")
    else:
        raise ImproperlyConfigured("You should provide either a title entry in the message dict, or provide an APP_NAME"
                                   "property in the settings module.")

    msg = messaging.Message(data=message, token=notifications_token)
    response = messaging.send(msg)
    logger.info(response)


def notify_topic(message: dict, topic: str):
    _notify_topic(message, topic)


def _notify_topic(message: dict, topic):
    """
    sends notifications per topic
    :param message: the message should be a dict normal use case consists of two keys (title,message)
    :param topic: a topic name, topics are to be initialized from the receiving apps (users subscribe to topics)
    :return: None
    """
    msg = messaging.Message(data=message, topic=topic)
    response = messaging.send(msg)
    logger.info(response)

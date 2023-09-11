from distutils.util import strtobool
from os import getenv, path
from typing import Dict
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import os
import sys
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
import ssl

from logger import Logger


class Config:
    APP_ENV = getenv('APP_ENV', 'local')

    LOG_LEVEL = getenv('LOG_LEVEL', 'DEBUG')
    logger = Logger()

    REQUEST_TIMEOUT = float(getenv('REQUEST_TIMEOUT', 10))

    URL_GET_ORDERS = getenv('URL_GET_ORDERS', 'http://localhost:8081')

    """
        Configuration environment variables for Broker message
    """
    BROKER_SERVER = getenv('BROKER_SERVER', 'pkc-n3603.us-central1.gcp.confluent.cloud:9092')
    BROKER_USERNAME = getenv('BROKER_USERNAME', '6BQ56X3IK2PZJ5OA')
    BROKER_PASSWORD = getenv('BROKER_PASSWORD', 'ClDejaccUcknj3z/f/mzy+H2nX5vrO1A493rD9Kq1i3bhmBqxCtIv0cBE9EvOHbo')
    
    TOPIC_CHECK_ORDER = getenv('TOPIC_CHECK_ORDER', 'check_order_local')

    MAX_RETRY = int(getenv('MAX_RETRY', 3))

    BROKER_SESSION_TIMEOUT = int(getenv('BROKER_SESSION_TIMEOUT', 120000))  # in milliseconds
    BROKER_REQUEST_TIMEOUT = int(getenv('BROKER_REQUEST_TIMEOUT', 120000))  # in milliseconds

    QUEUE_ORDERS_PAGINATION_LIMIT = int(getenv('QUEUE_ORDERS_PAGINATION_LIMIT', 10))

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_context.load_default_certs()

    INTERVAL= int(getenv('INTERVAL', 1))
 
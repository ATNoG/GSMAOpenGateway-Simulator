# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 11:34:16
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-11 20:17:45

import pika
from . import constants as Constants


def get_new_pika_connection_and_channel():
    consumer_connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=Constants.PIKA_CONNECTION_HOST,
            port=Constants.PIKA_CONNECTION_PORT
        )
    )
    return consumer_connection, consumer_connection.channel()

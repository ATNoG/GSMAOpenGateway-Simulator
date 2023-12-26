# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 11:21:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-26 12:30:36

from . import aux as Aux
from .topics import Topics
from . import connections_factory as Factory
import logging
import sys

# When this module is imported, the first thing to do is to create all
# queues/topics


# Todo: Deal with this later
# If under test, do not execute
if "pytest" not in sys.modules:

    # Create connection and channel
    consumer_connection, consumer_channel = Factory\
        .get_new_pika_connection_and_channel()

    # Create all topics/queues
    for topic in Topics:
        logging.info("Will bootstrap all meaningfull messsage topics...")
        Aux.create_queue_if_doesnt_exist(
            consumer_channel,
            topic.value
        )

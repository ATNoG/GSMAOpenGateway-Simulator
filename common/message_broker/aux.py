# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 11:23:49
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-11 20:16:15

import pika
import logging


def does_queue_exist(channel, queue_name):
    try:
        # Declare the queue (does not create it if it already exists)
        channel.queue_declare(queue=queue_name)
        # If the queue declaration is successful, it means the queue exists
        return True
    except pika.exceptions.ChannelClosedByBroker as e:
        # If the queue does not exist, a ChannelClosedByBroker exception is
        # raised
        if e.reply_code == 404:
            return False
        else:
            # Handle other exceptions if needed
            print(e)
            exit(0)
            raise


def create_queue_if_doesnt_exist(channel, queue_name):
    if does_queue_exist(channel, queue_name):
        logging.info(f"The queue '{queue_name}' already exists.")
    else:
        logging.info(
            f"The queue '{queue_name}' does not exist and will be created."
        )
        channel.queue_declare(queue=queue_name)
        logging.info(f"The queue '{queue_name}' was created.")

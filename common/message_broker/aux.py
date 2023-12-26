# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 11:23:49
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-26 12:57:15

import pika
import logging
from common.message_broker.topics import Topics


def create_queue_if_doesnt_exist(channel, queue_name):
    try:
        logging.info(
            f"The queue '{queue_name}' will be created."
        )
        if queue_name == Topics.SIMULATION.value:
            # This exhcange is a fanout exchange. It is used to stop the
            # simulations because it sends a stop message to ALL simulation
            # consumers
            channel.exchange_declare(
                exchange=Topics.SIMULATION.value,
                exchange_type='fanout'
            )
            logging.info(
                f"The exchange '{queue_name}' was created with the " +
                "exchange type 'fanout'."
            )
            # This queue is a 1-to-1 queue. It will be used to send the
            # simulation start messages
            channel.queue_declare(queue=queue_name)
            logging.info(f"The queue '{queue_name}' was created.")
        else:
            channel.queue_declare(queue=queue_name)
            logging.info(f"The queue '{queue_name}' was created.")

    except pika.exceptions.ChannelClosedByBroker as e:
        logging.error(
            f"Couldn't create the queue '{queue_name}'. Reason: {e}"
        )
        exit(1)
